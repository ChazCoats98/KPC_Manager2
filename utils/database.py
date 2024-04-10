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
        
def check_for_part(part_number):
    count = parts.count_documents({"partNumber": part_number})
    return count > 0
    
def save_cpk_values(partId, cpk_values):
    part_doc = parts.find_one({'partNumber': partId})
    if not part_doc:
        print(f'No part found with part number {partId}')
        return
    for feature in part_doc['features']:
        kpc_num = feature['kpcNum']
        if kpc_num in cpk_values:
            parts.update_one(
                {'partNumber': partId, 'features.kpcNum': kpc_num},
                {'$set': {'features.$.cpk': cpk_values[kpc_num]}}
            )
    print(f'CPK values updated for part number {partId}')
    
def add_measurement(upload_data):   
    try:
        result = measurements.insert_one(upload_data)
        if result.acknowledged:
            print("Upload success")
        else: 
            print("upload failure")
    except Exception as e:
        print(e)
    
def get_measurements_by_id(part_id):
    data = measurements.find({"partNumber":part_id})
    return (list(data))

def delete_duplicate_measurements():
    parts = measurements.find()
    
    for part in parts:
        seen = set()
        unique_measurements = []
        for measurement in part.get('measurements', []):
            identifier = (measurement['kpcNum'], measurement['measurement'])
            if identifier not in seen: 
                seen.add(identifier)
                unique_measurements.append(measurement)
                
        measurements.update_one(
            {'_id': part['_id']},
            {'$set': {'measurements': unique_measurements}}
        )
        
def delete_measurement_by_id(self, partNumber, serialNumber, uploadDate, callback=None):
    try:
        result = measurements.delete_one({'partNumber': partNumber, 'serialNumber': serialNumber, 'uploadDate':uploadDate})
        if result.deleted_count > 0:
            QMessageBox.information(self,"Success", "measurement deleted successfully." )
            return result.deleted_count
        else: 
            QMessageBox.warning(self, "Error", "Failed to delete selected measurement." )
            callback(False)
    except Exception as e:
        print(e)
        return
    