# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dlg_process.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Process(object):
    def setupUi(self, Process):
        Process.setObjectName("Process")
        Process.resize(448, 500)
        Process.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.verticalLayout = QtWidgets.QVBoxLayout(Process)
        self.verticalLayout.setObjectName("verticalLayout")
        self.listView = QtWidgets.QListView(Process)
        self.listView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.listView.setObjectName("listView")
        self.verticalLayout.addWidget(self.listView)
        self.action_kill = QtWidgets.QAction(Process)
        self.action_kill.setObjectName("action_kill")
        self.action_refresh = QtWidgets.QAction(Process)
        self.action_refresh.setObjectName("action_refresh")

        self.retranslateUi(Process)
        QtCore.QMetaObject.connectSlotsByName(Process)

    def retranslateUi(self, Process):
        _translate = QtCore.QCoreApplication.translate
        Process.setWindowTitle(_translate("Process", "Dialog"))
        self.action_kill.setText(_translate("Process", "结束进程"))
        self.action_refresh.setText(_translate("Process", "  刷  新"))

