import sys
import hashlib
import re
from datetime import datetime, timedelta, date
import time
import typing
from pymongo import MongoClient
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton, QWidget, QLineEdit, QLabel, QTableWidget, QTableWidgetItem, QDockWidget, QHeaderView, QFileSystemModel
from PyQt5 import QtCore
from PyQt5.QtCore import QModelIndex, Qt, QDir, QAbstractItemModel, Qt, pyqtSignal
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlRelation
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QTableView,
    QTreeView,
    QTreeWidget,
    QTreeWidgetItem,
)
from utils import database

emailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
passwordRegex = r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$'

class loginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KPC Manager")
        self.resize(400, 200)
        
        layout = QGridLayout()
        
        # Email form 
        emailLabel = QLabel('Email:')
        self.emailInput = QLineEdit()
        self.emailInput.setPlaceholderText('Enter Email')
        layout.addWidget(emailLabel, 0, 0)
        layout.addWidget(self.emailInput, 0, 1)
        
        # Password form
        passwordLabel = QLabel('Password:')
        self.passwordInput = QLineEdit()
        self.passwordInput.setPlaceholderText('Enter Password')
        layout.addWidget(passwordLabel, 1, 0)
        layout.addWidget(self.passwordInput, 1, 1)
        
        # Login Button
        loginButton = QPushButton('Login')
        loginButton.clicked.connect(self.loginSubmit)
        layout.addWidget(loginButton, 2, 0, 1, 2)
        
        registerButton = QPushButton('Register')
        registerButton.clicked.connect(self.registerSubmit)
        layout.addWidget(registerButton, 3, 0, 1, 2)
        
        self.setLayout(layout)
        
        # function to handle button submit
    def loginSubmit(self):
        email = self.emailInput.text()
        pwd = self.passwordInput.text()
            
        login(email, pwd)
        
    def registerSubmit(self):
        global r
        r = registerWindow()
        r.show()
        window.close()
        
class registerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KPC Manager")
        self.resize(400, 200)
        
        layout = QGridLayout()
        
        # Email form 
        emailLabel = QLabel('Email:')
        self.emailInput = QLineEdit()
        self.emailInput.setPlaceholderText('Enter Email')
        layout.addWidget(emailLabel, 0, 0)
        layout.addWidget(self.emailInput, 0, 1)
        
        # Password form
        passwordLabel = QLabel('Password:')
        self.passwordInput = QLineEdit()
        self.passwordInput.setPlaceholderText('Enter Password')
        layout.addWidget(passwordLabel, 1, 0)
        layout.addWidget(self.passwordInput, 1, 1)
        
        # Repeat Password form
        repeatPasswordLabel = QLabel('Repeat Password:')
        self.repeatPasswordInput = QLineEdit()
        self.repeatPasswordInput.setPlaceholderText('repeat Password')
        layout.addWidget(repeatPasswordLabel, 2, 0)
        layout.addWidget(self.repeatPasswordInput, 2, 1)
        
        # Register Button
        registerButton = QPushButton('Register')
        registerButton.clicked.connect(self.registerUser)
        layout.addWidget(registerButton, 3, 0, 1, 2)
        
        self.setLayout(layout)
        
        # function to handle button submit
    def registerUser(self):
        email = self.emailInput.text()
        pwd = self.passwordInput.text()
        confPwd = self.repeatPasswordInput.text()
            
        register(email, pwd, confPwd)
        
