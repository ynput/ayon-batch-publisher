import collections

from qtpy import QtWidgets, QtCore, QtGui

from ayon_core.tools.context_dialog import ContextDialog

from .batch_publisher_model import BatchPublisherModel

FOLDER_PATH_ROLE = QtCore.Qt.UserRole + 1


class BatchPublisherTableDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, controller, parent=None):
        super(BatchPublisherTableDelegate, self).__init__(parent)
        self._controller = controller

    def createEditor(self, parent, option, index):
        model = index.model()
        ingest_file = model.get_product_items()[index.row()]

        if index.column() == BatchPublisherModel.COLUMN_OF_FOLDER:
            editor = None
            view = parent.parent()
            # NOTE: Project name has been disabled to change from this dialog
            accepted, _project_name, folder_path, task_name = \
                self._on_choose_context(ingest_file.folder_path)
            # if accepted and folder_path:
            if folder_path:
                for _index in view.selectedIndexes():
                    model.setData(
                        model.index(_index.row(), model.COLUMN_OF_FOLDER),
                        folder_path,
                        QtCore.Qt.EditRole)
                    if task_name:
                        model.setData(
                            model.index(_index.row(), model.COLUMN_OF_TASK),
                            task_name,
                            QtCore.Qt.EditRole)

            return editor

        elif index.column() == BatchPublisherModel.COLUMN_OF_TASK:
            task_names = self._controller.get_task_names(
                ingest_file.folder_path)
            editor = QtWidgets.QComboBox(parent)
            editor.addItems(task_names)
            return editor

        elif index.column() == BatchPublisherModel.COLUMN_OF_PRODUCT_TYPE:
            product_types = self._controller.get_product_types()
            product_types = sorted(product_types)
            editor = QtWidgets.QComboBox(parent)
            editor.addItems(product_types)
            return editor

    def setEditorData(self, editor, index):
        if index.column() == BatchPublisherModel.COLUMN_OF_TASK:
            editor.blockSignals(True)
            value = index.data(QtCore.Qt.DisplayRole)
            row = editor.findText(value)
            editor.setCurrentIndex(row)
            editor.blockSignals(False)
        elif index.column() == BatchPublisherModel.COLUMN_OF_PRODUCT_TYPE:
            editor.blockSignals(True)
            value = index.data(QtCore.Qt.DisplayRole)
            row = editor.findText(value)
            editor.setCurrentIndex(row)
            editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        model = index.model()
        if index.column() == BatchPublisherModel.COLUMN_OF_TASK:
            value = editor.currentText()
            model.setData(index, value, QtCore.Qt.EditRole)
        elif index.column() == BatchPublisherModel.COLUMN_OF_PRODUCT_TYPE:
            value = editor.currentText()
            model.setData(index, value, QtCore.Qt.EditRole)

    def _on_choose_context(self, folder_path):
        project_name = self._controller.get_selected_project_name()
        dialog = ContextDialog()
        dialog._project_combobox.hide()
        dialog.set_context(
            project_name=project_name)
        accepted = dialog.exec_()
        # if accepted:
        context = dialog.get_context()
        project = context["project"]
        asset = context["asset"]
        # AYON version of dialog stores the folder path
        folder_path = context.get("folder_path")
        folder_path = folder_path or asset
        task_name = context["task"]
        return accepted, project, folder_path, task_name
        # return accepted, None, None, None


class ComboBox(QtWidgets.QComboBox):

    def keyPressEvent(self, event):
        # This is to prevent pressing "a" button with folder cell
        # selected and the "assets" is selected in QComboBox.
        # A default behaviour coming from QComboBox, when key is pressed
        # it selects first matching item in QComboBox root model index.
        # We don't want to select the "assets", since its not a full path
        # of folder.
        if event.type() == QtCore.QEvent.KeyPress:
            return