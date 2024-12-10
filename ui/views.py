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
        self.resize(1400, 800)
        
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
        self.ppap_data = database.get_all_ppap_data()
        self.ppapModel = PpapDataModel(self.ppap_data)
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
        
        self.manForm = ManagementFormWind(partId=part_id)
        self.manForm.loadPartData()
        self.manForm.show()
        
    def openPpapPartForm(self):
        self.partForm = ppapPartForm()
        self.partForm.ppapSubmitted.connect(self.refreshPpapView)
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
        
    def refreshPpapView(self):
        updated_ppap_data = database.get_all_ppap_data()
        
        self.ppapModel.updateData(updated_ppap_data)
        
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
    ppapSubmitted = pyqtSignal()
    def __init__(self, mode="add", partId=None):
        super().__init__()
        self.mode = mode
        self.partId = partId
        self.setWindowTitle("Add PPAP Part")
        self.resize(1000, 600)
        
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
        
        # Notes form
        ppapNumLabel = QLabel('PPAP Number:')
        self.ppapInput = QLineEdit()
        self.ppapInput.setPlaceholderText('Enter PPAP Number')
        layout.addWidget(ppapNumLabel, 0, 2)
        layout.addWidget(self.ppapInput, 1, 2)
        
        # upload date form
        phaseLabel = QLabel('PPAP Package Phase:')
        self.phaseInput = QLineEdit()
        self.phaseInput.setPlaceholderText('Enter PPAP Phase')
        layout.addWidget(phaseLabel, 0, 3)
        layout.addWidget(self.phaseInput, 1, 3)
        
        dueDateLabel = QLabel('Interim B Commit:')
        intBDate = date.today() + timedelta(days=365)
        self.intBBox = QDateEdit(intBDate)
        self.intBCheck = QCheckBox('Interim B Complete', self)
        self.intBCheck.stateChanged.connect(self.toggleIntBDate)
        layout.addWidget(dueDateLabel, 0, 4)
        layout.addWidget(self.intBBox, 1, 4)
        layout.addWidget(self.intBCheck, 1, 5)
        
        dueDateLabel = QLabel('Interim A Commit:')
        intADate = date.today() + timedelta(days=730)
        self.intABox = QDateEdit(intADate)
        self.intACheck = QCheckBox('Interim A Complete', self)
        self.intACheck.stateChanged.connect(self.toggleIntADate)
        layout.addWidget(dueDateLabel, 0, 6)
        layout.addWidget(self.intABox, 1, 6)
        layout.addWidget(self.intACheck, 1, 7)
        
        dueDateLabel = QLabel('Full Approval:')
        fullDate = date.today() + timedelta(days=1095)
        self.fullBox = QDateEdit(fullDate)
        self.fullCheck = QCheckBox('Full Approval Complete', self)
        self.fullCheck.stateChanged.connect(self.toggleFullDate)
        layout.addWidget(dueDateLabel, 0, 8)
        layout.addWidget(self.fullBox, 1, 8)
        layout.addWidget(self.fullCheck, 1, 9)
        
        self.elementsTable = QTableWidget()
        self.elementsTable.setColumnCount(9)
        self.elementsTable.setHorizontalHeaderLabels(['Element', 'Document', 'Element Submitted?', 'Date Submitted', 'Approval Status', 'Interim B', 'Interim A', 'Full Approval', 'Notes'])
        self.elementsTable.horizontalHeader().setStretchLastSection(False)
        for column in range(self.elementsTable.columnCount()):
            self.elementsTable.horizontalHeader().setSectionResizeMode(column, QHeaderView.Stretch)
        self.elementsTable.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
        elements = [
            ('Element 1', 'Design Records'),
            ('Element 2', 'Design Risk Analysis (IDS)'),
            ('Element 3', 'Process Flow Diagram'),
            ('Element 4', 'Process Failure Mode and Effects Analysis (PFMEA)'),
            ('Element 5', 'Control Plan'),
            ('Element 6', 'Measurement Systems Analysis (MSA)'),
            ('Element 7', 'Initial Process Capability Studies'),
            ('Element 8', 'Packaging, Preservation, and Labeling Approvals'),
            ('Element 9', 'First Article Inspection Report'),
            ('Element 10.1', 'Part Marking Approval'),
            ('Element 10.2', 'Production Process Run(s)'),
            ('Element 11', 'PPAP Approval')
        ]
            
        for i, (el, elName) in enumerate(elements):
            self.elementsTable.insertRow(i)
            self.elementsTable.setItem(i, 0, QTableWidgetItem(el))
            self.elementsTable.setItem(i, 1, QTableWidgetItem(elName))
            elRadio = RadioButtonTableWidget()
            elRadio.stateChanged.connect(self.changeStatus)
            self.elementsTable.setCellWidget(i, 2, elRadio)
            
        layout.addWidget(self.elementsTable, 4, 0, 1, 10)
        
        addPartButton = QPushButton('Save Part')
        addPartButton.setStyleSheet("background-color: #3ADC73")
        addPartButton.clicked.connect(lambda: functions.submitPPAPPart(self))
        layout.addWidget(addPartButton, 5, 2, 1, 7)
        
        cancelButton = QPushButton('Cancel')
        cancelButton.setStyleSheet("background-color: #D6575D")
        cancelButton.clicked.connect(self.closeWindow)
        layout.addWidget(cancelButton, 6, 2, 1, 7)        
        
        self.setLayout(layout)
        
    def changeStatus(self, state):
        sender = self.sender()
        
        if not state:
            for row in range(self.elementsTable.rowCount()):
                widget = self.elementsTable.cellWidget(row, 2)
                if widget == sender:
                    item = QTableWidgetItem('N/A')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.elementsTable.setItem(row, 3, item)
                    break
            
        
    def toggleIntBDate(self, state):
        if state == Qt.Checked:
            self.intBBox.setEnabled(False)
        else:
            self.intBBox.setEnabled(True)
            
    def toggleIntADate(self, state):
        if state == Qt.Checked:
            self.intBBox.setEnabled(False)
            self.intBCheck.setChecked(True)
            self.intABox.setEnabled(False)
        else:
            self.intBBox.setEnabled(True)
            self.intBCheck.setChecked(False)
            self.intABox.setEnabled(True)
        
    def toggleFullDate(self, state):
        if state == Qt.Checked:
            self.intBBox.setEnabled(False)
            self.intBCheck.setChecked(True)
            self.intABox.setEnabled(False)
            self.intACheck.setChecked(True)
            self.fullBox.setEnabled(False)
        else:
            self.intBBox.setEnabled(True)
            self.intBCheck.setChecked(False)
            self.intABox.setEnabled(True)
            self.intACheck.setChecked(False)
            self.fullBox.setEnabled(True)
        
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
        if feature_data:
            functions.addFeatureToTable(self.parent, feature_data)
            
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
        self.selectedKpcs = []
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
        layout.addWidget(addFeatureButton, 5, 1, 1, 4)
        
        viewFormButton = QPushButton('View Management Form for Selected KPC')
        viewFormButton.clicked.connect(self.viewForm)
        layout.addWidget(viewFormButton, 6, 1, 1, 4)
        
        
        cancelButton = QPushButton('Cancel')
        cancelButton.setStyleSheet("background-color: #D6575D")
        cancelButton.clicked.connect(self.closeWindow)
        layout.addWidget(cancelButton, 7, 1, 1, 4)
        
        self.featureTable = QTableWidget()
        self.featureTable.setColumnCount(12)
        self.featureTable.setHorizontalHeaderLabels(["Select KPC", "Feature Number", "KPC Designation", "KPC Number", "Operation Number", "Tolerance", "CPK", "Management Form Number", "Management Form Upload Date", "Milestone 2 Target Date", "Milestone 3 Target Date", "Milestone 4 Target Date"])
        self.featureTable.horizontalHeader().setStretchLastSection(False)
        for column in range(self.featureTable.columnCount()):
            self.featureTable.horizontalHeader().setSectionResizeMode(column, QHeaderView.Stretch)
        self.featureTable.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
        layout.addWidget(self.featureTable, 4, 0, 1, 6)
        
        
        self.setLayout(layout)
        
    def addForm(self):
        self.selectedKpcs.clear()
        
        for row in range(self.featureTable.rowCount()):
            checkbox = self.featureTable.cellWidget(row, 0)
            if checkbox is not None and checkbox.isChecked():
                kpc_number = self.featureTable.item(row, 3).text()
                tolerance = self.featureTable.item(row, 5).text()
                self.selectedKpcs.append((kpc_number, tolerance))
                
        self.addForm = ManagementFormAdd(self, self.partId, self.selectedKpcs)
        self.addForm.formSubmitted.connect(self.loadPartData)
        self.addForm.show()
        
    def viewForm(self):
        self.selectedKpcs.clear()
        formData = database.get_form_by_pn(self.partId)
        
        all_kpcs = {}
        for form in formData:
            formNumber = form.get('formNumber')
            for kpc in form['kpcs']:
                all_kpcs[kpc] = formNumber
                
        selectedFormNumbers = set()
            
        for row in range(self.featureTable.rowCount()):
            checkbox = self.featureTable.cellWidget(row, 0)
            if checkbox is not None and checkbox.isChecked():
                kpc_number = self.featureTable.item(row, 3).text()
                tolerance = self.featureTable.item(row, 5).text()
                self.selectedKpcs.append((kpc_number, tolerance))
                
                if kpc_number in all_kpcs:
                    selectedFormNumbers.add(all_kpcs[kpc_number])
                else:
                    QMessageBox.warning(self, "Error", "No management form found for this KPC")
                    return
        
            if len(selectedFormNumbers) > 1:
                QMessageBox.warning(self, "Error", "Selected KPCs belong to different management forms.")
                return
                    
        self.addForm = ManagementFormAdd(self, self.partId, self.selectedKpcs)
        self.addForm.formSubmitted.connect(self.loadPartData)
        self.addForm.loadForm(self.selectedKpcs)
        self.addForm.show()
        
    def loadPartData(self):
        formData = database.get_form_by_pn(self.partId)
        selectedPartData = database.get_part_by_id(self.partId)
        print('form data')
        print(formData)
        print('Part data')
        print(selectedPartData)
        self.partNumber.setText(selectedPartData['partNumber'])
        self.revLetter.setText(selectedPartData['rev'])
        self.uploadDate.setText(selectedPartData['uploadDate'])
        
        self.featureTable.setRowCount(0)
        for feature in selectedPartData['features']:
            if formData:
                for data in formData:
                    if feature['kpcNum'] in data['kpcs']:
                        print(data)
                        if data['ms2Date'] and data['ms3Date']:
                            feature['formNumber'] = data['formNumber']
                            feature['uploadDate'] = data['uploadDate']
                            feature['ms2Date'] = data['ms2Date']
                            feature['ms3Date'] = data['ms3Date']
                            feature['ms4Date'] = data['ms4Date']
                        elif data['ms3Date']:
                            feature['formNumber'] = data['formNumber']
                            feature['uploadDate'] = data['uploadDate']
                            feature['ms3Date'] = data['ms3Date']
                            feature['ms4Date'] = data['ms4Date']
                        else:
                            feature['formNumber'] = data['formNumber']
                            feature['uploadDate'] = data['uploadDate']
                            feature['ms4Date'] = data['ms4Date']
                functions.addFeatureToFormTable(self, feature)
            else:
                functions.addFeatureToFormTable(self, feature)
            
    def handleItemClicked(self, item):
        if item.checkState() == Qt.Checked:
            self.selectedKpcs.append(item.row())
            print(self.selectedKpcs)
        
    def closeWindow(self):
        self.close()
        
