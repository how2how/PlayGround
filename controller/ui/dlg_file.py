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
        File.resize(600, 450)
        File.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.horizontalLayout = QtWidgets.QHBoxLayout(File)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.splitter = QtWidgets.QSplitter(File)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.listView = QtWidgets.QListView(self.splitter)
        self.listView.setMouseTracking(True)
        self.listView.setProperty("tabletTracking", True)
        self.listView.setObjectName("listView")
        self.treeView = QtWidgets.QTreeView(self.splitter)
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.setObjectName("treeView")
        self.horizontalLayout.addWidget(self.splitter)
        self.action_new = QtWidgets.QAction(File)
        self.action_new.setObjectName("action_new")
        self.action_upload = QtWidgets.QAction(File)
        self.action_upload.setObjectName("action_upload")
        self.action_download = QtWidgets.QAction(File)
        self.action_download.setObjectName("action_download")
        self.action_refresh = QtWidgets.QAction(File)
        self.action_refresh.setObjectName("action_refresh")

        self.retranslateUi(File)
        QtCore.QMetaObject.connectSlotsByName(File)

    def retranslateUi(self, File):
        _translate = QtCore.QCoreApplication.translate
        File.setWindowTitle(_translate("File", "Dialog"))
        self.action_new.setText(_translate("File", "新建"))
        self.action_upload.setText(_translate("File", "上传"))
        self.action_upload.setToolTip(_translate("File", "上传文件"))
        self.action_download.setText(_translate("File", "下载"))
        self.action_refresh.setText(_translate("File", "刷新"))

import test_rc
