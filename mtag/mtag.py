#coding: gbk
import sys
import math
import os
import cPickle

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ui import main_ui

from HeapProfileParser import HeapProfileParser
from HeapProfileAddressTable import HeapProfileAddressTable

import config

class MtagApp(QApplication):
	def __init__(self, sys_argv, *args):
		QApplication.__init__(self, sys_argv, *args)


class StackNode(object):
	def __init__(self, parent, funcName, fileName, lineNo, libName, liveCount, liveBytes, sumCount, sumBytes):
		self.funcName = funcName
		self.fileName = fileName
		self.lineNo = lineNo
		self.libName = libName
		self.liveCount = liveCount
		self.liveBytes = liveBytes
		self.sumCount = sumCount
		self.sumBytes = sumBytes
		self.childs = []
		self.parent = parent
		self.tag = '<Remain>'

	def childCount(self):
		return len(self.childs)

	def child(self, index):
		return self.childs[index]

	def append(self, node):
		if node not in self.childs:
			self.childs.append(node)

	def clear(self):
		for child in self.childs:
			child.clear()
		self.tag = '<Remain>'
		self.childs = []

	def syncTag(self, other, outTags):
		self.tag = other.tag
		
		if self.tag != '<Remain>':
			outTags.add(self.tag)
		
		def get_childmap(node):
			cmap = {}
			for ch in node.childs:
				cmap[(ch.funcName, ch.fileName, ch.lineNo)] = ch
			return cmap
		other_childmap = get_childmap(other)
		
		for ch in self.childs:
			other_ch = other_childmap.get( (ch.funcName, ch.fileName, ch.lineNo), None )
			if other_ch:
				ch.syncTag(other_ch, outTags)


class StackTree(object):
	def __init__(self):
		self.root = StackNode(None, '__root__', '??', 0, '??', 0,0,0,0)

	def clear(self):
		self.root.clear()

	def empty(self):
		return self.root.childCount() == 0

	def scanTag(self, node, tag, result):
		if node.tag == tag:
			result[tag][0] += node.liveCount
			result[tag][1] += node.liveBytes
			result[tag][2] += node.sumCount
			result[tag][3] += node.sumBytes
			return
		childCount = node.childCount()
		for i in xrange(childCount):
			child = node.child(i)
			self.scanTag(child, tag, result)

	def scanTagValues(self, tagList):
		result = {}
		for tag in tagList:
			result.setdefault(tag, [0,0,0,0])
			self.scanTag(self.root, tag, result)
		return result

	def getTotalValues(self):
		result = [0, 0, 0, 0]
		for child in self.root.childs:
			result[0] += child.liveCount
			result[1] += child.liveBytes
			result[2] += child.sumCount
			result[3] += child.sumBytes
		return result

	def syncTagsFrom(self, other):
		tagList = set()
		self.root.syncTag(other.root, tagList)
		return list(tagList)

class ComboEditor(QComboBox):
	def __init__(self, parent, keydata):
		super(ComboEditor, self).__init__(parent)
		self.setEditable(False)
		self.keydata = keydata

