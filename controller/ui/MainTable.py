# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainTable.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(928, 655)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(6, item)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.tableWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 928, 20))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.about = QtWidgets.QMenu(self.menubar)
        self.about.setObjectName("about")
        self.menu_2 = QtWidgets.QMenu(self.menubar)
        self.menu_2.setObjectName("menu_2")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setStyleSheet("image: url(:/test/folder);")
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.toolBar_2 = QtWidgets.QToolBar(MainWindow)
        self.toolBar_2.setObjectName("toolBar_2")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar_2)
        self.action_file = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/test/folder"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_file.setIcon(icon)
        self.action_file.setObjectName("action_file")
        self.action_cmd = QtWidgets.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/test/cmd"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_cmd.setIcon(icon1)
        self.action_cmd.setObjectName("action_cmd")
        self.action_process = QtWidgets.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/test/process"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_process.setIcon(icon2)
        self.action_process.setObjectName("action_process")
        self.action_test = QtWidgets.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/test/exit"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_test.setIcon(icon3)
        self.action_test.setObjectName("action_quit")
        self.action_ctlSettings = QtWidgets.QAction(MainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/test/settings"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_ctlSettings.setIcon(icon4)
        self.action_ctlSettings.setObjectName("action_ctlSettings")
        self.action_svrSettings = QtWidgets.QAction(MainWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/test/server_settings"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_svrSettings.setIcon(icon5)
        self.action_svrSettings.setObjectName("action_svrSettings")
        self.menu.addAction(self.action_ctlSettings)
        self.menu.addAction(self.action_svrSettings)
        self.menu_2.addAction(self.action_file)
        self.menu_2.addAction(self.action_cmd)
        self.menu_2.addAction(self.action_process)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())
        self.menubar.addAction(self.about.menuAction())
        self.toolBar.addAction(self.action_ctlSettings)
        self.toolBar.addAction(self.action_svrSettings)
        self.toolBar.addAction(self.action_test)
        self.toolBar_2.addAction(self.action_file)
        self.toolBar_2.addAction(self.action_cmd)
        self.toolBar_2.addAction(self.action_process)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Id"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Ip"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Host"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "OS"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "User"))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "Mark"))
        item = self.tableWidget.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "SessionId"))
        self.menu.setTitle(_translate("MainWindow", "配置"))
        self.about.setTitle(_translate("MainWindow", "关于"))
        self.menu_2.setTitle(_translate("MainWindow", "功能"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.toolBar_2.setWindowTitle(_translate("MainWindow", "toolBar_2"))
        self.action_file.setIconText(_translate("MainWindow", "文件管理"))
        self.action_file.setToolTip(_translate("MainWindow", "文件管理"))
        self.action_file.setStatusTip(_translate("MainWindow", "文件管理"))
        self.action_file.setShortcut(_translate("MainWindow", "Ctrl+Shift+F"))
        self.action_cmd.setText(_translate("MainWindow", "命令执行"))
        self.action_cmd.setToolTip(_translate("MainWindow", "命令执行"))
        self.action_cmd.setShortcut(_translate("MainWindow", "Ctrl+Shift+C"))
        self.action_process.setText(_translate("MainWindow", "进程管理"))
        self.action_process.setToolTip(_translate("MainWindow", "进程管理"))
        self.action_process.setShortcut(_translate("MainWindow", "Ctrl+Shift+P"))
        self.action_test.setText(_translate("MainWindow", "退出"))
        self.action_test.setToolTip(_translate("MainWindow", "关闭系统"))
        self.action_test.setShortcut(_translate("MainWindow", "Ctrl+Q"))
        self.action_ctlSettings.setText(_translate("MainWindow", "控制端配置"))
        self.action_ctlSettings.setToolTip(_translate("MainWindow", "控制端配置"))
        self.action_ctlSettings.setShortcut(_translate("MainWindow", "Ctrl+Alt+C"))
        self.action_svrSettings.setText(_translate("MainWindow", "服务端设置"))
        self.action_svrSettings.setToolTip(_translate("MainWindow", "服务端设置"))
        self.action_svrSettings.setShortcut(_translate("MainWindow", "Ctrl+Alt+S"))

from controller import test_rc
