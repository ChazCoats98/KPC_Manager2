import json
from pymongo import MongoClient
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QMessageBox

client: MongoClient = MongoClient()
kpcdb = client['KPCManager']
parts = kpcdb['parts']

def get_all_data():
    data = parts.find()
    print(data)
    return list(data)

def submit_new_part(new_part_data):
    try: 
        result = parts.insert_one(new_part_data)
        
        if result.acknowledged:
            print("Upload success")
            pass
        else: 
            print("upload failure")
            pass
    except Exception as e:
        pass
    