class TagDelegate(QStyledItemDelegate):
	def __init__(self, parent=None):
		super(TagDelegate, self).__init__(parent)
		self.mainWnd = parent

	def createEditor(self, parent, option, index):
		#print parent, option, index.column(), index.row(), index.data().toPyObject()
		if index.column() == 1:
			return ComboEditor(parent, index.data().toPyObject())
		else:
			return QStyledItemDelegate.createEditor(self, parent, option, index)			

	def setEditorData(self, editor, index):
		if index.column() == 1:
			#tagList = index.model().data(index, Qt.UserRole).toPyObject()
			tagList = self.mainWnd._tagList
			for tag in tagList:
				editor.addItem(tag)
		else:
			return QStyledItemDelegate.setEditorData(self, editor, index)

	def checkParentsTag(self, model, index, tag):
		found = False
		parentIdx = index.parent()
		while parentIdx.isValid():
			stacknode = model.data(parentIdx, Qt.UserRole).toPyObject()
			print 'parent', stacknode
			if stacknode and tag == stacknode.tag:
				found = True
			parentIdx = parentIdx.parent()
		return found

	def recGetChildTags(self, model, index, tags):
		#print 'child', model.data(index, Qt.DisplayRole).toPyObject()
		stacknode = model.data(index, Qt.UserRole).toPyObject()
		if stacknode:
			tags.add(stacknode.tag)

		rowCount = model.rowCount(parent = index)
		for i in xrange(rowCount):
			childIdx = index.child(i, 0)
			self.recGetChildTags(model, childIdx, tags)

	def setModelData(self, editor, model, index):
		if index.column() == 1:
			funcNameIdx = model.index(index.row(), 0, index.parent())
			
			curTag = editor.currentText()
			if self.checkParentsTag(model, funcNameIdx, curTag):
				print '[error]', 'this tag already found in parents'
				return
			
			childTags = set()
			rowCount = model.rowCount(parent=funcNameIdx)
			self.recGetChildTags(model, funcNameIdx, childTags)
			#print 'child tag', childTags
			if curTag in list(childTags):
				print '[error]', 'this tag already found in children'
				return

			stacknode = model.data(funcNameIdx, Qt.UserRole).toPyObject()
			print 'userData', stacknode
			stacknode.tag = curTag
			model.setData(funcNameIdx, QVariant(stacknode), Qt.UserRole)
			model.setData(index, QVariant(curTag), Qt.DisplayRole)

			self.mainWnd.onTagChanged()
		else:
			return QStyledItemDelegate.setModelData(self, editor, model, index)

