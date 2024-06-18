from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt, QSortFilterProxyModel, QDate
from PyQt5 import QtGui
from utils import functions

#Model for main treeview display in DashboardView
class PartFeaturesModel(QAbstractItemModel):
    def __init__(self, part_data, parent=None):
        super(PartFeaturesModel, self).__init__(parent)
        
        self.part_data = part_data if part_data is not None else []
        
    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        
        if not parent.isValid():
            part = self.part_data[row]
            return self.createIndex(row, column, part)
        else: 
            part = parent.internalPointer()
            feature = part['features'][row]
            return self.createIndex(row, column, feature)
        
    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        
        child = index.internalPointer()
        if  'features' in child:
            
            return QModelIndex()
        else:
            for part in self.part_data:
                if child in part.get('features', []):
                    parent_row = self.part_data.index(part)
                    return self.createIndex(parent_row, 0, part)
        return QModelIndex()
    
    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            return len(self.part_data)
        else: 
            part = parent.internalPointer()
            return len(part.get('features', []))
        
    def columnCount(self, parent=QModelIndex()):
        return 6
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        item = index.internalPointer()
        if role == Qt.DisplayRole:
            if 'feature' in item:
                if index.column() == 0:
                    return f"Feature #: {item['feature']}"
                elif index.column() == 1:
                    return f"KPC Designation: {item['designation']}"
                elif index.column() == 2:
                    return f"KPC Number: {item['kpcNum']}"
                elif index.column() == 3:
                    return f"Tolerance Value: {item['tol']}"
                elif index.column() == 4:
                    return f"Engine: {item['engine']}"
                elif index.column() == 5:
                    return f"CPK: {item.get('cpk', 'N/A')}"
            else:
                if index.column() == 0:
                    return item.get('partNumber', '')
                elif index.column() == 1:
                    return item.get('rev', '')
                elif index.column() == 2:
                    date_string = item.get('uploadDate')
                    if date_string:
                        formatted_date = functions.format_date(date_string)
                    return formatted_date
                elif index.column() == 3:
                    return item.get('dueDate', '')
                elif index.column() == 4:
                    return item.get('notes', '')
            pass
        elif role == Qt.BackgroundRole:
            if 'currentManufacturing' in item and item['currentManufacturing']:
                return QtGui.QBrush(QtGui.QColor('red'))     
        return None
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            headers = ['Part Number', 'Revision', 'Last Upload Date', 'Upload Due Date', 'notes']
            if section < len(headers):
                return headers[section]
        return None
            
    def getPartId(self, index):
        if not index.isValid():
            return None
        item = index.internalPointer()
        
        return item.get('partNumber')
    
    def updateData(self, new_data):
        self.beginResetModel()
        self.part_data = new_data
        self.endResetModel()
        
        
#Model for sorting by date 
class DateSortProxyModel(QSortFilterProxyModel):
    def __init__(self, dateColumnIndex, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.dateColumnIndex = dateColumnIndex
    def lessThan(self, left, right):
        if left.column() == self.dateColumnIndex and right.column() == self.dateColumnIndex:
            leftData = self.sourceModel().data(left)
            rightData = self.sourceModel().data(right)
        
            leftDate = QDate.fromString(leftData, 'MM/dd/yyyy')
            rightDate = QDate.fromString(rightData, 'MM/dd/yyyy')
        
            
            return leftDate < rightDate
        else:
            return super(DateSortProxyModel, self).lessThan(left, right)
        