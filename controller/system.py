import threading

from PyQt5.QtCore import QThreadPool, QProcess, QObject, Qt
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtWidgets import *


class SysOutput(QObject):
    """Handle standard I/O queue"""
    data_avail = Signal()

    def __init__(self):
        QObject.__init__(self)
        self.queue = []
        self.lock = threading.Lock()

    def write(self, val):
        self.lock.acquire()
        self.queue.append(val)
        self.lock.release()
        self.data_avail.emit()

    def empty_queue(self):
        self.lock.acquire()
        s = "".join(self.queue)
        self.queue = []
        self.lock.release()
        return s

    # We need to add this method to fix Issue 1789
    def flush(self):
        pass

    # This is needed to fix Issue 2984
    @property
    def closed(self):
        return False


class WidgetProxyData(object):
    pass


class WidgetProxy(QObject):
    """Handle Shell widget refresh signal"""

    sig_new_prompt = Signal(str)
    sig_set_readonly = Signal(bool)
    sig_edit = Signal(str, bool)
    sig_wait_input = Signal(str)

    def __init__(self, input_condition):
        QObject.__init__(self)
        self.input_data = None
        self.input_condition = input_condition

    def new_prompt(self, prompt):
        self.sig_new_prompt.emit(prompt)

    def set_readonly(self, state):
        self.sig_set_readonly.emit(state)

    def edit(self, filename, external_editor=False):
        self.sig_edit.emit(filename, external_editor)

    def data_available(self):
        """Return True if input data is available"""
        return self.input_data is not WidgetProxyData

    def wait_input(self, prompt=''):
        self.input_data = WidgetProxyData
        self.sig_wait_input.emit(prompt)

    def end_input(self, cmd):
        self.input_condition.acquire()
        self.input_data = cmd
        self.input_condition.notify()
        self.input_condition.release()


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
