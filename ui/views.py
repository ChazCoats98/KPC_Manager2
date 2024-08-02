import shutil
import re
import time
from openpyxl import load_workbook
from utils import database, functions
import mplcursors
import pyqt5_fugueicons as fugue
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from .models import (
    PartFeaturesModel,
    DateSortProxyModel,
    PpapDataModel
    )
from .widgets import RadioButtonTableWidget, SpinnerWidget
from datetime import (
    datetime, 
    timedelta, 
    date
    )
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

#Main window view of application
class DashboardView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KPC Manager")
        self.resize(1200, 800)
        
        self.mainWidget = QWidget(self)
        self.mainLayout = QVBoxLayout()
        
        
        self.tabs = QTabWidget()
        self.kpcTab = QWidget()
        self.ppapTab = QWidget()
        
        self.tabs.addTab(self.kpcTab, 'KPC Manager')
        self.tabs.addTab(self.ppapTab, 'PPAP Manager')
        
        self.kpcTab.layout = QVBoxLayout()
        self.ppapTab.layout = QVBoxLayout()
        
        kpcToolbar = QToolBar('KPC Manager Toolbar')
        ppapToolbar = QToolBar('PPAP Manager Toolbar')
        
        plusIcon = fugue.icon('plus')
        editIcon = fugue.icon('pencil')
        uploadIcon = fugue.icon('blue-document--arrow')
        historicIcon = fugue.icon('clock-history')
        cpkIcon = fugue.icon('edit-mathematics')
        deleteIcon = fugue.icon('cross')
        gageIcon = QPixmap('./assets/gage_rr_logo.png')
        snapshotIcon = fugue.icon('chart-down-color')
        formIcon = fugue.icon('document-text')
        
        buttons = [
            ('Add Part', self.openPartForm, plusIcon),
            ('Edit Part', self.editSelectedPart, editIcon),
            ('Upload Data', self.openUploadForm, uploadIcon),
            ('Historic Data', self.openHistoricalUploadWindow, historicIcon),
            ('CPK Data', self.openCpkDashboard, cpkIcon),
            ('KPC Management Form Dashboard', self.openFormDashboard, formIcon),
            ('Gage R&R Dashboard', self.openGageRRForm, gageIcon),
            ('CPK Snapshot', self.openCpkSnapshot, snapshotIcon),
            ('Delete Part', self.deleteSelectedPart, deleteIcon)
        ]
        for name, callback, icon in buttons:
            actionButton = QAction(QIcon(icon), name, self)
            actionButton.setStatusTip(name)
            actionButton.triggered.connect(callback)
            kpcToolbar.addAction(actionButton)
        
        self.setStatusBar(QStatusBar(self))
        
        self.kpcTab.layout.addWidget(kpcToolbar)
        
        self.kpcTreeView = PartTreeView(self)
        self.part_data = database.get_all_data()
        self.kpcModel = PartFeaturesModel(self.part_data)
        self.kpcProxyModel = QSortFilterProxyModel(self)
        self.kpcProxyModel.setSourceModel(self.kpcModel)
        self.kpcTreeView.setModel(self.kpcProxyModel)
        self.kpcTreeView.setSortingEnabled(True)
        self.kpcTreeView.sortByColumn(3, Qt.AscendingOrder)
        self.kpcTreeView.resize(1200,800)
        self.kpcTab.layout.addWidget(self.kpcTreeView)
        
        addPpapPartButton = QAction(QIcon(plusIcon), 'Add PPAP Part', self)
        addPpapPartButton.setStatusTip('Add PPAP part')
        addPpapPartButton.triggered.connect(self.openPpapPartForm)
        ppapToolbar.addAction(addPpapPartButton)
        
        
        self.ppapTab.layout.addWidget(ppapToolbar)
        
        self.ppapTreeView = ppapTreeView(self)
        self.ppapModel = PpapDataModel(self.part_data)
        self.ppapProxyModel = QSortFilterProxyModel(self)
        self.ppapProxyModel.setSourceModel(self.ppapModel)
        self.ppapTreeView.setModel(self.ppapProxyModel)
        self.ppapTreeView.setSortingEnabled(True)
        self.ppapTreeView.sortByColumn(3, Qt.AscendingOrder)
        self.ppapTreeView.resize(1200,800)
        self.ppapTab.layout.addWidget(self.ppapTreeView)
        
        self.kpcTab.setLayout(self.kpcTab.layout)
        self.ppapTab.setLayout(self.ppapTab.layout)
        
        self.mainLayout.addWidget(self.tabs)
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)
        
    def openPartForm(self):
        self.partForm = partForm()
        self.partForm.partSubmitted.connect(self.refreshTreeView)
        self.partForm.show()
        
    def openFormDashboard(self):
        index = self.kpcTreeView.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Selection", "No part selected.")
            return
        sourceIndex = self.kpcProxyModel.mapToSource(index)
        part_id = self.kpcModel.getPartId(sourceIndex)
        if part_id is None:
            QMessageBox.warning(self, "Error", "Failed to identify selected part.")
            return
        
        selectedPartData = database.get_part_by_id(part_id)
        if not selectedPartData:
            QMessageBox.warning(self, "Error", "Could not find part data.")
            return
        
        self.manForm = ManagementFormWind(partId=part_id)
        self.manForm.loadPartData(selectedPartData)
        self.manForm.show()
        
    def openPpapPartForm(self):
        self.partForm = ppapPartForm()
        self.partForm.partSubmitted.connect(self.refreshTreeView)
        self.partForm.show()
        
    def openGageRRForm(self):
        self.gageRRForm = GageRRForm()
        self.gageRRForm.show()
        
    def openCpkSnapshot(self):
        self.KPCSumWind = KPCSummaryWind()
        self.KPCSumWind.show()
        
        
    def openUploadForm(self):
        index = self.kpcTreeView.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Selection", "No part selected.")
            return
        sourceIndex = self.kpcProxyModel.mapToSource(index)
        part_id = self.kpcModel.getPartId(sourceIndex)
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
        
    def openHistoricalUploadWindow(self):
        index = self.kpcTreeView.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "No part selected.")
            return
        sourceIndex = self.kpcProxyModel.mapToSource(index)
        part_id = self.kpcModel.getPartId(sourceIndex)
        if part_id is None:
            QMessageBox.warning(self, "Error", "Failed to identify selected part.")
            return
        
        selectedPartData = database.get_part_by_id(part_id)
        selectedPartUploadData = database.get_measurements_by_id(part_id)
        print(selectedPartUploadData)
        if not selectedPartData or selectedPartUploadData is None:
            QMessageBox.warning(self, "Error", "Could not find part data.")
            return
        
        try: 
            self.historicalData = HistoricalDataView(partId=part_id)
            self.historicalData.loadPartData(selectedPartData, selectedPartUploadData)
            database.delete_duplicate_measurements()
            self.historicalData.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            print(e)
            
    def openCpkDashboard(self):
        index = self.kpcTreeView.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "No part selected.")
            return
        sourceIndex = self.kpcProxyModel.mapToSource(index)
        part_id = self.kpcModel.getPartId(sourceIndex)
        if part_id is None:
            QMessageBox.warning(self, "Error", "Failed to identify selected part.")
            return
        
        selectedPartData = database.get_part_by_id(part_id)
        selectedPartUploadData = database.get_measurements_by_id(part_id)
        print(selectedPartUploadData)
        if not selectedPartData or selectedPartUploadData is None:
            QMessageBox.warning(self, "Error", "Could not find part data.")
            return
        
        try: 
            self.CpkDashboard = CpkDashboardView(partId=part_id)
            self.CpkDashboard.loadPartData(selectedPartData, selectedPartUploadData)
            database.delete_duplicate_measurements()
            self.CpkDashboard.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            print(e)
        
    def deleteSelectedPart(self):
        index = self.kpcTreeView.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Selection", "No part selected.")
            return
        sourceIndex = self.kpcProxyModel.mapToSource(index)
        part_id = self.kpcModel.getPartId(sourceIndex)
        if part_id is None:
            QMessageBox.warning(self, "Error", "Failed to identify selected part.")
            return
        database.delete_part(self, part_id)
        
    def editSelectedPart(self):
        index = self.kpcTreeView.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Selection", "No part selected.")
            return
        sourceIndex = self.kpcProxyModel.mapToSource(index)
        part_id = self.kpcModel.getPartId(sourceIndex)
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
        
        self.kpcModel.updateData(updated_parts_data)
        
