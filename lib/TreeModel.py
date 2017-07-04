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
            if item.depth == 0:
                return QBrush(QColor(157,159,85))
            if item.depth == 1:
                return QBrush(QColor(85,157,159))
            if item.depth == 2:
                return QBrush(QColor(85,120,159))

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

        self.aoiItem = TreeItem(["AOI","Revision","Edited"], self.base, 0)
        self.udtItem = TreeItem(["UDT","Decription","Type"], self.base, 0)

        self.base.appendChild(self.aoiItem)
        self.base.appendChild(self.udtItem)

        self.aois = self.getAois()

        self.udts = self.getUdts()

        self.draw()

    def getAois(self):
        aois = []
        for aoi in self.root.iter("AddOnInstructionDefinition"):
            aois.append({   'name'  : aoi.attrib['Name'],
                            'rev'   : aoi.attrib['Revision'],
                            'edited': aoi.attrib['EditedDate']})
        return aois

    def getUdts(self):
        udts = []
        for udt in self.root.iter("DataType"):
            desc = udt.findall("Description")
            if desc:
                desc = desc[0]
            else:
                desc = ""

            members = udt.findall("Members/Member")
            mems = []
            for member in members:
                mdes = member.findall("Description")
                if mdes:
                    mdes = mdes[0]
                else:
                    mdes = ""
                mems.append({'name' : member.attrib['Name'],
                             'desc' : mdes,
                             'type' : member.attrib['DataType']})


            udts.append({   'name'  : udt.attrib['Name'],
                            'desc'  : desc,
                            'mems'  : mems})
        return udts

    def draw(self):
        for aoi in self.aois:
            item = TreeItem([aoi['name'], aoi['rev'], aoi['edited']], self.aoiItem, 1)
            self.aoiItem.appendChild(item)

        for udt in self.udts:
            item = TreeItem([udt['name'], udt['desc']], self.udtItem, 1)
            self.udtItem.appendChild(item)
            for member in udt['mems']:
                memberItem = TreeItem([member['name'], member['desc'], member['type']], item, 2)
                item.appendChild(memberItem)
