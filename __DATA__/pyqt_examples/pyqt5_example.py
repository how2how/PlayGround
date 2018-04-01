#-*- coding:utf-8 -*-
#######line table 使用
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys


class MyWindow(QDialog,QWidget):
    def __init__(self,parent = None):
        super(MyWindow,self).__init__(parent)
        self.resize(400,400)
        self.mainlayout = QGridLayout(self)
        self.myTable = QTableWidget()
        self.mainlayout.addWidget(self.myTable)
        self.tableSetting()

    def tableSetting(self):
        self.myTable.setRowCount(3)########设置table的列数
        self.myTable.setColumnCount(3) #######设置table列数
        self.myTable.setColumnWidth(0,60)####设置第一列的宽度
        self.myTable.setHorizontalHeaderLabels([u"控件",u"  文字  ",u"图片"]) ######设置标题栏
        self.myTable.resizeColumnToContents(1) #####第二列根据标题自适应
        self.myTable.setSelectionBehavior(QAbstractItemView.SelectRows) ###设置一次选中一行
        self.myTable.setEditTriggers(QAbstractItemView.NoEditTriggers) ###设置表格禁止编辑
        self.myTable.setContextMenuPolicy(Qt.CustomContextMenu)######允许右键产生子菜单
        self.myTable.customContextMenuRequested.connect(self.generateMenu)   ####右键菜单
        #########设置表格内容
        self.setTableContext()

    def generateMenu(self,pos):
        # print pos
        row_num = -1
        for i in self.myTable.selectionModel().selection().indexes():
            row_num = i.row()
        menu = QMenu()
        item1 = menu.addAction(u"选项一")
        item2 = menu.addAction(u"选项二")
        item3 = menu.addAction(u"选项三" )
        action = menu.exec_(self.myTable.mapToGlobal(pos))
        if action == item1:
            print('您选了选项一，当前行文字内容是：',self.myTable.item(row_num,1).text())

        elif action == item2:
            print('您选了选项二，当前行文字内容是：',self.myTable.item(row_num,1).text())

        elif action == item3:
            print('您选了选项三，当前行文字内容是：',self.myTable.item(row_num,1).text())
        else:
            return

    def setTableContext(self):
        ctrlListCheckBox = [i for i in range(3)]
        for i in range(3):
            self.setRowData(i,ctrlListCheckBox)

    def setRowData(self,row,ctrl):
        ##########在table中添加控件
        ctrl[row] = QCheckBox()
        ctrl[row].setChecked(False)
        ctrl[row].clicked.connect(lambda:self.selectDev(ctrl[row].checkState(),row))
        self.myTable.setCellWidget(row,0,ctrl[row])
        ########table中添加文字
        nameItem = QTableWidgetItem("item"+str(row))
        self.myTable.setItem(row,1,nameItem)
        ########table中添加图片,线添加label控件 再添加图片
        self.label_pic = QLabel()
        self.label_pic.setPixmap(QPixmap(str(row)+".jpg"))
        self.myTable.setCellWidget(row,2,self.label_pic)

    def selectDev(self,check_state,row):
        print('check_state:',check_state)
        print('row:',row)

app=QApplication(sys.argv)
window=MyWindow()
window.show()
app.exec_()