#Tree View for parts
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
        
class ppapTreeView(QTreeView):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(QHeaderView.Stretch)
        self.setUniformRowHeights(True)
            
    def resizeEvent(self, event):
        super().resizeEvent(event)
        
    def setModel(self, model):
        super().setModel(model)
        
        
#Form for adding or updating a part
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
        
        #No current manufacturing flag
        self.manufacturingCheck = QCheckBox(text="No Current Manufacturing")
        layout.addWidget(self.manufacturingCheck, 1, 4)
        
        # Submit button Button
        addFeatureButton = QPushButton('Add Feature')
        addFeatureButton.clicked.connect(self.addFeature)
        layout.addWidget(addFeatureButton, 5, 1, 1, 3)
        
        addPartButton = QPushButton('Save Part')
        addPartButton.setStyleSheet("background-color: #3ADC73")
        addPartButton.clicked.connect(lambda: functions.submitPart(self))
        layout.addWidget(addPartButton, 6, 0, 1, 5)
        
        cancelButton = QPushButton('Cancel')
        cancelButton.setStyleSheet("background-color: #D6575D")
        cancelButton.clicked.connect(self.closeWindow)
        layout.addWidget(cancelButton, 7, 0, 1, 5)
        
        self.featureTable = QTableWidget()
        self.featureTable.setColumnCount(6)
        self.featureTable.setHorizontalHeaderLabels(["Feature Number", "KPC Designation", "KPC Number", "Operation Number", "Tolerance", "Engine"])
        self.featureTable.horizontalHeader().setStretchLastSection(False)
        for column in range(self.featureTable.columnCount()):
            self.featureTable.horizontalHeader().setSectionResizeMode(column, QHeaderView.Stretch)
            
        layout.addWidget(self.featureTable, 4, 0, 1, 5)
        
        
        self.setLayout(layout)
        
    def addFeature(self):
            self.featureForm = FeatureForm(self)
            self.featureForm.show()
    
    def loadPartData(self, selectedPartData):
        self.partInput.setText(selectedPartData['partNumber'])
        self.revInput.setText(selectedPartData['rev'])
        self.udInput.setText(selectedPartData['uploadDate'])
        self.notesInput.setText(selectedPartData['notes'])
        self.manufacturingCheck.setChecked(selectedPartData.get('currentManufacturing', False))
        
        self.featureTable.setRowCount(0)
        for feature in selectedPartData['features']:
            functions.addFeatureToTable(self, feature)
    
    def closeWindow(self):
        self.close()
        
