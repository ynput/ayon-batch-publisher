import os
import getpass
import glob
import json

import pyblish.api

from ayon_core.lib import Logger
from ayon_core.pipeline import install_host
from ayon_core.pipeline.create import CreateContext
from ayon_traypublisher.api import TrayPublisherHost

logger = Logger.get_logger(__name__)


REVIEW_FAMILIES = {
    "render"
}

PUBLISH_TO_SG_FAMILIES = {
    "render"
}


class PublishReturnItem(object):
    def __init__(self, logs, error_message):
        self.logs = logs
        self.error_message = error_message


def publish_version_pyblish(
        project_name,
        folder_path,
        task_name,
        product_type,
        product_name,
        expected_representations,
        publish_data,
        frame_start=None,
        frame_end=None):

    os.environ["AYON_PROJECT_NAME"] = project_name

    representation_name = list(expected_representations.keys())[0]
    file_path = list(expected_representations.values())[0]

    host = TrayPublisherHost()
    install_host(host)

    create_context = CreateContext(host)
    pyblish_context = pyblish.api.Context()
    pyblish_context.data["create_context"] = create_context
    pyblish_plugins = create_context.publish_plugins

    instance = pyblish_context.create_instance(
        name=product_name,
        family=product_type)
    instance.data.update(
        {
            "productType": product_type,
            "folderPath": folder_path,
            "task": task_name,
            "productName": product_name,
            "publish": True,
            "active": True,
            "version": publish_data.get("version"),
            "comment": publish_data.get("comment"),
            "frameStart": frame_start,
            "frameEnd": frame_end,
            "handleStart": frame_start,
            "handleEnd": frame_end,
        })

    directory = os.path.dirname(file_path)
    # If file path has star in it lets collect all the file names
    if "*" in file_path:
        _filepaths = glob.glob(file_path)
        file_names = list()
        for _filepath in _filepaths:
            file_name = os.path.basename(_filepath)
            file_names.append(file_name)
        extension = os.path.splitext(file_names[0])[1].lstrip(".")
    else:
        file_name = os.path.basename(file_path)
        extension = os.path.splitext(file_name)[1].lstrip(".")
        file_names = file_name

    representation = {
        "name": representation_name,
        "ext": extension,
        "preview": True,
        "tags": [],
        "files": file_names,
        "stagingDir": directory,
    }
    instance.data.setdefault("representations", [])
    instance.data["representations"].append(representation)

    error_format = ("Failed {plugin.__name__}:\n {error}\n{error.traceback}")

    logs = []
    error_message = None
    for result in pyblish.util.publish_iter(
            context=pyblish_context, plugins=pyblish_plugins):
        for record in result["records"]:
            log_line = "{}: {}".format(result["plugin"].label, record.msg)
            logger.info(log_line)
            logs.append(log_line)

        if result["error"]:
            error_message = error_format.format(**result)

    return PublishReturnItem(logs, error_message)