class ManagementFormAdd(QWidget):
    formSubmitted = pyqtSignal()
    def __init__(self, parent, partId, selectedKpcs, mode='add'):
        super().__init__()
        self.setWindowTitle("Management Form")
        self.resize(800, 600)
        
        self.mode = mode
        self.partId = partId
        self.selectedKpcs = selectedKpcs
        
        layout = QGridLayout()
        
        # Part number form 
        formLabel = QLabel('Form Number:')
        self.formInput = QLineEdit()
        self.formInput.setPlaceholderText('Enter form number')
        layout.addWidget(formLabel, 0, 0)
        layout.addWidget(self.formInput, 0, 1)
        
        # Part revision form
        udLabel = QLabel('Upload Date:')
        self.udBox = QDateEdit(date.today())
        layout.addWidget(udLabel, 0, 2)
        layout.addWidget(self.udBox, 0, 3)
        
        ms2Label = QLabel('Milestone 2 Target Date:')
        ms2Date = date.today() + timedelta(days=365)
        self.ms2Box = QDateEdit(ms2Date)
        self.ms2Check = QCheckBox('Milestone 2 Complete', self)
        self.ms2Check.stateChanged.connect(self.toggleMs2Date)
        layout.addWidget(ms2Label, 0, 4)
        layout.addWidget(self.ms2Box, 0, 5)
        layout.addWidget(self.ms2Check, 0, 6)
        
        # upload date form
        ms3Label = QLabel('Milestone 3 Target Date:')
        ms3Date = date.today() + timedelta(days=365)
        self.ms3Box = QDateEdit(ms3Date)
        self.ms3Check = QCheckBox('Milestone 3 Complete', self)
        self.ms3Check.stateChanged.connect(self.toggleMs3Date)
        layout.addWidget(ms3Label, 0, 7)
        layout.addWidget(self.ms3Box, 0, 8)
        layout.addWidget(self.ms3Check, 0, 9)
        
        ms4Label = QLabel('Milestone 4 Target Date:')
        ms4Date = date.today() + timedelta(days=365)
        self.ms4Box = QDateEdit(ms4Date)
        layout.addWidget(ms4Label, 0, 10)
        layout.addWidget(self.ms4Box, 0, 11)
        
        self.featureTable = QTableWidget()
        self.featureTable.setColumnCount(2)
        self.featureTable.setHorizontalHeaderLabels([ "KPC Number", "Tolerance"])
        self.featureTable.horizontalHeader().setStretchLastSection(False)
        for column in range(self.featureTable.columnCount()):
            self.featureTable.horizontalHeader().setSectionResizeMode(column, QHeaderView.Stretch)
        self.featureTable.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.addKpcToTable()
        layout.addWidget(self.featureTable, 3, 0, 3, 7)
        
        # Notes form
        self.notesInput = QTextEdit()
        self.notesInput.setPlaceholderText('Enter Management form process change')
        layout.addWidget(self.notesInput, 3, 7, 3, 5)
        
        # Submit button Button
        self.addFeatureButton = QPushButton('Add Form')
        self.addFeatureButton.clicked.connect(self.saveForm)
        layout.addWidget(self.addFeatureButton, 7, 0, 1, 12)
        
        self.setLayout(layout)
        
    def addKpcToTable(self):        
        if self.selectedKpcs:
            print(self.selectedKpcs)
            for i, (kpc, tol) in enumerate(self.selectedKpcs):
                row_position = self.featureTable.rowCount()
                self.featureTable.insertRow(row_position)
                self.featureTable.setItem(row_position, 0, QTableWidgetItem(str(kpc)))
                self.featureTable.setItem(row_position, 1, QTableWidgetItem(str(tol)))
                
    def loadForm(self, selectedKpcs):
        print(selectedKpcs)
        formData = database.get_form_by_pn(self.partId)
        partData = database.get_part_by_id(self.partId)
        
        loaded_kpcs = set(kpc for kpc, _ in selectedKpcs)
        
        for data in formData:
            for kpc, tol in selectedKpcs:
                if kpc in data['kpcs']:
                    for feature in partData['features']:
                        if feature['kpcNum'] not in loaded_kpcs and feature['kpcNum'] in data['kpcs']:
                            row_position = self.featureTable.rowCount()
                            self.featureTable.insertRow(row_position)
                            self.featureTable.setItem(row_position, 0, QTableWidgetItem(str(feature['kpcNum'])))
                            self.featureTable.setItem(row_position, 1, QTableWidgetItem(str(feature['tol'])))
                            loaded_kpcs.add(feature['kpcNum'])
                    uploadDate = datetime.strptime(data['uploadDate'], '%m/%d/%Y')
                    ms4Date = datetime.strptime(data['ms4Date'], '%m/%d/%Y')
                    self.formInput.setText(data['formNumber'])
                    self.formInput.setReadOnly(True)
                    self.udBox.setDate(QDate(uploadDate))
                    self.udBox.setReadOnly(True)
                    self.ms4Box.setDate(QDate(ms4Date))
                    self.ms4Box.setReadOnly(True)
                    self.notesInput.setText(data['formText'])
                    self.notesInput.setReadOnly(True)
                    self.addFeatureButton.hide()
                    if data['ms2Date']:
                        ms2Date = datetime.strptime(data['ms2Date'], '%m/%d/%Y')
                        self.ms2Box.setDate(ms2Date)
                    else:
                        self.ms2Check.setChecked(True)
                    if data['ms3Date']:
                        ms3Date = datetime.strptime(data['ms3Date'], '%m/%d/%Y')
                        self.ms3Box.setDate(ms3Date)
                    else:
                        self.ms3Check.setChecked(True)
                
                
        
    def saveForm(self):
        formNum = self.formInput.text().strip()
        formLText = self.notesInput.toPlainText()
        if not formNum:
            QMessageBox.warning(self, "Error", "You must enter a form number.")
            return
        elif not formLText:
            QMessageBox.warning(self, "Error", "Please enter process changes made.")
            return
        
        if self.ms2Check.isChecked() and self.ms3Check.isChecked():
            formData = {
                'partNumber': self.partId,
                'formNumber': formNum,
                'uploadDate': self.udBox.text(),
                'ms2Date': None,
                'ms3Date': None,
                'ms4Date': self.ms4Box.text(),
                'formText': formLText,
                'kpcs': []
            }
        elif self.ms2Check.isChecked():
            formData = {
                'partNumber': self.partId,
                'formNumber': formNum,
                'uploadDate': self.udBox.text(),
                'ms2Date': None,
                'ms3Date': self.ms3Box.text(),
                'ms4Date': self.ms4Box.text(),
                'formText': formLText,
                'kpcs': []
            }
        else:
            formData = {
                'partNumber': self.partId,
                'formNumber': formNum,
                'uploadDate': self.udBox.text(),
                'ms2Date': self.ms2Box.text(),
                'ms3Date': self.ms3Box.text(),
                'ms4Date': self.ms4Box.text(),
                'formText': formLText,
                'kpcs': []
            }
            
        for kpc, tol in self.selectedKpcs:
            formData['kpcs'].append(kpc)
        
        database.add_management_form(formData, callback=self.onSubmitSuccess)
        
        self.close()
        
    def toggleMs2Date(self, state):
        if state == Qt.Checked:
            self.ms2Box.setEnabled(False)
        else:
            self.ms2Box.setEnabled(True)
    def toggleMs3Date(self, state):
        if state == Qt.Checked:
            self.ms2Box.setEnabled(False)
            self.ms2Check.setChecked(True)
            self.ms3Box.setEnabled(False)
        else:
            self.ms2Box.setEnabled(True)
            self.ms2Check.setChecked(False)
            self.ms3Box.setEnabled(True)
        
    def onSubmitSuccess(self, isSuccess):
        if isSuccess:
            self.formSubmitted.emit()
