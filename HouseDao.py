from pymongo import MongoClient
import gridfs
import sys
class HouseDao:
    _instance = None
    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance

    def __init__(self):
        mongoUrl = sys.argv[2]
        self.client = MongoClient(mongoUrl)
        self.db = self.client['IMMO_DB']
        self.coll = self.db['houses']

    def update(self, findDoc, updateDoc):
        self.coll.update(findDoc, updateDoc, upsert=False)

    def updateHouseParsed(self,house):
        self.coll.update({"_id": house.id}, {"$currentDate": {'date_last': {'$type': 'date'}}},
                         upsert=False)
        return self.coll.update({"_id": house.id}, {"$set": {"price_last": house.price,"m2price_last": house.getM2Price(), "deleted":False}},
                         upsert=False);

    def insertHouse(self,house):
        return self.coll.insert(house.item())

    def addPdf(self,houseId,pdf):
        fs = gridfs.GridFS(self.db)
        id = fs.put(pdf)
        self.coll.update({"_id": houseId}, {"$set": {"pdf": id}}, upsert=False)

    def updateHouseDeleted(self,houseId):
        return self.coll.update({"_id": houseId}, {"$set": {"deleted":True}},
                         upsert=False);

    def getUndeletedHouses(self):
        return self.coll.find({'deleted':False});