class partForm(QWidget):
    partSubmitted = pyqtSignal()
    def __init__(self, mode="add", partId=None):
        super().__init__()
        self.mode = mode
        self.partId = partId
        self.setWindowTitle("Part")
        self.resize(800, 600)
        
        layout = QGridLayout()
        
        # Part number form 
        partLabel = QLabel('Part Number:')
        self.partInput = QLineEdit()
        self.partInput.setPlaceholderText('Enter part number')
        layout.addWidget(partLabel, 0, 0)
        layout.addWidget(self.partInput, 1, 0)
        
        # Part revision form
        revLabel = QLabel('Revision Letter:')
        self.revInput = QLineEdit()
        self.revInput.setPlaceholderText('Enter revision letter')
        layout.addWidget(revLabel, 0, 1)
        layout.addWidget(self.revInput, 1, 1)
        
        # upload date form
        udLabel = QLabel('Last Net-Inspect Upload Date:')
        self.udInput = QLineEdit()
        self.udInput.setPlaceholderText('Enter upload date')
        layout.addWidget(udLabel, 0, 2)
        layout.addWidget(self.udInput, 1, 2)
        
        # Notes form
        notesLabel = QLabel('Notes:')
        self.notesInput = QLineEdit()
        self.notesInput.setPlaceholderText('Enter notes')
        layout.addWidget(notesLabel, 0, 3)
        layout.addWidget(self.notesInput, 1, 3)
        
        # Submit button Button
        addFeatureButton = QPushButton('Add Feature')
        addFeatureButton.clicked.connect(self.addFeature)
        layout.addWidget(addFeatureButton, 5, 1, 1, 2)
        
        addPartButton = QPushButton('Save Part')
        addPartButton.setStyleSheet("background-color: #3ADC73")
        addPartButton.clicked.connect(self.submitPart)
        layout.addWidget(addPartButton, 6, 0, 1, 4)
        
        cancelButton = QPushButton('Cancel')
        cancelButton.setStyleSheet("background-color: #D6575D")
        cancelButton.clicked.connect(self.closeWindow)
        layout.addWidget(cancelButton, 7, 0, 1, 4)
        
        self.featureTable = QTableWidget()
        self.featureTable.setColumnCount(5)
        self.featureTable.setHorizontalHeaderLabels(["Feature Number", "KPC Designation", "KPC Number", "Tolerance", "Engine"])
        self.featureTable.horizontalHeader().setStretchLastSection(False)
        for column in range(self.featureTable.columnCount()):
            self.featureTable.horizontalHeader().setSectionResizeMode(column, QHeaderView.Stretch)
            
        layout.addWidget(self.featureTable, 4, 0, 1, 4)
        
        
        self.setLayout(layout)
    def addFeature(self):
            self.featureForm = FeatureForm(self)
            self.featureForm.show()
            
    def addFeatureToTable(self, feature_data):
        row_position = self.featureTable.rowCount()
        self.featureTable.insertRow(row_position)
        for i, key in enumerate(['feature', 'designation', 'kpcNum', 'tol', 'engine']):
            self.featureTable.setItem(row_position, i, QTableWidgetItem(feature_data[key]))
            
    def submitPart(self):
                
        upload_date_str = self.udInput.text()
        upload_date = datetime.strptime(upload_date_str, '%m/%d/%Y')
        due_date = upload_date + timedelta(days=90)
        due_date_str = due_date.strftime('%m/%d/%Y')
        new_part_data = {
            "partNumber": self.partInput.text(),
            "rev": self.revInput.text(),
            "uploadDate": self.udInput.text(),
            "dueDate": due_date_str,
            "notes": self.notesInput.text(),
            "features": []
        }
        for row in range(self.featureTable.rowCount()):
            feature = {
                "feature": self.featureTable.item(row, 0).text(),
                "designation": self.featureTable.item(row, 1).text(),
                "kpcNum": self.featureTable.item(row, 2).text(),
                "tol": self.featureTable.item(row, 3).text(),
                "engine": self.featureTable.item(row, 4).text(),
            }
            new_part_data["features"].append(feature)
            
        def on_submit_success(is_success):
            if is_success:
                self.partSubmitted.emit()
        if self.mode == "add":
            database.submit_new_part(new_part_data, callback=on_submit_success)
        elif self.mode == "edit":
            database.update_part_by_id(self.partId, new_part_data, callback=on_submit_success)
            
        self.close()
    
    def loadPartData(self, selectedPartData):
        self.partInput.setText(selectedPartData['partNumber'])
        self.revInput.setText(selectedPartData['rev'])
        self.udInput.setText(selectedPartData['uploadDate'])
        self.notesInput.setText(selectedPartData['notes'])
        
        self.featureTable.setRowCount(0)
        for feature in selectedPartData['features']:
            self.addFeatureToTable(feature)
    
    def closeWindow(self):
        self.close()
        
class dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KPC Manager")
        self.resize(1200, 800)
        
        self.mainWidget = QWidget(self)
        self.mainLayout = QVBoxLayout()
        
        self.tree_view = PartTreeView(self)
        self.part_data = database.get_all_data()
        self.model = PartFeaturesModel(self.part_data)
        self.tree_view.setModel(self.model)
        self.tree_view.resize(1200,800)
        self.mainLayout.addWidget(self.tree_view)
        
        self.addPart = QPushButton('Add Part')
        self.addPart.setStyleSheet("background-color: #3ADC73")
        self.addPart.clicked.connect(self.openPartForm)
        self.mainLayout.addWidget(self.addPart)
        
        self.editPart = QPushButton('Edit Selected Part')
        self.editPart.setStyleSheet("background-color: #DFDA41")
        self.editPart.clicked.connect(self.editSelectedPart)
        self.mainLayout.addWidget(self.editPart)
        
        self.uploadPartData = QPushButton('Upload Data for selected Part')
        self.uploadPartData.setStyleSheet("background-color: #E6A42B")
        self.uploadPartData.clicked.connect(self.openUploadForm)
        self.mainLayout.addWidget(self.uploadPartData)
        
        self.deletePart = QPushButton('Delete Part')
        self.deletePart.setStyleSheet("background-color: #D6575D")
        self.deletePart.clicked.connect(self.deleteSelectedPart)
        self.mainLayout.addWidget(self.deletePart)
        
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)
        
    def openPartForm(self):
        self.partForm = partForm()
        self.partForm.partSubmitted.connect(self.refreshTreeView)
        self.partForm.show()
        
    def openUploadForm(self):
        index = self.tree_view.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Selection", "No part selected.")
            return
        part_id = self.model.getPartId(index)
        if part_id is None:
            QMessageBox.warning(self, "Error", "Failed to identify selected part.")
            return
        
        selectedPartData = database.get_part_by_id(part_id)
        if not selectedPartData:
            QMessageBox.warning(self, "Error", "Could not find part data.")
            return
        
        self.uploadForm = uploadDataForm(partId = part_id)
        self.uploadForm.loadPartData(selectedPartData)
        self.uploadForm.dataSubmitted.connect(self.refreshTreeView)
        self.uploadForm.show()
        
    def deleteSelectedPart(self):
        index = self.tree_view.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Selection", "No part selected.")
            return
        part_id = self.model.getPartId(index)
        if part_id is None:
            QMessageBox.warning(self, "Error", "Failed to identify selected part.")
            return
        database.delete_part(self, part_id)
        
    def editSelectedPart(self):
        index = self.tree_view.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Selection", "No part selected.")
            return
        part_id = self.model.getPartId(index)
        print(part_id)
        if part_id is None:
            QMessageBox.warning(self, "Error", "Failed to identify selected part.")
            return
        
        selectedPartData = database.get_part_by_id(part_id)
        if not selectedPartData:
            QMessageBox.warning(self, "Error", "Could not find part data.")
            return
        
        self.partForm = partForm(mode="edit", partId=part_id)
        self.partForm.loadPartData(selectedPartData)
        self.partForm.partSubmitted.connect(self.refreshTreeView)
        self.partForm.show()       
        
        
    def refreshTreeView(self):
        updated_parts_data = database.get_all_data()
        
        self.model.updateData(updated_parts_data)
        
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
        return 5
    
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
            else: 
                if index.column() == 0:
                    return item.get('partNumber', '')
                elif index.column() == 1:
                    return item.get('rev', '')
                elif index.column() == 2:
                    return item.get('uploadDate', '')
                elif index.column() == 3:
                    return item.get('dueDate', '')
                elif index.column() == 4:
                    return item.get('notes', '')
                    
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
        
        
class PartTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(QHeaderView.Stretch)
        self.setUniformRowHeights(True)
            
    def resizeEvent(self, event):
        super().resizeEvent(event)
        
    def setModel(self, model):
        super().setModel(model)
        
