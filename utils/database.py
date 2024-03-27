import json
from pymongo import MongoClient
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QMessageBox

client: MongoClient = MongoClient()
kpcdb = client['KPCManager']
parts = kpcdb['parts']

def get_all_data():
    data = parts.find()

def submit_new_part(part_data):
    upload_date_str = part_data['uploadDate']
    
    
    uploadDate = datetime.strptime(upload_date_str, '%m/%d/%Y')
    
    due_date = uploadDate + timedelta(days=90)
    
    due_date_str = due_date.strftime('%m/%d/%y')
    part_data['dueDate'] = due_date_str
    
    print(part_data)