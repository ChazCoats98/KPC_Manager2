import json
from pymongo import MongoClient
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QMessageBox

client: MongoClient = MongoClient()
kpcdb = client['KPCManager']
parts = kpcdb['parts']
measurements = kpcdb['measurements']

def get_all_data():
    data = parts.find()
    print(data)
    return list(data)

def get_part_by_id(part_id):
    data = parts.find_one({"partNumber": part_id})
    print(data)
    return data

def update_part_by_id(partId, new_part_data, callback=None):
    try:
        result = parts.update_one({"partNumber": partId}, {"$set": new_part_data})
        if result.modified_count > 0:
            print("Part updated successfully")
            if callback: 
                callback(True)
            else: 
                print("No changes made to part")
                if callback:
                    callback(False)
    except Exception as e: 
        print(e)
        if callback:
            callback(False)

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
        
    
def add_measurement(measurement_data):
    result = measurements.insert_one()
