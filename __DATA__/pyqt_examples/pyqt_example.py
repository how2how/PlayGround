from PyQt5.QtWidgets import *
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QSize, QPoint, QRect, QModelIndex
import sys
class Example(QMainWindow): # 继承QMainWindow
　　#初步介绍常用控件的用法，以后会单独介绍每种控件的详细用法
    def __init__(self):
        super().__init__()
        self.setUi()
    def setUi(self):
        self.statusBar().showMessage('statusbar')
        self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle('test')
        self.setMouseTracking(True)
        self.setFixedSize(800, 400)
        #==============PushButton
        self.pushButton = QPushButton(self)
        self.pushButton.setStyleSheet('text-align: center;'
                                      'width:60;'
                                      'height:40;'
                                      'background:yellow;') # 竟然支持css 很强大
        self.pushButton.setText('这是一个测试按钮')
        #===============Label
        self.label = QLabel(self)
        self.label.setGeometry(QRect(10, 130, 300, 40))
        self.label.setText('我是label标签')
        #===============comboBox
        self.comboBox = QComboBox(self)
        self.comboBox.setGeometry(QRect(10, 60, 100, 60))
        itemdata = ['item0', 'item1', 'item2']
        self.comboBox.addItems(itemdata)
        self.comboBox.currentIndexChanged.connect(self._comboxChanged)
        #设置当前默认item index = 0 第一个选项
        self.comboBox.setCurrentIndex(0)
        #=-=============listWidget 普通listview 或者 widget不能添加表头,要使用表头请使用 treeView
        self.listWidget = QListWidget(self)
        self.listWidget.addItems(['item1', 'item2', 'item3'])
        self.listWidget.setGeometry(QRect(10, 160, 160, 100))
        self.listWidget.setFixedWidth(60) # 设置固定宽度
        self.listWidget.itemClicked.connect(self._listClicked)
        #===============treeWidget
        self.treeWidget = QTreeWidget(self)
        self.treeWidget.setGeometry(QRect(170, 160, 160, 100))
        headers = ['head1', 'head2', 'head3']
        self.treeWidget.setColumnCount(3)
        self.treeWidget.setColumnWidth(0, 50)
        self.treeWidget.setColumnWidth(1, 50)
        self.treeWidget.setColumnWidth(2, 50)
        self.treeWidget.setHeaderLabels(headers)
        #===============tableWidget
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setGeometry(QRect(340, 160, 224, 100))
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setColumnWidth(0, 60)
        self.tableWidget.setColumnWidth(1, 60)
        self.tableWidget.setColumnWidth(2, 60)
 
        self.tableWidget.setHorizontalHeaderLabels(('head1', 'head2', 'head3'))
        self.tableWidget.setSelectionMode(QTableWidget.NoSelection)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed) # 表头不可拖动
        self.tableWidget.itemClicked.connect(self._tableItem_OnClicked) # item被点击事件
        #初始化十行 row 注意 row　与 item 的区别
 
        for count in range(10):
            self.tableWidget.insertRow(count)
            #填充列项
            self.tableWidget.setItem(count, 0, QTableWidgetItem('item0'))
            self.tableWidget.setItem(count, 1, QTableWidgetItem('item1'))
            self.tableWidget.setItem(count, 2, QTableWidgetItem('item2'))
        self.show()
    def _comboxChanged(self, index):
        self.label.setText('comboboxChanged: index-%d item-%s' %(index, self.comboBox.itemText(index)))
    def _listClicked(self, item):
        print(item.text())
        index  = self.listWidget.indexFromItem(item) #type: QModelIndex # 数据模型 用来定位数据，行信息，列信息，item文本等
        print(index.row()) #获取所在行
    def _tableItem_OnClicked(self, item):
        tmp = item #type: QTableWidgetItem
        print(tmp.text())
        print(self.tableWidget.indexFromItem(tmp).row()) #获取所在行<br>　　　

　　def mousePressEvent(self, e):  # 鼠标点击事件
        if e.button() == Qt.LeftButton:
            print('leftbutton clicked')
        elif e.button() == Qt.RightButton:
            self.popMenu.exec(self.cursor().pos())  # 弹出菜单
        print('x:', e.x(), 'y:', e.y())  # 这里x y坐标是全局坐标 转换成client 需要用mapFromGlobal

    def changeEvent(self, e):
        print(e.type())  # type 代表改变事件的类型，并不是指具体的事件，比如窗口状态的改变，并没有说具体的窗口状态
        if self.windowState() == Qt.WindowMinimized:
            print('窗口最小化')
        elif self.windowState() == Qt.WindowMaximized:
            print('窗口最大化')　　　

if __name__ == '__main__': app = QApplication(sys.argv)
	ex = Example()
	sys.exit(app.exec_()) # 防止和python exec 冲突