class ppapPartForm(QWidget):
    partSubmitted = pyqtSignal()
    def __init__(self, mode="add", partId=None):
        super().__init__()
        self.mode = mode
        self.partId = partId
        self.setWindowTitle("Add PPAP Part")
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
        phaseLabel = QLabel('PPAP Package Phase:')
        self.phaseInput = QLineEdit()
        self.phaseInput.setPlaceholderText('Enter PPAP Phase')
        layout.addWidget(phaseLabel, 0, 2)
        layout.addWidget(self.phaseInput, 1, 2)
        
        dueDateLabel = QLabel('PPAP Package Due Date:')
        self.dueDateInput = QLineEdit()
        self.dueDateInput.setPlaceholderText('Enter PPAP Due Date')
        layout.addWidget(dueDateLabel, 0, 3)
        layout.addWidget(self.dueDateInput, 1, 3)
        
        # Notes form
        notesLabel = QLabel('PPAP Number:')
        self.notesInput = QLineEdit()
        self.notesInput.setPlaceholderText('Enter PPAP Number')
        layout.addWidget(notesLabel, 0, 4)
        layout.addWidget(self.notesInput, 1, 4)
        
        self.elementsTable = QTableWidget()
        self.elementsTable.setColumnCount(5)
        self.elementsTable.setHorizontalHeaderLabels(['Element', 'Document', 'Element Submitted?', 'Date Submitted', 'Approval Status'])
        self.elementsTable.horizontalHeader().setStretchLastSection(False)
        for column in range(self.elementsTable.columnCount()):
            self.elementsTable.horizontalHeader().setSectionResizeMode(column, QHeaderView.Stretch)
            
        for i in range(12):
            self.elementsTable.insertRow(i)
        
        self.elementsTable.setItem(0, 0, QTableWidgetItem('Element 1'))
        self.elementsTable.setItem(0, 1, QTableWidgetItem('Design Records'))
        el1Radio = RadioButtonTableWidget()
        self.elementsTable.setCellWidget(0, 2, el1Radio)
            
        layout.addWidget(self.elementsTable, 4, 0, 1, 5)
        
        # Submit button Button
        addFeatureButton = QPushButton('Add Feature')
        addFeatureButton.clicked.connect(self.addFeature)
        layout.addWidget(addFeatureButton, 5, 1, 1, 3)
        
        addPartButton = QPushButton('Save Part')
        addPartButton.setStyleSheet("background-color: #3ADC73")
        addPartButton.clicked.connect(lambda: functions.submitPart(self))
        layout.addWidget(addPartButton, 6, 0, 1, 5)
        
        cancelButton = QPushButton('Cancel')
        cancelButton.setStyleSheet("background-color: #D6575D")
        cancelButton.clicked.connect(self.closeWindow)
        layout.addWidget(cancelButton, 7, 0, 1, 5)        
        
        self.setLayout(layout)
        
    def addFeature(self):
            self.featureForm = FeatureForm(self)
            self.featureForm.show()
    
    def closeWindow(self):
        self.close()
        
        
