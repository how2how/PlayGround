# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dlg_file.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
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
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setObjectName("splitter")
        self.listView = QtWidgets.QListView(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(35)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listView.sizePolicy().hasHeightForWidth())
        self.listView.setSizePolicy(sizePolicy)
        self.listView.setMinimumSize(QtCore.QSize(100, 0))
        self.listView.setMouseTracking(True)
        # self.listView.setTabletTracking(True)
        self.listView.setObjectName("listView")
        self.treeView = QtWidgets.QTreeView(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(65)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeView.sizePolicy().hasHeightForWidth())
        self.treeView.setSizePolicy(sizePolicy)
        self.treeView.setMinimumSize(QtCore.QSize(200, 0))
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.setObjectName("treeView")
        self.horizontalLayout.addWidget(self.splitter)
        self.action_newfile = QtWidgets.QAction(File)
        self.action_newfile.setObjectName("action_newfile")
        self.action_upload = QtWidgets.QAction(File)
        self.action_upload.setObjectName("action_upload")
        self.action_download = QtWidgets.QAction(File)
        self.action_download.setObjectName("action_download")
        self.action_refresh = QtWidgets.QAction(File)
        self.action_refresh.setObjectName("action_refresh")
        self.action_newfolder = QtWidgets.QAction(File)
        self.action_newfolder.setObjectName("action_newfolder")

        self.retranslateUi(File)
        QtCore.QMetaObject.connectSlotsByName(File)

    def retranslateUi(self, File):
        _translate = QtCore.QCoreApplication.translate
        File.setWindowTitle(_translate("File", "Dialog"))
        self.action_newfile.setText(_translate("File", "新建文件"))
        self.action_upload.setText(_translate("File", "上传"))
        self.action_upload.setToolTip(_translate("File", "上传文件"))
        self.action_download.setText(_translate("File", "下载"))
        self.action_refresh.setText(_translate("File", "刷新"))
        self.action_newfolder.setText(_translate("File", "新建文件夹"))

import test_rc
