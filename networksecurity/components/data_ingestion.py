from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

## configuration of data ingestion config
from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact

import os 
import sys 
from typing import List
import pandas as pd 
import numpy as np 
import pymongo
from sklearn.model_selection import train_test_split

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL=os.getenv("MONGO_DB_URL")

class DataIngestion:
    def __init__(self,data_ingestion_config:DataIngestionConfig):
        try:
            self.data_ingestion_config=data_ingestion_config

        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def export_collection_as_dataframe(self):
        """
        read the data from the mongoDB 
        
        """

        try:
            database_name=self.data_ingestion_config.database_name ## get the db name from the config
            collection_name=self.data_ingestion_config.collection_name
            self.mongo_client=pymongo.MongoClient(MONGO_DB_URL) # initialise the mongo client 
            collection=self.mongo_client[database_name][collection_name] # extracting the collection from mongoDB

            df=pd.DataFrame(list(collection.find())) #convert it into dataframe 
            if "_id" in df.columns.to_list():
                df.drop(columns=["_id"],axis=1)
            
            df.replace({"na":np.nan},inplace=True)
            return df

        except Exception as e :
            raise NetworkSecurityException(e,sys)
    
    def export_data_to_feature_store(self,dataframe:pd.DataFrame):
        try:
            feature_store_file_path=self.data_ingestion_config.feature_store_file_path
            #creating a folder
            dir_path=os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path,exist_ok=True)
            dataframe.to_csv(feature_store_file_path,index=False,header=True) ## will store this in this path 
            return dataframe
        
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def split_data_as_train_test(self, dataframe: pd.DataFrame):
        try:
            train_set, test_set = train_test_split(
                dataframe, 
                test_size=self.data_ingestion_config.train_test_split_ratio
            )
            logging.info("performed train test split")
            logging.info("exited the train test split method of Data_Ingestion class")
            
            # Create the ingested directory - both files go in the same directory
            ingested_dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(ingested_dir_path, exist_ok=True)

            logging.info("Exporting train and test file path.")

            # Save train file
            train_set.to_csv(
                self.data_ingestion_config.training_file_path, 
                index=False, 
                header=True
            )
            
            # Save test file  
            test_set.to_csv(
                self.data_ingestion_config.test_file_path, 
                index=False, 
                header=True
            )
            
            logging.info("Exported train and test file path.")
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)



    def initiate_data_ingestion(self):
        try:
            dataframe=self.export_collection_as_dataframe() ## step 1 reading data from the mongodb
            dataframe=self.export_data_to_feature_store(dataframe) ## step 2 converting into csv and exporting into feature store as raw csv 
            self.split_data_as_train_test(dataframe)
            dataingestionartifact=DataIngestionArtifact(trained_file_path=self.data_ingestion_config.training_file_path,
                                                        test_file_path=self.data_ingestion_config.test_file_path)
            return dataingestionartifact ## final output of the data ingestion component
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        