#Form for uploading data based on part 
class uploadDataForm(QWidget):
    dataSubmitted = pyqtSignal()
    partIdSignal = pyqtSignal(int)
    def __init__(self, partId=None):
        super().__init__()
        self.partId = partId
        self.serialNumberInputs = []
        self.featureTables = []
        self.setWindowTitle("New Data Upload")
        self.resize(800, 600)
        
        layout = QGridLayout()
        
        self.spinner = SpinnerWidget(
            parent=self,
            roundness=100.0,
            fade=61.98,
            radius=25,
            lines=65,
            line_length=13,
            line_width=20,
            speed=0.68,
            color= QColor(34, 130, 255),
            spinner_text='Calculating CPK.\nThis may take a while...',
        )
        
        self.scrollArea = QScrollArea(self)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        layout.addWidget(self.scrollArea, 4, 0, 1, 7)
        
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
        
        runNumberLabel = QLabel('Run Number:')
        self.runNumberInput = QLineEdit()
        self.runNumberInput.setPlaceholderText('Enter Run Number')
        layout.addWidget(runNumberLabel, 1, 0)
        layout.addWidget(self.runNumberInput, 1, 1, 1, 2)
        
        machineLabel = QLabel('Machine:')
        self.machineComboBox = QComboBox()
        self.machineComboBox.addItems([ '', 'CMM - Zeiss Accura'])
        layout.addWidget(machineLabel, 3, 0)
        layout.addWidget(self.machineComboBox, 3, 1)
        
        lotSizeLabel = QLabel('Lot Size:')
        self.lotSizeComboBox = QComboBox()
        self.lotSizeComboBox.addItems(['', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25'])
        layout.addWidget(lotSizeLabel, 3, 4)
        layout.addWidget(self.lotSizeComboBox, 3, 5, 1, 1)
        
        self.serialNumbersLayout = QVBoxLayout()
        layout.addLayout(self.serialNumbersLayout, 4,0,1,7)
        
        self.lotSizeComboBox.currentTextChanged.connect(self.onLotSizeChange)
        
        readPdfButton = QPushButton('Add Data From PDF')
        readPdfButton.setStyleSheet("background-color: #439EF3")
        readPdfButton.clicked.connect(lambda: functions.openPdfFileDialog(self))
        layout.addWidget(readPdfButton, 6, 2, 1, 3)
        
        addPartButton = QPushButton('Save Data')
        addPartButton.setStyleSheet("background-color: #3ADC73")
        addPartButton.clicked.connect(lambda: functions.submitData(self))
        layout.addWidget(addPartButton, 7, 2, 1, 3)
        
        updateCpkButton = QPushButton('Calculate CPK')
        updateCpkButton.setStyleSheet("background-color: #3ADC73")
        updateCpkButton.clicked.connect(lambda: functions.calculateCpk(self))
        layout.addWidget(updateCpkButton, 8, 2, 1, 3)
        
        cancelButton = QPushButton('Cancel')
        cancelButton.setStyleSheet("background-color: #D6575D")
        cancelButton.clicked.connect(self.close)
        layout.addWidget(cancelButton, 9, 2, 1, 3)
        
        self.dataTable = QTableWidget()
        self.dataTable.setColumnCount(5)
        self.dataTable.horizontalHeader().setStretchLastSection(False)
        self.dataTable.setHorizontalHeaderLabels(['Feature Number', 'KPC Number', 'Blueprint Dimension', 'Op Number', 'Measurement'])
        for column in range(self.dataTable.columnCount()):
            self.dataTable.horizontalHeader().setSectionResizeMode(column, QHeaderView.Stretch)
            
        self.setLayout(layout)
        
    def onLotSizeChange(self, text):
        if text.isdigit():
            lot_size = int(text)
            functions.createLotInputs(self, lot_size)
        else:
            functions.clearLotInputs(self)
    
    def loadPartData(self, selectedPartData):
        self.partNumber.setText(selectedPartData['partNumber'])
        self.revLetter.setText(selectedPartData['rev'])
        self.uploadDate.setText(selectedPartData['uploadDate'])
        
        self.dataTable.setRowCount(0)
        self.dataTable.setHorizontalHeaderLabels(['Feature Number', 'KPC Number', 'Blueprint Dimension', 'Op Number', 'Measurement'])
        
    def closeWindow(self):
        self.close()
        
        
##View for previous part upload data
class HistoricalDataView(QWidget):
    def __init__(self, partId=None):
        super().__init__()
        self.partId = partId
        self.setWindowTitle("data Upload History")
        self.resize(800, 600)
        
        layout = QGridLayout()
        
        partLabel = QLabel('Part Number:')
        self.partNumber = QLabel('')
        layout.addWidget(partLabel, 0, 0)
        layout.addWidget(self.partNumber, 0, 1)

        revLabel = QLabel('Revision Letter:')
        self.revLetter = QLabel('')
        layout.addWidget(revLabel, 0, 2)
        layout.addWidget(self.revLetter, 0, 3)
        
        deleteMeasButton = QPushButton('Delete Current Measurement Record')
        deleteMeasButton.setStyleSheet("background-color: #D6575D")
        deleteMeasButton.clicked.connect(self.deleteMeasurement)
        layout.addWidget(deleteMeasButton, 6, 0, 1, 6)
        
        cancelButton = QPushButton('Close Window')
        cancelButton.setStyleSheet("background-color: #D6575D")
        cancelButton.clicked.connect(self.closeWindow)
        layout.addWidget(cancelButton, 7, 0, 1, 6)
        
        self.model = QStandardItemModel()
        self.proxyModel = DateSortProxyModel(dateColumnIndex=0, parent=self)
        self.proxyModel.setSourceModel(self.model)
        self.treeView= QTreeView()
        self.treeView.header().setStretchLastSection(False)
        self.treeView.header().setSectionResizeMode(QHeaderView.Stretch)
        self.model.setHorizontalHeaderLabels(['Upload Date', 'Part Number', 'Serial Number', 'KPC Number', 'Measurement'])
        self.treeView.setModel(self.proxyModel)
        self.treeView.setSortingEnabled(True)
        
            
        layout.addWidget(self.treeView, 4, 0, 1, 6)
        
        
        self.setLayout(layout)
            
        self.close()
        
    def getTolerance(self, selectedPartData, kpcNum):
        for feature in selectedPartData['features']:
            if feature['kpcNum'] == kpcNum:
                return feature['tol']
        return "N/A"
    
    def deleteMeasurement(self):
        index = self.treeView.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "No measurement selected.")
            return
        
        sourceIndex = self.proxyModel.mapToSource(index)
        uploadDate = self.model.itemFromIndex(sourceIndex.siblingAtColumn(0)).text()
        stripped_date = datetime.strptime(uploadDate, '%m/%d/%Y')
        formatted_date = datetime.strftime(stripped_date, '%m/%d/%y')
        serialNumber = self.model.itemFromIndex(sourceIndex.siblingAtColumn(1)).text()
        
        if uploadDate and serialNumber:
            partNumber = self.partNumber.text()
            result = database.delete_measurement_by_id(self, partNumber, serialNumber, formatted_date)
            if result > 0:
                self.currentRow = sourceIndex.row()
                self.refreshTreeView()
        else: 
            QMessageBox.warning(self, "Error", "Could not retrieve data.")
    
    def loadPartData(self, selectedPartData, selectedPartUploadData):
        self.partNumber.setText(selectedPartData['partNumber'])
        self.revLetter.setText(selectedPartData['rev'])
        
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Upload Date','Serial Number', 'KPC Number', 'Blueprint Requirement', 'Measurement'])
        self.treeView.sortByColumn(0, Qt.AscendingOrder)
        
        for uploadData in selectedPartUploadData:
            uploadDate = uploadData['uploadDate']
            formatted_date = functions.format_date(uploadDate)
            serialNumber = uploadData['serialNumber']
            
            parentRow = [
                QStandardItem(formatted_date),
                QStandardItem(serialNumber),
                QStandardItem(""),
                QStandardItem("")
            ]
            self.model.appendRow(parentRow)
            
            if 'measurements' in uploadData:
            
                for measurement in uploadData['measurements']:
                    kpcNum = measurement['kpcNum']
                    meas = measurement['measurement']
                    tolerance = self.getTolerance(selectedPartData, kpcNum)
                    childRow = [
                        QStandardItem(""),
                        QStandardItem(""),
                        QStandardItem(kpcNum),
                        QStandardItem(tolerance),
                        QStandardItem(meas)
                    ]
                    parentRow[0].appendRow(childRow)
        self.model.layoutChanged.emit()
                    
    def refreshTreeView(self):
        part_id = self.partId
        selectedPartData = database.get_part_by_id(part_id)
        selectedPartUploadData = database.get_measurements_by_id(part_id)
        currentSortColumn = self.treeView.header().sortIndicatorSection()
        currentSortOrder = self.treeView.header().sortIndicatorOrder()
        
        self.loadPartData(selectedPartData, selectedPartUploadData)
        
        if hasattr(self, 'currentRow'):
            rowCount = self.model.rowCount()
            if rowCount > 0:
                newRowIndex = min(self.currentRow, rowCount - 1)
                newIndex = self.model.index(newRowIndex, 0)
                mappedIndex = self.proxyModel.mapFromSource(newIndex)
                self.treeView.setCurrentIndex(mappedIndex)
                print(mappedIndex.row(), mappedIndex.column())
                self.treeView.scrollTo(mappedIndex, 5)
        
        self.treeView.header().setSortIndicator(currentSortColumn, currentSortOrder)
        self.treeView.sortByColumn(currentSortColumn, currentSortOrder)
        
    def closeWindow(self):
        self.close()
        
        
##Dashboard display for CPK Data
class CpkDashboardView(QWidget):
    def __init__(self, partId=None):
        super().__init__()
        self.partId = partId
        self.setWindowTitle("CPK Dashboard")
        self.resize(1200, 800)
        
        layout = QGridLayout()
        
        partLabel = QLabel('Part Number:')
        self.partNumber = QLabel('')
        layout.addWidget(partLabel, 0, 0)
        layout.addWidget(self.partNumber, 0, 1)

        revLabel = QLabel('Revision Letter:')
        self.revLetter = QLabel('')
        layout.addWidget(revLabel, 0, 2)
        layout.addWidget(self.revLetter, 0, 3)
        
        cpkLabel = QLabel('CPK:')
        self.cpkDisplay= QLabel('')
        layout.addWidget(cpkLabel, 0, 4)
        layout.addWidget(self.cpkDisplay, 0, 5)
        
        kpcLabel = QLabel('KPC:')
        layout.addWidget(kpcLabel, 0, 6)
        
        self.kpcComboBox = QComboBox()
        layout.addWidget(self.kpcComboBox, 0, 7)
        self.kpcComboBox.currentIndexChanged.connect(self.updateGraph)
        
        kpcLabel = QLabel('Data:')
        layout.addWidget(kpcLabel, 0, 8)
        
        self.dataRangeComboBox = QComboBox()
        self.dataRangeComboBox.addItems(['Last', 'First', 'All'])
        layout.addWidget(self.dataRangeComboBox, 0, 9)
        self.dataRangeComboBox.currentIndexChanged.connect(self.updateGraph)
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas, 4, 0, 1, 10)
        
        cancelButton = QPushButton('Close Window')
        cancelButton.setStyleSheet("background-color: #D6575D")
        cancelButton.clicked.connect(self.closeWindow)
        layout.addWidget(cancelButton, 7, 0, 1, 10)
        
        self.setLayout(layout)
        
        self.selectedPartUploadData = []
        self.selectedPartData = []
        
    def loadPartData(self, selectedPartData, selectedPartUploadData):
        if isinstance(selectedPartData, list):
            self.selectedPartData = selectedPartData[0]
        else: 
            self.selectedPartData = selectedPartData
            
        self.partNumber.setText(selectedPartData['partNumber'])
        self.revLetter.setText(selectedPartData['rev'])
        kpcs = {measurement['kpcNum'] for data in selectedPartUploadData for measurement in data['measurements']}
        self.kpcComboBox.addItems(sorted(kpcs))
        self.selectedPartUploadData = selectedPartUploadData
        self.selectedPartData = selectedPartData
        if self.kpcComboBox.count() > 0:
            self.kpcComboBox.setCurrentIndex(0)
            self.updateGraph()
        
    def updateGraph(self):
        kpcNum = self.kpcComboBox.currentText()
        if not kpcNum:
            return
        dataRange = self.dataRangeComboBox.currentText()
        tolerance = None
        cpk_value = self.getCpkValue(kpcNum)
        self.cpkDisplay.setText(f'{cpk_value}' if cpk_value is not None else 'N/A')
        
        for feature in self.selectedPartData['features']:
            if feature['kpcNum'] == kpcNum:
                tolerance = feature['tol']
                break
        
        if tolerance:
            lower_tolerance, upper_tolerance = functions.parse_tolerance(tolerance)
        else:
            lower_tolerance, upper_tolerance = None, None
            
        dates_measurements = [
            (datetime.strptime(data['uploadDate'], '%m/%d/%Y'), float(measurement['measurement']))
            for data in self.selectedPartUploadData
            for measurement in data['measurements']
            if measurement['kpcNum'] == kpcNum
        ]
        
        if not dates_measurements:
            return
        
        dates_measurements.sort(key=lambda x: x[0])
        
        if dataRange == 'Last':
            dates_measurements = dates_measurements[-20:]
        elif dataRange == 'First':
            dates_measurements = dates_measurements[:20]
                    
        x_values = [i for i, _ in enumerate(dates_measurements)]
        measurements = [dm[1] for dm in dates_measurements]
        dates = [dm[0].strftime("%m/%d/%Y") for dm in dates_measurements]
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        ax.plot(x_values, measurements, marker='o')
        ax.set_xticks(x_values)
        ax.set_xticklabels(dates, rotation=45, ha='right')
    
        ax.set_title(f'Measurement Data Trends for KPC {kpcNum} {tolerance}')
        ax.set_xlabel('Upload Date')
        ax.set_ylabel("Measurement Value")
        
        if lower_tolerance is not None and upper_tolerance is not None:
            ax.axhline(y=lower_tolerance, color='g', linestyle='--', label='Lower Tolerance')
            ax.axhline(y=upper_tolerance, color='b', linestyle='--', label='Upper Tolerance')
            
        cursor = mplcursors.cursor(hover=True)
        @cursor.connect("add")
        def on_add(sel):
            idx = sel.target.index
            data_point = dates_measurements[idx]
            self.annotation.set_text(
                f"Date: {data_point[0].strftime('%m/%d/%Y')}"
                f"Measurement: {data_point[1]}"
                f"Serial Number: {data_point[2]}"
            )
            
            sel.annotation.get_bbox_patch().set_alpha(0.8)
            
        ax.grid(True)
        self.canvas.draw()
        
    def getCpkValue(self, kpcNum):
        for feature in self.selectedPartData['features']:
            if feature['kpcNum'] == kpcNum:
                return feature.get('cpk', None)
        return None
        
    def getTolerance(self, selectedPartData, kpcNum):
        for feature in selectedPartData['features']:
            if feature['kpcNum'] == kpcNum:
                return feature['tol']
        return "N/A"
        
    def closeWindow(self):
        self.close()


