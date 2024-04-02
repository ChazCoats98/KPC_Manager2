from pymongo import MongoClient
import pandas as pd

client: MongoClient = MongoClient()
kpcdb = client['KPCManager']
parts = kpcdb['parts']
users = kpcdb['users']
measurements = kpcdb['measurements']

df = pd.read_excel('710410_data.xlsx')

partData = {
    'partNumber': '710410',
    'rev': 'F',
    'uploadDate': '8/21/2023',
    'dueDate': '11/19/2023',
    'notes': 'needs gage R&R',
    'features': [{'feature': '1','designation': 'KPC1' , 'kpcNum': '84740', 'tol': '16.396 - 16.398', 'engine': 'TF33' }, 
        {'feature': '2','designation': 'KPC1' , 'kpcNum': '109584', 'tol': '.215 Min', 'engine': 'TF33' }, 
        {'feature': '3','designation': 'KPC1' , 'kpcNum': '109582', 'tol': '.104 Min', 'engine': 'TF33'}, 
        {'feature': '4','designation': 'KPC1' , 'kpcNum': '84739', 'tol': '.437 - .439', 'engine': 'TF33'}, 
        {'feature': '5','designation': 'KPC1' , 'kpcNum': '109583', 'tol': '.115 Min', 'engine': 'TF33'},
        {'feature': '6','designation': 'KPC1' , 'kpcNum': '112276', 'tol': 'True Position .001', 'engine': 'TF33'},
        {'feature': '7','designation': 'KPC2' , 'kpcNum': '84741', 'tol': '5.5114 - 5.5121', 'engine': 'TF33'}]
}

for (partNumber, serialNumber, uploadDate), group in df.groupby(['partNumber', 'serialNumber', "uploadDate"]):
    measurement_data = {
        'partNumber': partNumber,
        'serialNumber': serialNumber,
        'uploadDate': uploadDate,
        'measurements': group[['kpcNum', 'measurement']].to_dict('records')
        
    }


measurements.insert_one(measurement_data)