class Main(QMainWindow, main_ui.Ui_MainWindow):
	def __init__(self, parent=None):
		super(Main, self).__init__(parent)
		self._tagList = config.Tags
		self.stackTree = StackTree()

		self.setupUi(self)
		self.treeHeap.setColumnWidth(0,300)
		self.treeHeap.setColumnWidth(1,100)
		self.treeHeap.setColumnWidth(2,250)
		self.treeHeap.setColumnWidth(3,100)
		self.treeHeap.setColumnWidth(4,100)
		self.treeHeap.setColumnWidth(5,100)
		self.treeHeap.setColumnWidth(6,100)
		
		self._initEvents()


	def _initEvents(self):
		self.treeHeap.setItemDelegate(TagDelegate(self))

		self.treeContextMenu = QMenu(self)

		self.action_addTag = QAction('Add Tag', self.treeContextMenu)
		self.action_addTag.triggered.connect(self._addTag)
		self.treeHeap.addAction(self.action_addTag)
		self.treeHeap.setContextMenuPolicy(Qt.ActionsContextMenu)

		self.action_LoadHeap.triggered.connect(self._loadHeap)
		self.action_SaveTag.triggered.connect(self._saveTag)
		self.action_AddTag.triggered.connect(self._addTag)
		self.action_LoadTag.triggered.connect(self._loadTag)

		self.btnNewTag.clicked.connect(self._addTag)

	def _addTag(self):
		newtag = self.editTagName.text()
		oldset = set(self._tagList)
		oldset.add(newtag)
		self._tagList = list(oldset)
		self._updateTable()

	def _loadTag(self):
		fileName = QFileDialog.getOpenFileName(self, u"打开tag文件", u"", u"Tag文件(*.tagfile)")
		if fileName:
			with open(fileName, 'r') as fp:
				self.taggedStackTree = cPickle.loads(fp.read())
				self._updateTags()

	def _updateTags(self):
		if self.stackTree.empty() or self.taggedStackTree.empty():
			return
		
		self._tagList = self.stackTree.syncTagsFrom(self.taggedStackTree)
		self._updateUI()

	def _checkTag(self, key, tag):
		curNode = self.root
		while True:
			childCount = curNode.childCount()
			nextNode = None
			for i in xrange(childCount):
				child = curNode.child(i)


	def _saveTag(self):
		fileName = QFileDialog.getSaveFileName(self, u"保存tag文件", u"", u"Tag文件(*.tagfile)")
		if fileName:
			with open(fileName, 'w') as fp:
				fp.write(cPickle.dumps(self.stackTree))

	def _loadHeap(self):
		fileName = QFileDialog.getOpenFileName(self, u"打开Tcmalloc Heap文件", u"", u"Heap文件(*.heap)")
		if fileName:
			self.heapFile = fileName
			self.parser = HeapProfileParser()
			self.parser.parseIt(fileName)
			
			print '==== LibInfo ===='
			for lib in self.parser.libInfo:
				print lib

		#	print '\n==== AddressInfo ===='
		#	for addr in self.parser.addressInfo:
		#		print addr

			self.addrTbl = HeapProfileAddressTable(self.parser)
			self.addrTbl.buildTable()
			print len(self.parser.addressInfo), len(self.parser.addressInfo[0])

		#	cnt = 0
		#	for x in self.parser.addressInfo:
		#		cnt += 1
		#		if cnt > 5:
		#			break
		#		print '------------------------------------------------'
		#		for addr in x[1]:
		#			print self.addrTbl.addr2name(addr)

			self._buildStackTree()
			self._updateUI()

	def onTagChanged(self):
		self._updateTable()

	def itemDataChanged(self, topLeft, bottomRight):
		if topLeft.column() == 1 and bottomRight.column() == 1:
			print 'itemChanged', topLeft.column(), topLeft.row(), bottomRight.column(), bottomRight.row()

	def _buildStackTree(self):
		self.stackTree.clear()
		for sample in self.parser.addressInfo:
			liveCount, liveBytes, sumCount, sumBytes = sample[0]
			stack = sample[1]
			stack_depth = len(stack)
			depth = 0
			curNode = self.stackTree.root
			while True:
				addr = stack[depth]
				funcName, fileName, lineNo, libName = self.addrTbl.addr2name(addr)
				addrKey = (funcName, fileName, lineNo, libName)
				childCount = curNode.childCount()
				nextNode = None
				for i in xrange(childCount):
					child = curNode.child(i)
					userKey = (child.funcName, child.fileName, child.lineNo, child.libName)
					if userKey == addrKey:
						nextNode = child
				if not nextNode:
					nextNode = StackNode(curNode, funcName, fileName, lineNo, libName, liveCount, liveBytes, sumCount, sumBytes)
					curNode.append(nextNode)
				else:
					nextNode.liveCount += liveCount
					nextNode.liveBytes += liveBytes
					nextNode.sumCount += sumCount
					nextNode.sumBytes += sumBytes
				curNode = nextNode
				depth += 1
				if depth >= stack_depth:
					break

	def _addStackNodeUI(self, parentTreeItem, stacknode):
		newItem = QTreeWidgetItem(parentTreeItem)
		newItem.setFlags( newItem.flags() | Qt.ItemIsEditable )
		newItem.setText(0, stacknode.funcName)			# function name
		newItem.setData(0, Qt.UserRole, QVariant(stacknode))		# save 
		#newItem.setData(1, Qt.UserRole, self._tagList)	# tag

		newItem.setText(1, stacknode.tag)
		moduleName = os.path.split(stacknode.libName)[1]
		newItem.setText(2, '[%s]%s, Line:%d'%(moduleName, stacknode.fileName, stacknode.lineNo))	# code line
		newItem.setText(3, str(stacknode.liveCount))
		newItem.setText(4, str(stacknode.liveBytes))
		newItem.setText(5, str(stacknode.sumCount))
		newItem.setText(6, str(stacknode.sumBytes))

		childCount = stacknode.childCount()
		for i in xrange(childCount):
			child = stacknode.child(i)
			self._addStackNodeUI( newItem, child )

	def _updateTable(self):
		tagValues = self.stackTree.scanTagValues(self._tagList)
		tagCount = len(self._tagList)
		
		self.tableWidget.setColumnCount(6)
		self.tableWidget.setRowCount(tagCount+2)

		sumValues = [0, 0, 0, 0]
		totalValues = self.stackTree.getTotalValues()
		for i in xrange(tagCount):
			tag = self._tagList[i]
			sumValues[0] += tagValues[tag][0]
			sumValues[1] += tagValues[tag][1]
			sumValues[2] += tagValues[tag][2]
			sumValues[3] += tagValues[tag][3]

			self.tableWidget.setItem(i, 0, QTableWidgetItem(tag))
			self.tableWidget.setItem(i, 1, QTableWidgetItem(str(tagValues[tag][0])))
			self.tableWidget.setItem(i, 2, QTableWidgetItem('%.4fM'%(tagValues[tag][1]/1024.0/1024.0)))
			self.tableWidget.setItem(i, 3, QTableWidgetItem(str(tagValues[tag][2])))
			self.tableWidget.setItem(i, 4, QTableWidgetItem('%.4fM'%(tagValues[tag][3]/1024.0/1024.0)))
			self.tableWidget.setItem(i, 5, QTableWidgetItem('%.2f%%'%(tagValues[tag][1]*100.0/totalValues[1])))

		remainValues = [ (totalValues[i] - sumValues[i]) for i in xrange(4) ]
		self.tableWidget.setItem(tagCount, 0, QTableWidgetItem('<Remain>'))
		self.tableWidget.setItem(tagCount, 1, QTableWidgetItem(str(remainValues[0])))
		self.tableWidget.setItem(tagCount, 2, QTableWidgetItem('%.4fM'%(remainValues[1]/1024.0/1024.0)))
		self.tableWidget.setItem(tagCount, 3, QTableWidgetItem(str(remainValues[2])))
		self.tableWidget.setItem(tagCount, 4, QTableWidgetItem('%.4fM'%(remainValues[3]/1024.0/1024.0)))
		self.tableWidget.setItem(tagCount, 5, QTableWidgetItem('%.2f%%'%(remainValues[1]*100.0/totalValues[1])))
		
		self.tableWidget.setItem(tagCount+1, 0, QTableWidgetItem('<Total>'))
		self.tableWidget.setItem(tagCount+1, 1, QTableWidgetItem(str(totalValues[0])))
		self.tableWidget.setItem(tagCount+1, 2, QTableWidgetItem('%.4fM'%(totalValues[1]/1024.0/1024.0)))
		self.tableWidget.setItem(tagCount+1, 3, QTableWidgetItem(str(remainValues[2])))
		self.tableWidget.setItem(tagCount+1, 4, QTableWidgetItem('%.4fM'%(totalValues[3]/1024.0/1024.0)))
		self.tableWidget.setItem(tagCount+1, 5, QTableWidgetItem('%.2f%%'%(totalValues[1]*100.0/totalValues[1])))


	def _updateUI(self):
		self.treeHeap.clear()

		self.root = QTreeWidgetItem(self.treeHeap)
		self.root.setText(0, "root")
		self.treeHeap.addTopLevelItem(self.root)

		for child in self.stackTree.root.childs:
			self._addStackNodeUI(self.root, child)

		self._updateTable()

