# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created: Wed Jan 21 22:51:05 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1062, 819)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tableWidget = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, item)
        self.gridLayout.addWidget(self.tableWidget, 2, 0, 1, 1)
        self.treeHeap = QtGui.QTreeWidget(self.centralwidget)
        self.treeHeap.setMinimumSize(QtCore.QSize(0, 500))
        self.treeHeap.setObjectName(_fromUtf8("treeHeap"))
        self.gridLayout.addWidget(self.treeHeap, 1, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.editTagName = QtGui.QLineEdit(self.centralwidget)
        self.editTagName.setMaximumSize(QtCore.QSize(200, 16777215))
        self.editTagName.setObjectName(_fromUtf8("editTagName"))
        self.horizontalLayout.addWidget(self.editTagName)
        self.btnNewTag = QtGui.QPushButton(self.centralwidget)
        self.btnNewTag.setObjectName(_fromUtf8("btnNewTag"))
        self.horizontalLayout.addWidget(self.btnNewTag)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1062, 23))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menu = QtGui.QMenu(self.menubar)
        self.menu.setObjectName(_fromUtf8("menu"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.action_LoadHeap = QtGui.QAction(MainWindow)
        self.action_LoadHeap.setObjectName(_fromUtf8("action_LoadHeap"))
        self.action_LoadTag = QtGui.QAction(MainWindow)
        self.action_LoadTag.setObjectName(_fromUtf8("action_LoadTag"))
        self.action_SaveTag = QtGui.QAction(MainWindow)
        self.action_SaveTag.setObjectName(_fromUtf8("action_SaveTag"))
        self.action_AddTag = QtGui.QAction(MainWindow)
        self.action_AddTag.setObjectName(_fromUtf8("action_AddTag"))
        self.menu.addAction(self.action_LoadHeap)
        self.menu.addAction(self.action_LoadTag)
        self.menu.addAction(self.action_SaveTag)
        self.menu.addSeparator()
        self.menu.addAction(self.action_AddTag)
        self.menubar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Tag", None))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Live Count", None))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Live Bytes", None))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Sum Count", None))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Sum Bytes", None))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "Percentage", None))
        self.treeHeap.headerItem().setText(0, _translate("MainWindow", "函数名", None))
        self.treeHeap.headerItem().setText(1, _translate("MainWindow", "Tag", None))
        self.treeHeap.headerItem().setText(2, _translate("MainWindow", "代码行", None))
        self.treeHeap.headerItem().setText(3, _translate("MainWindow", "Live Counts", None))
        self.treeHeap.headerItem().setText(4, _translate("MainWindow", "Live Bytes", None))
        self.treeHeap.headerItem().setText(5, _translate("MainWindow", "Sum Counts", None))
        self.treeHeap.headerItem().setText(6, _translate("MainWindow", "Sum Bytes", None))
        self.btnNewTag.setText(_translate("MainWindow", "新建 Tag", None))
        self.menu.setTitle(_translate("MainWindow", "文件", None))
        self.action_LoadHeap.setText(_translate("MainWindow", "加载Heap文件...", None))
        self.action_LoadTag.setText(_translate("MainWindow", "加载Tag分类...", None))
        self.action_SaveTag.setText(_translate("MainWindow", "保存Tag分类...", None))
        self.action_AddTag.setText(_translate("MainWindow", "添加新Tag...", None))

