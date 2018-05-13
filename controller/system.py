import json

from PyQt5.QtCore import QThreadPool, QProcess, QObject, Qt, pyqtSignal


class Client(object):

    def __init__(self, ip, hostname=None, OS=None, user=None, cwd=None):
        self.ip = ip
        self.hostname = hostname
        self.os = OS
        self.user = user
        self.cwd = cwd

    def __repr__(self):
        return dict(ip=self.ip, hostname=self.hostname, os=self.os, user=self.user, cwd=self.cwd)

    def __str__(self):
        return json.dumps(self)


class System(QObject):
    sig_data_ready = pyqtSignal(str)
    sig_client_connect = pyqtSignal(object)
    sig_wait_input = pyqtSignal()
    sig_system_started = pyqtSignal()
    sig_system_shutdown = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.prog = None
        self.args = []
        self.task_list = []
        self.process = QProcess(self)

    def add_handler(self, handler):
        pass

    def redirect_stdio(self):
        pass

    def start(self, prog=None, args=None):
        self.prog = prog or "python"
        self.args = args or ['-c', 'from server.core.shells.multi import MultiShell;MultiShell().start()']
        self.process.start(prog, args)
        self.sig_system_started.emit()

    def restart(self):
        pass

    def shutdown(self):
        self.process.terminate()
        self.sig_system_shutdown.emit()

    def stop(self):
        pass

    def output(self, text=None, encoding='utf-8'):
        text = text or str(self.process.readAll(), encoding=encoding)
        self.sig_data_ready.emit(text)

    def input(self, data):
        if not data.endswith('\n'):
            data += '\n'
            self.process.write(bytes(data, encoding='utf-8'))

    def run(self):
        pass

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()


class ShelMixin(QObject):
    sig_new_client = pyqtSignal()

    def __init__(self, shell):
        self.shell = shell
