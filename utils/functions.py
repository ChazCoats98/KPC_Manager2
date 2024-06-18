import re
import shutil
import hashlib
from datetime import datetime
import numpy as np
from openpyxl import load_workbook
from PyQt5.QtWidgets import QMessageBox
from utils import database, functions
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

emailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
passwordRegex = r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$'

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
        
def format_date(date_str):
    parts = date_str.split('/')
    if len(parts) == 3:
        month, day, year = parts
        if len(year) == 2:
            date_obj = datetime.strptime(date_str, '%m/%d/%y')
        elif len(year) == 4:
            date_obj = datetime.strptime(date_str, '%m/%d/%Y')
        else:
            raise ValueError('Invalid date format')
            
        return date_obj.strftime('%m/%d/%Y')
    else: 
        raise ValueError('Invalid date format')
    

#_____________________________#
##Upload Data View Functions##
#_____________________________#

#clears lot inputs from table 
def clearLotInputs(self):
        while self.scrollAreaWidgetLayout.count():
            item = self.scrollAreaWidgetLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.serialNumberInputs = []
        self.featureTables = []

#Create tables for data upload    
def createLotInputs(self, lot_size):
        currentInputs = {
            'serialNumbers': [input.text() for input in self.serialNumberInputs],
            'measurements': []
        }
        
        for table in self.featureTables:
            currentTableData = []
            for row in range(table.rowCount()):
                rowData = [table.item(row, col).text() if table.item(row, col) else '' for col in range(table.columnCount())]
                currentTableData.append(rowData)
            currentInputs['measurements'].append(currentTableData)
        
        
        clearLotInputs(self)
        
        partData = database.get_part_by_id(self.partId)
        if not partData:
            QMessageBox.warning(self, "Error", "Part data not found in database.")
            return
        part_features = partData['features']
        
        for lot_index in range(lot_size):
            serialNumberInput = QLineEdit()
            serialNumberInput.setPlaceholderText(f'Enter Serial Number {lot_index+1}')
            serialNumberInput.textChanged.connect(lambda text, sn_input=serialNumberInput: checkSerialNumber(self, text, sn_input))
            self.serialNumbersLayout.addWidget(serialNumberInput)
            self.serialNumberInputs.append(serialNumberInput)
            
            featureTable = QTableWidget()
            featureTable.setColumnCount(5)
            featureTable.setRowCount(len(part_features))
            featureTable.setHorizontalHeaderLabels(['Feature Number', 'KPC Number', 'Blueprint Dimension', 'Op Number', 'Measurement'])
            featureTable.horizontalHeader().setStretchLastSection(False)
            for column in range(featureTable.columnCount()):
                featureTable.horizontalHeader().setSectionResizeMode(column, QHeaderView.Stretch)
                
            featureTable.setFixedHeight(250)
                
            for row, feature in enumerate(part_features):
                featureTable.setItem(row, 0, QTableWidgetItem(feature['feature']))
                featureTable.setItem(row, 1, QTableWidgetItem(feature['kpcNum']))
                featureTable.setItem(row, 2, QTableWidgetItem(feature['tol']))
                featureTable.setItem(row, 3, QTableWidgetItem(feature.get('opNum', '')))
                featureTable.setItem(row, 4, QTableWidgetItem(''))
                
            
            self.adjustTableHeight(featureTable)
            self.featureTables.append(featureTable)
            
            self.scrollAreaWidgetLayout.addWidget(serialNumberInput)
            self.scrollAreaWidgetLayout.addWidget(featureTable)
            
        if len(currentInputs['serialNumbers']) <= lot_size:
            for i, text in enumerate(currentInputs['serialNumbers']):
                self.serialNumberInputs[i].setText(text)
        else:    
            for i, text in enumerate(currentInputs['serialNumbers'][:lot_size]):
                self.serialNumberInputs[i].setText(text)
                
        if len(currentInputs['measurements']) <= lot_size:
            for i, table_data in enumerate(currentInputs['measurements']):
                for row, row_data in enumerate(table_data):
                    for col, value in enumerate(row_data):
                        self.featureTables[i].setItem(row, col, QTableWidgetItem(value))
        else:
            for i, table_data in enumerate(currentInputs['measurements'][:lot_size]):
                for row, row_data in enumerate(table_data):
                    for col, value in enumerate(row_data):
                        self.featureTables[i].setItem(row, col, QTableWidgetItem(value))
                        
