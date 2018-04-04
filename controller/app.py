# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtGui
from PyQt5 import QtCore
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
        btn = QMessageBox.question(self, "退出", "是否确定退出？",
                                   QMessageBox.Ok|QMessageBox.Cancel)
        if btn == QMessageBox.Ok:
            qApp.quit()

    def onCmdTriggered(self):
        cmd = DialogCmd(self)
        cmd.show()

    def onFileTriggered(self):
        file = DialogFile(self)
        file.show()

    def onProcessTriggered(self):
        process = DialogProcess(self)
        process.show()

    def onCtlSettingsTriggered(self):
        ctl = DialogCtlSettings(self)
        ctl.show()

    def onSvrSettingsTriggered(self):
        svr = DialogSvrSettings(self)
        svr.show()


class DialogFile(QDialog, Ui_File):
    def __init__(self, parent=None):
        super(DialogFile, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('File')

        self.treeView.customContextMenuRequested.connect(self.open_right_menu)
        self.action_upload.triggered.connect(self.upload_file)

    def open_right_menu(self, po):
        popMenu = QMenu(self)
        popMenu.addAction(self.action_new)
        popMenu.addAction(self.action_upload)
        popMenu.addAction(self.action_download)
        popMenu.addSeparator()
        popMenu.addAction(self.action_refresh)
        popMenu.exec_(self.treeView.viewport().mapToGlobal(po))

    def new_file(self, fname='New Text.txt'):
        pass

    def new_folder(self, name='New Folder'):
        pass

    def upload_file(self):
        filename, _ = QFileDialog(self, '打开文件', '.', '*')
        print(filename)
        # with open(filename, 'r') as f:
        #     f.read()


class DialogCmd(QDialog, Ui_Cmd):
    def __init__(self, parent=None):
        super(DialogCmd, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('Cmd')


class DialogProcess(QDialog, Ui_Process):
    def __init__(self, parent=None):
        super(DialogProcess, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('Process Manager')


class DialogSvrSettings(QDialog, Ui_svrSettings):
    def __init__(self, parent=None):
        super(DialogSvrSettings, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Server Setting")


class DialogCtlSettings(QDialog, Ui_ctlSettings):
    def __init__(self, parent=None):
        super(DialogCtlSettings, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('Controller Setting')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