#Form for adding features when adding a new part 
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
        
        opNumLabel = QLabel('Op Number:')
        self.opNumInput = QLineEdit()
        self.opNumInput.setPlaceholderText('Enter Op Number')
        layout.addWidget(opNumLabel, 0, 2)
        layout.addWidget(self.opNumInput, 1, 2)
        
        # upload date form
        kpcNumLabel = QLabel('KPC Number:')
        self.kpcNumInput = QLineEdit()
        self.kpcNumInput.setPlaceholderText('Enter KPC Number from Net-Inspect')
        layout.addWidget(kpcNumLabel, 0, 3)
        layout.addWidget(self.kpcNumInput, 1, 3)
        
        # Notes form
        requirementLabel = QLabel('Requirement:')
        self.requirementInput = QLineEdit()
        self.requirementInput.setPlaceholderText('Enter Blueprint Requirement')
        layout.addWidget(requirementLabel, 0, 4)
        layout.addWidget(self.requirementInput, 1, 4)
        
        engineLabel = QLabel('Engine:')
        self.engineInput = QLineEdit()
        self.engineInput.setPlaceholderText('Enter Part Engine Program')
        layout.addWidget(engineLabel, 0, 45)
        layout.addWidget(self.engineInput, 1, 5)
        
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
            "opNum": self.opNumInput.text(),
            "kpcNum": self.kpcNumInput.text(),
            "tol": self.requirementInput.text(),
            "engine": self.engineInput.text(),
        }
        if self.parent:
            self.parent.addFeatureToTable(feature_data)
            
        self.close()
        
    def closeWindow(self):
        self.close()
        