#calculate or recalculate CPK on data upload 
def calculateAndUpdateCpk(self, partId):
        part_data = database.get_part_by_id(partId)
        if part_data:
            tolerances = {feature['kpcNum']: functions.parse_tolerance(feature.get('tol', '0-0')) for feature in part_data.get('features', [])}
            
        measurement_data = database.get_measurements_by_id(partId)
        
        measurements_by_kpc = {kpc: [] for kpc in tolerances.keys()}
        
        if measurement_data:
            for entry in measurement_data:
                for measurement in entry.get('measurements', []):
                    kpcNum = measurement.get('kpcNum')
                    if kpcNum and kpcNum in measurements_by_kpc:
                        measurements_by_kpc[kpcNum].append(float(measurement['measurement']))
        print(measurements_by_kpc)            
        cpk_values = {}
        for kpc, data in measurements_by_kpc.items():
            usl, lsl = tolerances[kpc]
            print(f'usl: {usl} lsl: {lsl}')
            if usl is not None and lsl is not None:
                cpk = functions.calculate_cpk(data, usl, lsl)
                if cpk is not None:
                    cpk_values[kpc] = cpk
        print(cpk_values)
                
        if cpk_values:
            formatted_cpk_values = {kpc: round(abs(cpk if cpk is not None else 0), 3) for kpc, cpk in cpk_values.items()}
            database.save_cpk_values(partId, formatted_cpk_values)
            self.dataSubmitted.emit()
            
#Checks user input serial number against database to prevent duplicates
def checkSerialNumber(self, text, sender):
        exists = database.check_serial_number(text)
        if exists:
            sender.setStyleSheet("background-color: red")
            QMessageBox.warning(self, "Serial Number Invalid", "Data for this serial number has already been uploaded.")
        else: 
            sender.setStyleSheet("background-color: white")
            
#Lets user select a PDF to pull measurement data from. Not functional yet.
#issues with PDF structure and correctly identifying actual measurements.
#Plan to fix with ML model
def extractDataFromPdf(self, filePath):
        for page_layout in extract_pages(filePath):
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    for text_line in element:
                        text = text_line.get_text().strip()
                        print(text)
        #part_data = database.get_part_by_id(self.partNumber.text())
        #tolerances = {feature['kpcNum']: parse_tolerance(feature['tol']) for feature in part_data['features']}
        #print(tolerances)
        #try:
            #reader = PdfReader(filePath)
            #text = ''
            #for page in reader.pages:
                #text += page.extract_text() + '\n'
            
            #pattern = re.compile(r'\b\d*\.?\d+\b')
            #measurements = [float(m) for m in pattern.findall(text)]
            
            #matched_measurements = {kpc: [] for kpc in tolerances.keys()}
            #for measurement in measurements:
                #for kpc, tolerance in tolerances.items():
                    #lower, upper = tolerance
                    #if lower is not None and upper is not None and lower < measurement < upper:
                        # matched_measurements[kpc].append(measurement)
                    
            #print(matched_measurements)
            #for row in range(self.dataTable.rowCount()):
                #kpcNum = self.dataTable.item(row, 1).text()
                #if kpcNum in matched_measurements and matched_measurements[kpcNum]:
                    #self.dataTable.setItem(row, 4, QTableWidgetItem(str(matched_measurements[kpcNum][0])))
        #except Exception as e:
            #print(str(e))
            #QMessageBox.critical(self, "Error", f"Failed to read PDF: {str(e)}")

