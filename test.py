from pymongo import MongoClient
import pandas as pd

client: MongoClient = MongoClient()
kpcdb = client['KPCManager']
parts = kpcdb['parts']
users = kpcdb['users']
measurements = kpcdb['measurements']

df = pd.read_excel('710410_data.xlsx')


for (partNumber, serialNumber, uploadDate), group in df.groupby(['partNumber', 'serialNumber','uploadDate']):
    group['kpcNum'] = group['kpcNum'].astype(str)
    group['measurement'] = group['measurement'].astype(str)
    
    partNumber = str(partNumber)
    serialNumber = str(serialNumber)
    formattedDate = uploadDate.strftime('%m/%d/%y') if pd.notnull(uploadDate) else uploadDate
    measurement_data = {
        'partNumber': partNumber,
        'serialNumber': serialNumber,
        'uploadDate': formattedDate,
        'measurements': group[['kpcNum', 'measurement']].to_dict('records')
        
    }
    print(measurement_data)
    measurements.insert_one(measurement_data)

