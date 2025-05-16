import os 
import sys 
import json 

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL=os.getenv("MONGO_DB_URL")
print(MONGO_DB_URL)

## to ensure secure HTTPS connection 
## certifi helps in maintaing and specifying trusted CA(certificate authority) to verify servers certificate 
import certifi
ca=certifi.where()

import pandas as pd
import numpy as np 
import pymongo
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

class Network_Extract():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    def covert_tojson(self,filepath):
        try:
            data=pd.read_csv(filepath)
            data.reset_index(drop=True,inplace=True)
            records=list(json.loads(data.T.to_json()).values())
            return records
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def insert_data_mongoDb(self,records,database,collection):
        try:
            self.records=records
            self.database=database
            self.collection=collection
 
            self.mongo_client=pymongo.MongoClient(MONGO_DB_URL) ## connects the client 
            self.database=self.mongo_client[self.database] ## selects the client database 
            self.collection=self.database[self.collection] ## selects collection from the database

            self.collection.insert_many(self.records) ## insert all the records in the collection 
            return len(records)
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    
if __name__=="__main__":
    FILE_PATH="Network_Data/phisingData.csv"
    DATABASE="MukundAi"
    Collection="NetworkData"
    network_obj=Network_Extract()
    records=network_obj.covert_tojson(filepath=FILE_PATH)
    print(records)
    no_of_records=network_obj.insert_data_mongoDb(records=records,database=DATABASE,collection=Collection)
    print(no_of_records)