class GageRRForm(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Gage R&R")
        self.resize(800, 600)
        
        layout = QGridLayout()
        
        # Part number form 
        partLabel = QLabel('Part Number:')
        self.partInput = QLabel()
        layout.addWidget(partLabel, 0, 0)
        layout.addWidget(self.partInput, 1, 0)
        
        # Part revision form
        revLabel = QLabel('Revision Letter:')
        self.revInput = QLabel()
        layout.addWidget(revLabel, 0, 1)
        layout.addWidget(self.revInput, 1, 1)
        
        # upload date form
        udLabel = QLabel('Last Net-Inspect Upload Date:')
        self.udInput = QLabel()
        layout.addWidget(udLabel, 0, 2)
        layout.addWidget(self.udInput, 1, 2)
        
    def loadPartData(self, selectedPartData):
        self.partInput.setText(selectedPartData['partNumber'])
        self.revInput.setText(selectedPartData['rev'])
        self.udInput.setText(selectedPartData['uploadDate'])
        
        self.featureTable.setRowCount(0)
        for feature in selectedPartData['features']:
            functions.addFeatureToTable(self, feature)

class KPCSummaryWind(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("KPC Summary Window")
        self.resize(1200, 800)
        
        layout = QGridLayout()
        
        self.kpcTable = QTableWidget()
        self.kpcTable.setColumnCount(8)
        self.kpcTable.setHorizontalHeaderLabels(['Part Number', 'KPC Number', 'Dimension', 'Last Data Upload Date', 'CPK Value', 'Management Form Number', 'Management Form Upload Date', 'Management Form Expiration Date'])
        for column in range(self.kpcTable.columnCount()):
            self.kpcTable.horizontalHeader().setSectionResizeMode(column, QHeaderView.Stretch)
        self.kpcTable.horizontalHeader().setStretchLastSection(False)
        self.kpcTable.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
                
        functions.addKPCToTable(self)
            
        layout.addWidget(self.kpcTable, 4, 0, 1, 5)
        self.setLayout(layout)
        
        
class ManagementFormWind(QWidget):
    def __init__(self, partId = None):
        super().__init__()
        
        self.partId = partId
        self.setWindowTitle("KPC Management Forms")
        self.resize(1000, 600)
        
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

        # Submit button Button
        addFeatureButton = QPushButton('Add Management Form')
        addFeatureButton.clicked.connect(self.addForm)
        layout.addWidget(addFeatureButton, 5, 1, 1, 3)
        
        cancelButton = QPushButton('Cancel')
        cancelButton.setStyleSheet("background-color: #D6575D")
        cancelButton.clicked.connect(self.closeWindow)
        layout.addWidget(cancelButton, 7, 0, 1, 5)
        
        self.featureTable = QTableWidget()
        self.featureTable.setColumnCount(10)
        self.featureTable.setHorizontalHeaderLabels(["Select KPC", "Feature Number", "KPC Designation", "KPC Number", "Operation Number", "Tolerance", "CPK", "Management Form Number", "Management Form Upload Date", "Management Form Expiration Date"])
        self.featureTable.horizontalHeader().setStretchLastSection(False)
        for column in range(self.featureTable.columnCount()):
            self.featureTable.horizontalHeader().setSectionResizeMode(column, QHeaderView.Stretch)
        self.featureTable.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
        layout.addWidget(self.featureTable, 4, 0, 1, 6)
        
        
        self.setLayout(layout)
        
    def addForm(self):
        self.addForm = ManagementFormAdd(self)
        self.addForm.show()
        
    def loadPartData(self, selectedPartData):
        self.partNumber.setText(selectedPartData['partNumber'])
        self.revLetter.setText(selectedPartData['rev'])
        self.uploadDate.setText(selectedPartData['uploadDate'])
        
        self.featureTable.setRowCount(0)
        for feature in selectedPartData['features']:
            functions.addFeatureToFormTable(self, feature)
        
    def closeWindow(self):
        self.close()
        
class ManagementFormAdd(QWidget):
    def __init__(self, mode='add'):
        super().__init__()
        self.setWindowTitle("Add Management Form")
        self.resize(800, 600)
        
        self.mode = mode
        
        layout = QGridLayout()
        
        # Part number form 
        formLabel = QLabel('Management Form Number:')
        self.formInput = QLineEdit()
        self.formInput.setPlaceholderText('Enter form number')
        layout.addWidget(formLabel, 0, 0)
        layout.addWidget(self.formInput, 1, 0)
        
        # Part revision form
        udLabel = QLabel('Management Form Upload Date:')
        udIcon = fugue.icon('calendar-blue')
        self.udButton = QPushButton()
        self.udButton.setIcon(QIcon(udIcon))
        self.udButton.clicked.connect(self.uploadCal)
        layout.addWidget(udLabel, 0, 1)
        layout.addWidget(self.udButton, 1, 1)
        
        # upload date form
        ddLabel = QLabel('Management Form Expiration Date:')
        ddIcon = fugue.icon('calendar-select')
        self.ddButton = QPushButton()
        self.ddButton.setIcon(ddIcon)
        self.ddButton.clicked.connect(self.dueCal)
        layout.addWidget(ddLabel, 0, 2)
        layout.addWidget(self.ddButton, 1, 2)
        
        self.featureTable = QTableWidget()
        self.featureTable.setColumnCount(2)
        self.featureTable.setHorizontalHeaderLabels([ "KPC Number", "Tolerance"])
        self.featureTable.horizontalHeader().setStretchLastSection(False)
        for column in range(self.featureTable.columnCount()):
            self.featureTable.horizontalHeader().setSectionResizeMode(column, QHeaderView.Stretch)
        self.featureTable.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Notes form
        notesLabel = QLabel('Notes:')
        self.notesInput = QLineEdit()
        self.notesInput.setPlaceholderText('Enter notes')
        layout.addWidget(notesLabel, 0, 3)
        layout.addWidget(self.notesInput, 1, 3)
        
        # Submit button Button
        addFeatureButton = QPushButton('Add Feature')
        addFeatureButton.clicked.connect(self.addFeature)
        layout.addWidget(addFeatureButton, 5, 1, 1, 3)
        
        self.setLayout(layout)
        
    def addFeature(self):
        print('feature')
        
    def uploadCal(self):
        self.uploadCalendar = QCalendarWidget(self)
        self.uploadCalendar.show()
        
    def dueCal(self):
        self.dueCalendar = QCalendarWidget(self)
        self.dueCalendar.show()
