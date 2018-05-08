from PyQt5.QtCore import QThreadPool, QProcess, QObject, Qt, pyqtSignal
from PyQt5.QtWidgets import *


class System(QObject):
    onDataReady = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.task_list = []
        self.process = QProcess(parent)

    def _start(self, prog, args):
        self.process.start(prog, args)

    def restart(self):
        pass

    def shutdown(self):
        self.process.terminate()

    def stop(self):
        pass

    def output(self, text=None, encoding='utf-8'):
        text = text or str(self.process.readAll(), encoding=encoding)
        self.onDataReady.emit(text)

    def input(self, data):
        if not data.endswith('\n'):
            data += '\n'
            self.process.write(bytes(data, encoding='utf-8'))

    def run(self):
        pass

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