'''
		for sample in self.parser.addressInfo:
			liveCount, liveBytes, sumCount, sumBytes = sample[0]
			stack = sample[1]
			stack_depth = len(stack)
			depth = 0
			curNode = self.root
			while True:
				addr = stack[depth]
				funcName, fileName, lineNo = self.addrTbl.addr2name(addr)
				tagData = {
					'key': (funcName, fileName, lineNo),
					'tag': '<Remain>',
				}
				qtagData = QVariant(tagData)

				childCount = curNode.childCount()
				nextNode = None
				for i in xrange(childCount):
					child = curNode.child(i)
					userData = child.data(0, Qt.UserRole).toPyObject()
					userKey = userData[QString('key')]
					if userKey == tagData['key']:
						nextNode = child
				if not nextNode:
					nextNode = QTreeWidgetItem(curNode)
					nextNode.setFlags( nextNode.flags() | Qt.ItemIsEditable )
					nextNode.setText(0, funcName)			# function name
					nextNode.setData(0, Qt.UserRole, qtagData)		# save 
					nextNode.setData(1, Qt.UserRole, self._tagList)	# tag

					nextNode.setText(1, '<Remain>')
					nextNode.setText(2, '%s, Line:%d'%(fileName, lineNo))	# code line
					nextNode.setText(3, str(liveCount))
					nextNode.setText(4, str(liveBytes))
					nextNode.setText(5, str(sumCount))
					nextNode.setText(6, str(sumBytes))
				curNode = nextNode
				depth += 1
				if depth >= stack_depth:
					break
'''

if __name__ == "__main__":
	app = MtagApp(sys.argv)
	main = Main()
	main.show()
	app.exec_()
