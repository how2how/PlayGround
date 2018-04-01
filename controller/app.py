# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication

# from controller.ui.controller import Ui_MainWindow
from controller.ui.MainTable import Ui_MainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(win)
    win.show()
    sys.exit(app.exec_())
