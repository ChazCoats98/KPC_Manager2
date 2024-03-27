from pymongo import MongoClient

client: MongoClient = MongoClient()
kpcdb = client['KPCManager']
parts = kpcdb['parts']

def getAllData():
    data = parts.find()
    return list(data)
