# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dlg_svrSettings.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_svrSettings(object):
    def setupUi(self, svrSettings):
        svrSettings.setObjectName("svrSettings")
        svrSettings.resize(410, 172)
        svrSettings.setModal(True)
        self.buttonBox = QtWidgets.QDialogButtonBox(svrSettings)
        self.buttonBox.setGeometry(QtCore.QRect(50, 130, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtWidgets.QLabel(svrSettings)
        self.label.setGeometry(QtCore.QRect(20, 30, 131, 21))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.url = QtWidgets.QLineEdit(svrSettings)
        self.url.setGeometry(QtCore.QRect(20, 60, 371, 21))
        self.url.setObjectName("url")
        self.frame = QtWidgets.QFrame(svrSettings)
        self.frame.setGeometry(QtCore.QRect(10, 20, 391, 91))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.retranslateUi(svrSettings)
        self.buttonBox.accepted.connect(svrSettings.accept)
        self.buttonBox.rejected.connect(svrSettings.reject)
        QtCore.QMetaObject.connectSlotsByName(svrSettings)

    def retranslateUi(self, svrSettings):
        _translate = QtCore.QCoreApplication.translate
        svrSettings.setWindowTitle(_translate("svrSettings", "Dialog"))
        self.label.setText(_translate("svrSettings", "木马配置文件地址："))

