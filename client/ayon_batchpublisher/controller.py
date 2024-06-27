import collections
import glob
import os
import re
from tempfile import NamedTemporaryFile

import ayon_api
from ayon_api import (
    get_projects,
    get_folders,
    get_tasks_by_folder_paths
)
from ayon_core.settings import get_project_settings

from ayon_batchpublisher.publish import publish_version_pyblish


class ProductItem(object):
    def __init__(
            self,
            filepath,
            product_type,
            representation_name,
            product_name=None,
            version=None,
            comment=None,
            enabled=True,
            folder_path=None,
            task_name=None,
            frame_start=None,
            frame_end=None):
        self.enabled = enabled
        self.filepath = filepath
        self.product_type = product_type
        self.product_name = product_name
        self.representation_name = representation_name
        self.version = version
        self.folder_path = folder_path
        self.comment = comment
        self.task_name = task_name
        self.frame_start = frame_start
        self.frame_end = frame_end

        self.derive_product_name()

    def derive_product_name(self):
        filename = os.path.basename(self.filepath)
        filename_no_ext, extension = os.path.splitext(filename)
        # Exclude possible frame in product name
        product_name = filename_no_ext.split(".")[0]
        # Add the product type as prefix to product name
        if product_name.startswith("_"):
            product_name = self.product_type + product_name
        else:
            product_name = self.product_type + "_" + product_name
        # Try to extract version number from filename
        self.version = None
        results = re.findall("_v[0-9]*", self.filepath)
        if results:
            try:
                self.version = int(results[0].replace("_v", ""))
            except ValueError:
                print(results[0])
        # Remove version from product name
        self.product_name = re.sub("_v[0-9]*", "", product_name)
        return self.product_name

    @property
    def defined(self):
        return all([
            self.filepath,
            self.folder_path,
            self.task_name,
            self.product_type,
            self.product_name,
            self.representation_name])


class HierarchyItem:
    def __init__(self, folder_name, folder_path, folder_id, parent_id):
        self.folder_name = folder_name
        self.folder_path = folder_path
        self.folder_id = folder_id
        self.parent_id = parent_id