#Submits data to database and writes data to Net-Inspect template
def submitData(self):
        part_number = self.partNumber.text()
        existing_part_data = database.get_part_by_id(part_number)
        machine = self.machineComboBox.currentText()
        run_number = self.runNumberInput.text()
        lot_size = self.lotSizeComboBox.currentText()
        target_row = 2
        template_path = './utils/Templates/Measurement_Import_template.xlsx'
        today = datetime.today()
        upload_date_str = today.strftime('%m/%d/%Y')
        upload_date_file_path = today.strftime('%m-%d-%Y')
        new_file_path = f'./Results/{part_number}_data_upload_{upload_date_file_path}.xlsx'
        due_date = today + timedelta(days=90)
        due_date_str = due_date.strftime('%m/%d/%Y')

        if not existing_part_data:
            QMessageBox.warning(self, "Error", "Part data not found in database.")
            return
        
        
        if len(run_number) == 0:
            QMessageBox.warning(self, "Error", "Please enter a valid run number")
            return
        elif len(machine) == 0:
            QMessageBox.warning(self, "Error", "Please select a valid machine")
            return
        elif len(lot_size) == 0:
            QMessageBox.warning(self, "Error", "Please select a lot size")
            return
        
        shutil.copy(template_path,  new_file_path)
        
        workbook = load_workbook(filename=new_file_path)
        sheet = workbook.active
        
        try:
            for serial_input, feature_table in zip(self.serialNumberInputs, self.featureTables):
                serial_number = serial_input.text()
                if database.check_serial_number(serial_number):
                    QMessageBox.warning(self, "Duplicate Serial Number", f"Serial Number {serial_number} already in database")
                    continue
            
                upload_data = {
                    "partNumber": part_number,
                    "serialNumber": serial_number,
                    "uploadDate": upload_date_str,
                    "measurements": []
                }
                
                updated_part_data = {
                        "uploadDate": upload_date_str,
                        "dueDate": due_date_str,
                    }
            
                for row in range(feature_table.rowCount()):
                    feature_number = feature_table.item(row, 0).text()
                    kpcNum = feature_table.item(row, 1).text()
                    measurement = feature_table.item(row, 4).text()
            
                    if part_number:
                        sheet.cell(row=target_row, column=1).value = part_number
                    if feature_number:
                        sheet.cell(row=target_row, column=2).value = feature_number
                    if machine:
                        sheet.cell(row=target_row, column=3).value = machine
                    if run_number:
                        sheet.cell(row=target_row, column=4).value = run_number
                    if lot_size:
                        sheet.cell(row=target_row, column=5).value = lot_size
                    if measurement:
                        sheet.cell(row=target_row, column=6).value = measurement
                    if serial_number:
                        sheet.cell(row=target_row, column=8).value = serial_number
                    target_row += 1
            
                    upload_data["measurements"].append({
                        "kpcNum": kpcNum,
                        "measurement": measurement
                    })
            
            workbook.save(filename=new_file_path)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")
        try: 
            partNumber = self.partNumber.text()
            basePath = f'//server/D/Quality Control/UPPAP Records/Process Cert + Data Collection/Data points/{partNumber}'
            fileName, ok = QFileDialog.getSaveFileName(
                self,
                "Save Excel File",
                basePath,
                "Excel files (*.xlsx)")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
        
        if not fileName:
            QMessageBox.information(self, "Save Canceled", "The save operation was cancelled")
            return
        
        if fileName:
            if not fileName.endswith('.xlsx'):
                fileName += '.xlsx'
            try: 
                shutil.move(new_file_path, fileName)
                database.add_measurement(upload_data)
            
                def on_submit_success(is_success):
                    if is_success:
                        self.dataSubmitted.emit()
                        QMessageBox.information(self, "Success", "Data uploaded successfully.")
                        functions.clearLotInputs(self)
                        
                database.update_part_by_id(self.partId, updated_part_data, callback=on_submit_success)
        
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while saving the file: {e}")
                
        
        functions.calculateAndUpdateCpk(self, self.partId)
            

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
    
def parse_tolerance(tolerance):
    range_pattern = re.compile(r'(?<!\S)(\d*\.\d+)\s*-\s*(\d*\.\d+)(?!\S)')
    specific_tolerance_pattern = re.compile(r'([A-Za-z ]+)\s+(\d*\.\d+)')
    
    range_match = range_pattern.search(tolerance)
    
    if range_match:
        max_val, min_val = map(float, range_match.groups())
        return ( max_val, min_val)
    
    specific_tolerance_match = specific_tolerance_pattern.search(tolerance)
    if specific_tolerance_match:
        tolerance_type, value = specific_tolerance_match.groups()
        return (0, float(value))
    
    return None, None

def calculate_cpk(data, usl=None, lsl=None, target=None):
    if not data or len(data) < 2 or np.isnan(data).any() or np.isinf(data).any():
        return None
    sigma = np.std(data, ddof=1)
    mean = np.mean(data)
    
    if sigma == 0:
        return None
    
    cpk = None
    if usl is None and lsl is not None:
        cpk = (mean - lsl) / (3 * sigma)
        return cpk
    elif usl is not None and lsl is not None:
        cpk_upper = (usl - mean) / (3 * sigma)
        cpk_lower = (mean - lsl) / (3 * sigma)
        cpk = min(cpk_upper, cpk_lower)
    elif usl is not None:
        cpk = (usl - mean) / (3 * sigma)
    elif lsl is not None:
        cpk = (mean - lsl) / (3 * sigma)
    
    if target is not None:
        if usl is not None:
            cpk = (usl - target) / (3 * sigma)
        elif lsl is not None:
            cpk = (target - lsl) / (3 * sigma)
    return cpk

