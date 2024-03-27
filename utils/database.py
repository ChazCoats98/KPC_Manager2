import json
from pymongo import MongoClient
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QMessageBox

client: MongoClient = MongoClient()
kpcdb = client['KPCManager']
parts = kpcdb['parts']

def get_all_data():
    data = parts.find()
    return list(data)

def submit_new_part(part_form):
    partNumber = part_form.partInput.text()
    rev = part_form.revInput.text()
    uploadDateStr = part_form.udInput.text()
    notes = part_form.notesInput.text()
    features = part_form.featuresInput.text()
    
    try: 
        uploadDate = datetime.strptime(uploadDateStr, '%m/%d/%Y')
    except ValueError:
        QMessageBox.warning(part_form, "Error", "Invalid upload date format. Use MM/DD/YYYY")
        return
    
    dueDate = uploadDate + timedelta(days=90)
    
    dueDateStr = dueDate.strftime('%m/%d/%y')
    
    