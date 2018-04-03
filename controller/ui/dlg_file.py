# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dlg_file.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_File(object):
    def setupUi(self, File):
        File.setObjectName("File")
        File.resize(530, 210)
        File.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.horizontalLayout = QtWidgets.QHBoxLayout(File)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.splitter = QtWidgets.QSplitter(File)
        self.splitter.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.splitter.setLineWidth(3)
        self.splitter.setMidLineWidth(3)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setHandleWidth(3)
        self.splitter.setObjectName("splitter")
        self.treeView = QtWidgets.QTreeView(self.splitter)
        self.treeView.setObjectName("treeView")
        self.listView = QtWidgets.QListView(self.splitter)
        self.listView.setMouseTracking(True)
        self.listView.setProperty("tabletTracking", True)
        self.listView.setObjectName("listView")
        self.horizontalLayout.addWidget(self.splitter)
        self.action_new = QtWidgets.QAction(File)
        self.action_new.setObjectName("action_new")

        self.retranslateUi(File)
        QtCore.QMetaObject.connectSlotsByName(File)

    def retranslateUi(self, File):
        _translate = QtCore.QCoreApplication.translate
        File.setWindowTitle(_translate("File", "Dialog"))
        self.action_new.setText(_translate("File", "新建"))
        self.action_new.setShortcut(_translate("File", "Ctrl+N"))

import test_rc
