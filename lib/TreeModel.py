from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex
from PyQt5.QtGui import QBrush, QColor
import lxml.etree as ET

from lib.TreeItem import TreeItem

class TreeModel(QAbstractItemModel):
    def __init__(self, path, parent=None):
        super(TreeModel, self).__init__(parent)


        self.path = path

        self.isHighlighted = False

        self.setupModel(path)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == Qt.BackgroundRole:
            if self.isHighlighted:
                if item.data(1) != item.data(3):
                    return QBrush(QColor(159,87,85))
            if item.depth == 0:
                return QBrush(QColor(157,159,85))
            elif item.depth == 1:
                return QBrush(QColor(85,157,159))
            elif item.depth == 2:
                return QBrush(QColor(85,120,159))
            elif item.depth == 3:
                return QBrush(QColor(87,85,159))
            elif item.depth == 4:
                return QBrush(QColor(120,159,85))

        if role == Qt.EditRole:
            return item.data(index.column())

        if role != Qt.DisplayRole:
            return None

        return item.data(index.column())

    def highlight(self):
        self.isHighlighted = not self.isHighlighted

    def setupModel(self, path):
        self.parser = ET.XMLParser(strip_cdata=False, resolve_entities=False)
        self.tree = ET.parse(path, parser=self.parser)
        self.root = self.tree.getroot()

        self.rootItem = TreeItem(["Hardware", "Hardware Comment", "Connected Parameter"])

        self.base = TreeItem([path.split('/')[-1]], self.rootItem)
        self.rootItem.appendChild(self.base)

        self.aoiItem = TreeItem(["AOI","Revision","Edited"], self.base)
        self.udtItem = TreeItem(["UDT","Decription","Type"], self.base)

        self.base.appendChild(self.aoiItem)
        self.base.appendChild(self.udtItem)

        self.aois = self.getAois()

        self.udts = self.getUdts()

        self.draw()

    def getAois(self):
        print("gettin")

    def getUdts(self):
        print("gettin")

    def draw(self):
        print("drawing")
