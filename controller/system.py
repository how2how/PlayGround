from PyQt5.QtCore import QThreadPool, QProcess, QObject, Qt
from PyQt5.QtWidgets import *


class System(QObject):
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

    def output(self, widget=None, encoding='utf-8'):
        if not widget:
            return str(self.process.readAll(), encoding=encoding)
        if isinstance(widget, QTextEdit):
            cursor = self.textEdit.textCursor()
            cursor.movePosition(cursor.End)
            cursor.insertText(str(self.process.readAll(), encoding=encoding))
            self.textEdit.setTextCursor(cursor)
            self.textEdit.ensureCursorVisible()

    def input(self, widget=None):\
        pass

    def run(self):
        pass

    def write_data(self, data):
        if not data.endswith('\n'):
            data += '\n'
            self.process.write(bytes(data, encoding='utf-8'))

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