class FeatureForm(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Add Feature")
        self.resize(600, 100)
        
        layout = QGridLayout()
        
        # Part number form 
        featureLabel = QLabel('Feature Number:')
        self.featureInput = QLineEdit()
        self.featureInput.setPlaceholderText('Enter Feature Number')
        layout.addWidget(featureLabel, 0, 0)
        layout.addWidget(self.featureInput, 1, 0)
        
        # Part revision form
        kpcLabel = QLabel('KPC Designation:')
        self.kpcInput = QLineEdit()
        self.kpcInput.setPlaceholderText('Enter KPC Designation')
        layout.addWidget(kpcLabel, 0, 1)
        layout.addWidget(self.kpcInput, 1, 1)
        
        # upload date form
        kpcNumLabel = QLabel('KPC Number:')
        self.kpcNumInput = QLineEdit()
        self.kpcNumInput.setPlaceholderText('Enter KPC Number from Net-Inspect')
        layout.addWidget(kpcNumLabel, 0, 2)
        layout.addWidget(self.kpcNumInput, 1, 2)
        
        # Notes form
        requirementLabel = QLabel('Requirement:')
        self.requirementInput = QLineEdit()
        self.requirementInput.setPlaceholderText('Enter Blueprint Requirement')
        layout.addWidget(requirementLabel, 0, 3)
        layout.addWidget(self.requirementInput, 1, 3)
        
        engineLabel = QLabel('Engine:')
        self.engineInput = QLineEdit()
        self.engineInput.setPlaceholderText('Enter Part Engine Program')
        layout.addWidget(engineLabel, 0, 4)
        layout.addWidget(self.engineInput, 1, 4)
        
        # Submit button Button
        addFeatureButton = QPushButton('Add Feature')
        addFeatureButton.setStyleSheet("background-color: #3ADC73")
        addFeatureButton.clicked.connect(self.submitFeature)
        layout.addWidget(addFeatureButton, 2, 2, 1, 1)
        
        cancelButton = QPushButton('Cancel')
        cancelButton.setStyleSheet("background-color: #D6575D")
        cancelButton.clicked.connect(self.closeWindow)
        layout.addWidget(cancelButton, 3, 2, 1, 1)
        
        self.setLayout(layout)
        
    def submitFeature(self):
        
        feature_data = {
            "feature": self.featureInput.text(),
            "designation": self.kpcInput.text(),
            "kpcNum": self.kpcNumInput.text(),
            "tol": self.requirementInput.text(),
            "engine": self.engineInput.text(),
        }
        if self.parent:
            self.parent.addFeatureToTable(feature_data)
            
        self.close()
        
    def closeWindow(self):
        self.close()
        
class uploadDataForm(QWidget):
    dataSubmitted = pyqtSignal()
    def __init__(self, mode="add", partId=None):
        super().__init__()
        self.mode = mode
        self.partId = partId
        self.setWindowTitle("Part")
        self.resize(800, 600)
        
        layout = QGridLayout()
        
        # Part number form 
        partLabel = QLabel('Part Number:')
        self.partNumber = QLabel('')
        layout.addWidget(partLabel, 0, 0)
        layout.addWidget(self.partNumber, 0, 1)
        
        # Part revision form
        revLabel = QLabel('Revision Letter:')
        self.revLetter = QLabel('')
        layout.addWidget(revLabel, 0, 2)
        layout.addWidget(self.revLetter, 0, 3)
        
        # upload date form
        udLabel = QLabel('Last Net-Inspect Upload Date:')
        self.uploadDate = QLabel('')
        layout.addWidget(udLabel, 0, 4)
        layout.addWidget(self.uploadDate, 0, 5)
        
        serialNumberLabel = QLabel('Serial Number:')
        self.serialNumberInput = QLineEdit()
        self.serialNumberInput.setPlaceholderText('Enter Serial Number')
        layout.addWidget(serialNumberLabel, 2, 0)
        layout.addWidget(self.serialNumberInput, 2, 1, 1, 2)
        
        addPartButton = QPushButton('Save Data')
        addPartButton.setStyleSheet("background-color: #3ADC73")
        addPartButton.clicked.connect(self.submitData)
        layout.addWidget(addPartButton, 6, 0, 1, 6)
        
        cancelButton = QPushButton('Cancel')
        cancelButton.setStyleSheet("background-color: #D6575D")
        cancelButton.clicked.connect(self.closeWindow)
        layout.addWidget(cancelButton, 7, 0, 1, 6)
        
        self.dataTable = QTableWidget()
        self.dataTable.setColumnCount(3)
        self.dataTable.setHorizontalHeaderLabels(["KPC Number", "Blueprint Requirement", "Measurement"])
        self.dataTable.horizontalHeader().setStretchLastSection(False)
        for column in range(self.dataTable.columnCount()):
            self.dataTable.horizontalHeader().setSectionResizeMode(column, QHeaderView.Stretch)
            
        layout.addWidget(self.dataTable, 4, 0, 1, 6)
        
        
        self.setLayout(layout)
    def addFeature(self):
            self.featureForm = FeatureForm(self)
            self.featureForm.show()
            
    def addFeatureToTable(self, feature_data):
        row_position = self.dataTable.rowCount()
        self.dataTable.insertRow(row_position)
        for i, key in enumerate(['kpcNum', 'tol']):
            self.dataTable.setItem(row_position, i, QTableWidgetItem(feature_data[key]))
            
    def submitData(self):
        upload_date_value = datetime.strftime(date.today())
        upload_date = datetime.strptime(upload_date_value, '%m/%d/%Y')
        due_date = upload_date + timedelta(days=90)
        due_date_str = due_date.strftime('%m/%d/%Y')
        updated_part_data = {
            "uploadDate": upload_date_value,
            "dueDate": due_date_str,
        }
        for row in range(self.dataTable.rowCount()):
            upload_data = {
                "partNumber": self.dataTable.item(row, 0).text(),
                "kpcNum": self.dataTable.item(row, 0).text(),
                "serialNumber": self.dataTable.item(row, 2).text(),
                "measurement": self.dataTable.item(row, 2).text(),
                "uploadDate": upload_date_value,
            }
            
        def on_submit_success(is_success):
            if is_success:
                self.dataSubmitted.emit()
        database.update_part_by_id(self.partId, updated_part_data, callback=on_submit_success)
        database.add_measurement(upload_data)
            
        self.close()
    
    def loadPartData(self, selectedPartData):
        self.partNumber.setText(selectedPartData['partNumber'])
        self.revLetter.setText(selectedPartData['rev'])
        self.uploadDate.setText(selectedPartData['uploadDate'])
        
        self.dataTable.setRowCount(0)
        
        for feature in selectedPartData['features']:
            self.addFeatureToTable(feature)
    
    def closeWindow(self):
        self.close()
        
def renderDashboard():
    global d
    d = dashboard()
    d.show()
    window.close()
    
def login(email, pwd):
        renderDashboard()
    # auth = pwd.encode()
    # password = hashlib.md5(auth).hexdigest()
    # storedData = cursor.execute("SELECT * FROM user WHERE email = (?) AND password = (?)", [email, password])
    
    # loginQueue = []
    
    # for row in storedData:
    #     for x in row:
    #         loginQueue.append(x)
            
    # if (email and password) in loginQueue:
    #     renderDashboard()
    # else:
    #     loginFailed()
        
def register(email, pwd, confPwd):
    if confPwd != pwd:
        passMismatch()
    elif(re.fullmatch(emailRegex, email)) and(re.fullmatch(passwordRegex, pwd)):
        enc = confPwd.encode()
        password = hashlib.md5(enc).hexdigest()
        
        loginQueue = []
    
        if email in loginQueue:
            userExists()
        else:
            print('user has been registered')
        
    else:
        invalid()

def loginFailed():
    dlg = QMessageBox()
    dlg.setWindowTitle('ERROR')
    dlg.setText('Login Failed')
    dlg.exec()
    
def userExists():
    dlg = QMessageBox()
    dlg.setWindowTitle('ERROR')
    dlg.setText('User Already Exists')
    dlg.exec()
    
def invalid():
    dlg = QMessageBox()
    dlg.setWindowTitle('ERROR')
    dlg.setText('Invalid Email or Password')
    dlg.exec()
    
def passMismatch():
    dlg = QMessageBox()
    dlg.setWindowTitle('ERROR')
    dlg.setText('Passwords do not match')
    dlg.exec()
    
app = QApplication(sys.argv)
window = loginWindow()
window.show()
app.exec_()