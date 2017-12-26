from PythonQt.QtGui import *
from PythonQt.QtCore import Qt

import traceback

class ConfigDialog(QDialog):
    def __init__(self, cfg, schema, plugin, parent=None):
        super(QDialog, self).__init__(parent)

        self.schema = schema
        self.plugin = plugin

        self.setAttribute(Qt.WA_DeleteOnClose)

        self.lay = QFormLayout(self)

        for k, v in schema.items():
            label = QLabel(v[1], self)
            edit = QLineEdit(self)
            setattr(self, f'{k}label', label)
            setattr(self, f'{k}edit', edit)
            self.lay.addRow(label)
            self.lay.addRow(edit)

        self.buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.lay.addRow(self.buttonbox)

        self.connect("finished(int)", self.onClose)
        self.buttonbox.connect("accepted()", self.accept)
        self.buttonbox.connect("rejected()", self.reject)

        self.cfg = cfg

        try:
            self.initValues()
        except Exception as e:
            self.delete()
            raise e

    def initValues(self):
        for k, v in self.schema.items():
            edit = getattr(self, f'{k}edit')
            edit.setText(self.cfg.get(k))

    def onClose(self, r):
        if r == QDialog.Accepted:
            try:
                for k, v in self.schema.items():
                    edit = getattr(self, f'{k}edit')
                    self.cfg[k] = edit.text

                self.plugin.onConfigUpdate()
            except:
                print(traceback.format_exc())

