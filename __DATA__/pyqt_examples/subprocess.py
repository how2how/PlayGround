# -*- coding: utf-8 -*-
# 直接运行， 提示请在命令行中运行， 运行参数， -install   -open=C:\document\apple.mp3    -color=red|green|yellow
from PyQt5 import QtCore, QtGui, QtWidgets
import sys, os
import subprocess


class class_cmds(QtWidgets.QWidget):
    Cargv = QtCore.pyqtSignal(list)  # 定义一个带list参数的signal

    def __init__(self, ):
        super(class_cmds, self).__init__()
        # 直接运行exe
        if sys.argv.__len__() == 1:
            self.dobexec()
            sys.exit()

        self.resize(100, 100)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint)  # 去掉windowHint
        self.setWindowIcon(QtGui.QIcon('favicon.ico'))
        self.Cargv.connect(self.dialogg)  # 触发信号后连接到一个槽dialogg

        is_show_btn = ''
        for arg in sys.argv:
            if arg == '-install':
                is_show_btn = '安装软件！'
            color = arg.split('-color=')  # 设置背景颜色
            if color.__len__() >= 2:
                try:
                    '''
                    palette1 = QtGui.QPalette(self)
                    palette1.setColor(QtGui.QPalette.Background, QtGui.QColor(192, 253, 123))  # 设置背景颜色
                    self.setPalette(palette1)
                    '''
                    self.setStyleSheet('background-color:'+color[1])
                except:
                    pass
            copen = arg.split('-open=')  # 打开一个文件
            if copen.__len__() >= 2:
                try:
                    subprocess.Popen(copen[1])  # 非阻塞, 可打开exe，但对于.mp3、xls、txt、pdf 无效
                    # os.system(str(copen[1]))
                    pass
                except:
                    pass
        if is_show_btn:
            self.verticalLayout = QtWidgets.QVBoxLayout()
            self.pushButton = QtWidgets.QPushButton(is_show_btn)
            self.verticalLayout.addWidget(self.pushButton)
            self.setLayout(self.verticalLayout)
            self.pushButton.clicked.connect(self.ok)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def ok(self):
        self.Cargv.emit(sys.argv)  # 发射一个信号

    def dialogg(self, list):
        QtWidgets.QMessageBox.about(self, '安装提示！', '可实行逻辑安装！' + list[0])

    # 直接运行
    def dobexec(self):
        QtWidgets.QMessageBox.information(None, "运行提示！",
                                          "<p>请在命令行中运行!运行参数包括：</p>"
                                          "<p><b>-install：</b>开始安装软件</p>"
                                          "<p><b>-open=path：</b>打开一个path的文件，如：-open=C:\\document\\apple.mp3</p>"
                                          "<p><b>-color：</b>color 显示exe背景颜色， 其中color=（ red|green|yellow ）</p>")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myclass = class_cmds()
    myclass.show()
    sys.exit(app.exec_())