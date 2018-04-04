# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dlg_process.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Process(object):
    def setupUi(self, Process):
        Process.setObjectName("Process")
        Process.resize(448, 500)
        self.verticalLayout = QtWidgets.QVBoxLayout(Process)
        self.verticalLayout.setObjectName("verticalLayout")
        self.listView = QtWidgets.QListView(Process)
        self.listView.setObjectName("listView")
        self.verticalLayout.addWidget(self.listView)

        self.retranslateUi(Process)
        QtCore.QMetaObject.connectSlotsByName(Process)

    def retranslateUi(self, Process):
        _translate = QtCore.QCoreApplication.translate
        Process.setWindowTitle(_translate("Process", "Dialog"))

