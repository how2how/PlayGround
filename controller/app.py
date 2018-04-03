# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import *

from controller.ui import *
# from controller.ui.MainTable import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.action_test.triggered.connect(self.onExitTriggered)
        self.action_cmd.triggered.connect(self.onCmdTriggered)
        self.action_file.triggered.connect(self.onFileTriggered)
        self.action_process.triggered.connect(self.onProcessTriggered)
        self.action_ctlSettings.triggered.connect(self.onCtlSettingsTriggered)
        self.action_svrSettings.triggered.connect(self.onSvrSettingsTriggered)

    def onExitTriggered(self):
        btn = QMessageBox.question(self, "", "是否确定退出？",
                                   QMessageBox.Ok|QMessageBox.Cancel)
        if btn == QMessageBox.Ok:
            qApp.quit()

    def onCmdTriggered(self):
        cmd = DialogCmd(self)
        cmd.show()

    def onFileTriggered(self):
        print('file')

    def onProcessTriggered(self):
        print('process')

    def onCtlSettingsTriggered(self):
        print('Ctlsettings')

    def onSvrSettingsTriggered(self):
        print('Svrsettings')


class DialogFile(QDialog, Ui_File):
    def __init__(self, parent=None):
        super(DialogFile, self).__init__(parent)
        self.setupUi(self)


class DialogCmd(QDialog, Ui_Cmd):
    def __init__(self, parent=None):
        super(DialogCmd, self).__init__(parent)
        self.setupUi(self)


# class DialogProcess(QDialog, Ui_Process):
#     def __init__(self, parent=None):
#         super(DialogProcess, self).__init__(parent)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
