import shutil
import re
from openpyxl import load_workbook
from utils import database, functions
import mplcursors
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from .models import (
    PartFeaturesModel,
    DateSortProxyModel
    )
from datetime import (
    datetime, 
    timedelta, 
    date
    )
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import (
    QStandardItemModel, 
    QStandardItem
)

#Main window view of application
class DashboardView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KPC Manager")
        self.resize(1200, 800)
        
        self.mainWidget = QWidget(self)
        self.mainLayout = QVBoxLayout()
        
        self.tree_view = PartTreeView(self)
        self.part_data = database.get_all_data()
        self.model = PartFeaturesModel(self.part_data)
        self.proxyModel = QSortFilterProxyModel(self)
        self.proxyModel.setSourceModel(self.model)
        self.tree_view.setModel(self.proxyModel)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.sortByColumn(3, Qt.AscendingOrder)
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
        
        self.showHistoricalUploads = QPushButton('Show Past Data Uploads for selected Part')
        self.showHistoricalUploads.setStyleSheet("background-color: #439EF3")
        self.showHistoricalUploads.clicked.connect(self.openHistoricalUploadWindow)
        self.mainLayout.addWidget(self.showHistoricalUploads)
        
        self.showCpkData = QPushButton('Show CPK Data for selected Part')
        self.showCpkData.setStyleSheet("background-color: #439EF3")
        self.showCpkData.clicked.connect(self.openCpkDashboard)
        self.mainLayout.addWidget(self.showCpkData)
        
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
        sourceIndex = self.proxyModel.mapToSource(index)
        part_id = self.model.getPartId(sourceIndex)
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
        index = self.tree_view.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "No part selected.")
            return
        sourceIndex = self.proxyModel.mapToSource(index)
        part_id = self.model.getPartId(sourceIndex)
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
        index = self.tree_view.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "No part selected.")
            return
        sourceIndex = self.proxyModel.mapToSource(index)
        part_id = self.model.getPartId(sourceIndex)
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
        index = self.tree_view.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Selection", "No part selected.")
            return
        sourceIndex = self.proxyModel.mapToSource(index)
        part_id = self.model.getPartId(sourceIndex)
        if part_id is None:
            QMessageBox.warning(self, "Error", "Failed to identify selected part.")
            return
        database.delete_part(self, part_id)
        
    def editSelectedPart(self):
        index = self.tree_view.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Selection", "No part selected.")
            return
        sourceIndex = self.proxyModel.mapToSource(index)
        part_id = self.model.getPartId(sourceIndex)
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
        addPartButton.clicked.connect(self.submitPart)
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
            
    def addFeatureToTable(self, feature_data):
        row_position = self.featureTable.rowCount()
        self.featureTable.insertRow(row_position)
        
        keys = ['feature', 'designation', 'kpcNum', 'opNum', 'tol', 'engine']
        for i, key in enumerate(keys):
            value = feature_data.get(key, '')
            self.featureTable.setItem(row_position, i, QTableWidgetItem(value))
            
    def submitPart(self):
                
        upload_date_str = self.udInput.text().strip()
        if not upload_date_str:
            QMessageBox.warning(self, "Error", "Upload date cannot be empty.")
            return
        try: 
            upload_date = datetime.strptime(upload_date_str, '%m/%d/%Y')
        except ValueError:
            QMessageBox.warning(self, "Error", "Upload date must be in MM/DD/YYYY Format.")
            return
            
        due_date = upload_date + timedelta(days=90)
        due_date_str = due_date.strftime('%m/%d/%Y')
        new_part_data = {
            "partNumber": self.partInput.text(),
            "rev": self.revInput.text(),
            "uploadDate": self.udInput.text(),
            "dueDate": due_date_str,
            "notes": self.notesInput.text(),
            "currentManufacturing": self.manufacturingCheck.isChecked(),
            "features": []
        }
        for row in range(self.featureTable.rowCount()):
            feature = {
                "feature": self.featureTable.item(row, 0).text(),
                "designation": self.featureTable.item(row, 1).text(),
                "kpcNum": self.featureTable.item(row, 2).text(),
                "opNum": self.featureTable.item(row, 3).text(),
                "tol": self.featureTable.item(row, 4).text(),
                "engine": self.featureTable.item(row, 5).text(),
            }
            new_part_data["features"].append(feature)
            
        def on_submit_success(is_success):
            if is_success:
                self.partSubmitted.emit()
        if self.mode == "add":
            if database.check_for_part(self.partInput.text()):
                QMessageBox.warning(self, "Error", "Part already exists in database.")
                return
            else: 
                database.submit_new_part(new_part_data, callback=on_submit_success)
        elif self.mode == "edit":
            database.update_part_by_id(self.partId, new_part_data, callback=on_submit_success)
            
        self.close()
    
    def loadPartData(self, selectedPartData):
        self.partInput.setText(selectedPartData['partNumber'])
        self.revInput.setText(selectedPartData['rev'])
        self.udInput.setText(selectedPartData['uploadDate'])
        self.notesInput.setText(selectedPartData['notes'])
        self.manufacturingCheck.setChecked(selectedPartData.get('currentManufacturing', False))
        
        self.featureTable.setRowCount(0)
        for feature in selectedPartData['features']:
            self.addFeatureToTable(feature)
    
    def closeWindow(self):
        self.close()
        
        
#Form for uploading data based on part 
class uploadDataForm(QWidget):
    dataSubmitted = pyqtSignal()
    def __init__(self, partId=None):
        super().__init__()
        self.partId = partId
        self.serialNumberInputs = []
        self.featureTables = []
        self.setWindowTitle("New Data Upload")
        self.resize(800, 600)
        
        layout = QGridLayout()
        
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
        updateCpkButton.clicked.connect(self.calculateCpk)
        layout.addWidget(updateCpkButton, 8, 2, 1, 3)
        
        cancelButton = QPushButton('Cancel')
        cancelButton.setStyleSheet("background-color: #D6575D")
        cancelButton.clicked.connect(self.closeWindow)
        layout.addWidget(cancelButton, 9, 2, 1, 3)
        
        self.dataTable = QTableWidget()
        self.dataTable.setColumnCount(5)
        self.dataTable.horizontalHeader().setStretchLastSection(False)
        self.dataTable.setHorizontalHeaderLabels(['Feature Number', 'KPC Number', 'Blueprint Dimension', 'Op Number', 'Measurement'])
        for column in range(self.dataTable.columnCount()):
            self.dataTable.horizontalHeader().setSectionResizeMode(column, QHeaderView.Stretch)
            
        self.setLayout(layout)
        
    def calculateCpk(self):
        functions.calculateAndUpdateCpk(self, self.partId)
        
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