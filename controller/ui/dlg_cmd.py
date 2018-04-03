# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dlg_cmd.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Cmd(object):
    def setupUi(self, Cmd):
        Cmd.setObjectName("Cmd")
        Cmd.resize(850, 658)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Cmd)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.textEdit = QtWidgets.QTextEdit(Cmd)
        self.textEdit.setObjectName("textEdit")
        self.horizontalLayout.addWidget(self.textEdit)

        self.retranslateUi(Cmd)
        QtCore.QMetaObject.connectSlotsByName(Cmd)

    def retranslateUi(self, Cmd):
        _translate = QtCore.QCoreApplication.translate
        Cmd.setWindowTitle(_translate("Cmd", "Dialog"))