class BatchPublisherController(object):

    def __init__(self):
        self._selected_project_name = None
        self._project_names = None
        self._asset_docs_by_project = {}
        self._asset_docs_by_path = {}

    def get_project_names(self):
        if self._project_names is None:
            projects = get_projects(fields={"name"})
            project_names = []
            for project in projects:
                project_names.append(project["name"])
            self._project_names = project_names
        return self._project_names

    def get_selected_project_name(self):
        return self._selected_project_name

    def set_selected_project_name(self, project_name):
        self._selected_project_name = project_name

    def _get_asset_docs(self):
        """
        Returns:
            dict[str, dict]: Dictionary of asset documents by path.
        """

        project_name = self._selected_project_name
        if not project_name:
            return {}

        asset_docs = ayon_api.get_folders(project_name)
        asset_docs_by_path = self._prepare_assets_by_path(asset_docs)
        self._asset_docs_by_project[project_name] = asset_docs_by_path
        return self._asset_docs_by_project[project_name]

    def get_hierarchy_items(self):
        """
        Returns:
            list[HierarchyItem]: List of hierarchy items.
        """

        asset_docs = get_folders(project_name=self._selected_project_name)
        if not asset_docs:
            return []

        output = []
        for folder_path, asset_doc in asset_docs.items():
            folder_name = asset_doc["name"]
            folder_id = asset_doc["_id"]
            parent_id = asset_doc["data"]["visualParent"]
            hierarchy_item = HierarchyItem(
                folder_name, folder_path, folder_id, parent_id)
            output.append(hierarchy_item)
        return output

    def get_task_names(self, folder_path):
        if not folder_path:
            return []
        tasks = get_tasks_by_folder_paths(
            self._selected_project_name, folder_paths=[folder_path])
        return [task["name"] for task in tasks[folder_path]]

    def _prepare_assets_by_path(self, asset_docs):
        output = {}
        for asset_doc in asset_docs:
            output[asset_doc["path"]] = asset_doc
        return output

    def get_product_items(self, directory):
        """
        Returns:
            list[ProductItem]: List of ingest files for the given directory
        """
        product_items = collections.OrderedDict()
        if not directory or not os.path.exists(directory):
            return product_items

        project_name = self._selected_project_name
        project_settings = get_project_settings(project_name)
        batchpublisher_sett = project_settings["batchpublisher"]

        file_mappings = batchpublisher_sett["pattern_to_product_type"]
        product_items = self._get_items_from_regex_mapping(
            directory, product_items, file_mappings)

        extensions_to_product_mapping = (
            batchpublisher_sett["extensions_to_product_type"])
        product_items = self._get_items_from_extension_mapping(
            directory, product_items, extensions_to_product_mapping)

        return list(product_items.values())

    def _get_items_from_regex_mapping(self, directory, product_items,
                                      file_mappings):
        """Traverses `directory`, uses regular expressions to guess product"""
        for file_mapping in file_mappings:
            product_type = file_mapping["product_type"]
            glob_full_path = directory + "/" + file_mapping["pattern"]
            files = glob.glob(glob_full_path, recursive=False)
            for filepath in files:
                filename = os.path.basename(filepath)
                filepath, frame_end, frame_start = self._get_frame_info(
                    filepath)
                # Do not add ingest file path, if it's already been added
                if filepath in product_items:
                    continue
                _filename_no_ext, extension = os.path.splitext(filename)
                # Create representation name from extension
                representation_name = extension.lstrip(".")
                product_item = ProductItem(
                    filepath,
                    product_type,
                    representation_name,
                    frame_start=frame_start,
                    frame_end=frame_end)
                product_items[filepath] = product_item

        return product_items

    def _get_items_from_extension_mapping(
            self, directory, product_items, extensions_to_product_mapping):
        # Walk the entire directory structure again
        # and look for product items to add.
        # This time we are looking for product types
        # by PRODUCT_TYPE_TO_EXT_MAP
        for root, _dirs, filenames in os.walk(directory, topdown=False):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                filename = os.path.basename(filepath)
                filepath, frame_end, frame_start = self._get_frame_info(
                    filepath)
                # Do not add ingest file path, if it's already been added
                if filepath in product_items:
                    continue
                _filename_no_ext, extension = os.path.splitext(filename)
                product_type = None
                for setting_item in extensions_to_product_mapping:
                    _product_type = setting_item["name"]
                    extensions = setting_item["extensions"]
                    if extension in extensions:
                        product_type = _product_type
                        break
                if not product_type:
                    continue
                # Create representation name from extension
                representation_name = extension.lstrip(".")
                product_item = ProductItem(
                    filepath,
                    product_type,
                    representation_name,
                    frame_start=frame_start,
                    frame_end=frame_end)
                product_items[filepath] = product_item

        return product_items

    def publish_product_items(self, product_items):
        """
        Args:
            product_items (list[ProductItem]): List of ingest files to publish.
        """
        msg = ""
        for product_item in product_items:
            if product_item.enabled and product_item.defined:
                publish_return = self._publish_product_item(product_item)

                msg += f"Publish of \n '{product_item.filepath}' \n"
                error_message = publish_return.error_message
                if error_message:
                    msg += f" failed with: \n {error_message} \n\n"
                    with NamedTemporaryFile(delete=False) as temp_file:
                        # Write data to the file
                        for line in publish_return.logs:
                            temp_file.write(str(line + "\n").encode("utf-8"))

                        # Get the temporary file path (optional)
                        temp_file_path = temp_file.name
                        msg += f"Log could be found '{temp_file_path}'.\n\n"
                else:
                    msg += "finished successfully.\n\n"

        return msg

    def _publish_product_item(self, product_item):
        msg = f"""
Publishing (ingesting): {product_item.filepath}
As Folder: {product_item.folder_path}
Task: {product_item.task_name}
Product Type: {product_item.product_type}
Product Name: {product_item.product_name}
Representation: {product_item.representation_name}
Version: {product_item.version}
Comment: {product_item.comment}
Frame start: {product_item.frame_start}
Frame end: {product_item.frame_end}
Project: {self._selected_project_name}
"""
        print(msg)
        publish_data = {
            "version": product_item.version,
            "comment": product_item.comment,
        }
        expected_representations = dict()
        expected_representations[product_item.representation_name] = \
            product_item.filepath
        return publish_version_pyblish(
            self._selected_project_name,
            product_item.folder_path,
            product_item.task_name,
            product_item.product_type,
            product_item.product_name,
            expected_representations,
            publish_data,
            frame_start=product_item.frame_start,
            frame_end=product_item.frame_end)

    def _get_frame_info(self, filepath):
        # Get frame infomration (if any)
        frame_start = None
        frame_end = None
        filename = os.path.basename(filepath)
        if filename.count(".") >= 2:
            # Lets add the star in place of the frame number
            filepath_parts = filepath.split(".")
            filepath_parts[-2] = "*"
            # Replace the file path with the version with star in it
            _filepath = ".".join(filepath_parts)
            frames = self._get_frames_for_filepath(_filepath)
            if frames:
                filepath = _filepath
                frame_start = frames[0]
                frame_end = frames[-1]
        return filepath, frame_end, frame_start

    def _get_frames_for_filepath(self, filepath):
        # Collect all the frames found within the paths of glob search string
        frames = list()
        for _filepath in glob.glob(filepath):
            filepath_parts = _filepath.split(".")
            try:
                frame = int(filepath_parts[-2])
            except Exception:
                continue
            frames.append(frame)
        return sorted(frames)
