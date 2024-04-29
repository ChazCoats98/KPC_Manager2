import re
import hashlib
from datetime import datetime
import numpy as np
from PyQt5.QtWidgets import QMessageBox

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

