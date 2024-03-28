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

def submit_new_part(new_part_data, callback=None):
    try: 
        result = parts.insert_one(new_part_data)
        
        if result.acknowledged:
            print("Upload success")
            if callback:
                callback(True)
        else: 
            print("upload failure")
            if callback: 
                callback(False)
    except Exception as e:
        print(e)
        if callback: 
            callback(False)
    
def delete_part(self, part_id):
    result = parts.delete_one({"partNumber": part_id})
    if result.deleted_count > 0:
        QMessageBox.information(self,"Success", "Part deleted successfully." )
        self.refreshTreeView()
    else: 
        QMessageBox.warning(self, "Error", "Failed to delete selected part." )
