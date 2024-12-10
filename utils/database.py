import json
from pymongo import MongoClient
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QMessageBox


client: MongoClient = MongoClient()
kpcdb = client['KPCManager']
parts = kpcdb['parts']
ppap = kpcdb['ppap']
forms = kpcdb['forms']
measurements = kpcdb['measurements']

def get_all_data():
    data = parts.find()
    print(data)
    return list(data)

def get_part_by_id(part_id):
    data = parts.find_one({"partNumber": part_id})
    return data

def update_part_by_id(partId, new_part_data, callback=None):
    try:
        existing_part_data = parts.find_one({"partNumber": partId})
        
        if not existing_part_data:
            print(f"Part # {partId} not found.")
            return
        
        changed_data = {
            key: value for key, value in new_part_data.items() 
            if existing_part_data[key] != value 
        }
        result = parts.update_one({"partNumber": partId}, {"$set": changed_data})
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
    
def get_all_ppap_data():
    data = ppap.find()
    return list(data)
    
def submit_new_ppap_part(new_ppap_data, callback=None):
    try: 
        result = ppap.insert_one(new_ppap_data)
        
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
            
def check_for_ppap(part_number):
    count = ppap.count_documents({"partNumber": part_number})
    return count > 0

def update_ppap_by_id(partId, new_part_data, callback=None):
    try:
        result = ppap.update_one({"partNumber": partId}, {"$set": new_part_data})
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
    print(partNumber, serialNumber, uploadDate )
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
    
def check_serial_number(text):
    try: 
        result = measurements.find_one({'serialNumber': text})
        if result:
            return True
        else: 
            return False
    except Exception as e:
        print(e)
        return False
    
def convert_date_format(date_str):
    date_obj = datetime.strptime(date_str, '%m/%d/%y')
    
    new_date_str = datetime.strftime(date_obj, '%m/%d/%Y')
    
    return new_date_str

def update_dates():
    for document in measurements.find():
        if len(document["uploadDate"]) == 8:
            new_date = convert_date_format(document["uploadDate"])
            
            measurements.update_one({'_id': document["_id"]}, {'$set': {'uploadDate': new_date }})
        else:
            print(f'Skipped document {document["_id"]}: date format already correct or unexpected error')
    print("Date format update completed")
    
def add_management_form(form, callback=None):
    try:
        result = forms.insert_one(form)
        if result.acknowledged:
            print('Form upload successful')
            if callback:
                callback(True)
        else:
            print('Form upload failed')
            if callback:
                callback(False)
    except Exception as e:
        print(e)
        if callback:
            callback(False)
            
def get_form_by_pn(pn):
    response = forms.find({'partNumber': pn})
    return list(response)