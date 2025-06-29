from networksecurity.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH
from networksecurity.utils.main_utils.utils import read_yaml_file,write_yaml_file
from scipy.stats import ks_2samp
import pandas as pd 
import numpy as np 
import os 
import sys


class DataValidation:
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,data_validation_config:DataValidationConfig):
        try:
            self.data_ingestion_artifact=data_ingestion_artifact
            self.data_validation_config=data_validation_config
            self.schema_config=read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    @staticmethod
    def read_data(file)->pd.DataFrame:
        try:
            dataframe = pd.read_csv(file)
            return dataframe
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def validate_no_of_columns(self,dataframe:pd.DataFrame):
        try:
            num_of_col=len(self.schema_config)
            logging.info(f"required no of columns{num_of_col}")
            logging.info(f"no. of columns in the dataframe{len(dataframe.columns)}")
            if len(dataframe.columns)==num_of_col:
                return True
            return False
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def detect_data_drift(self,base_df,current_df,threshold=0.05)->bool:
        try:
            status=True
            report={}
            for column in base_df.columns:
                d1=base_df[column]
                d2=current_df[column]
                is_same_distb=ks_2samp(d1,d2)
                if threshold<=is_same_distb.pvalue:
                    is_found=False
                else:
                    is_found=True
                    status=False
                
                report.update({column:{
                    "pvalue":is_same_distb.pvalue,
                    "drift_status":is_found
                }})
            drift_report_file_path=self.data_validation_config.drift_report_file_path

            ##create a directory
            dir_name=os.path.dirname(drift_report_file_path)
            os.makedirs(dir_name,exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path,content=report)
            return status

        except Exception as e:
            raise NetworkSecurityException(e,sys)

    def initiate_data_validation(self)->DataValidationArtifact:
        try:
            train_file_path=self.data_ingestion_artifact.trained_file_path
            test_file_path=self.data_ingestion_artifact.test_file_path

            ##read the file path 
            train_dataframe=DataValidation.read_data(train_file_path)
            test_dataframe=DataValidation.read_data(test_file_path)

            ## validate the no of columns 
            status=self.validate_no_of_columns(dataframe=train_dataframe)
            if status==False:
                error_message="train data does not contain all the columns"
            status=self.validate_no_of_columns(dataframe=test_dataframe)
            if status==False:
                error_message="test data does not contain all the columns"

            ## detect data drift 
            status=self.detect_data_drift(train_dataframe,test_dataframe)
            dir_path=os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path,exist_ok=True)

            train_dataframe.to_csv(
                self.data_validation_config.valid_train_file_path , index=False, header=True
            )
            test_dataframe.to_csv(
                self.data_validation_config.valid_test_file_path , index=False,header=True
            )

            data_validation_artifact=DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_ingestion_artifact.trained_file_path,
                valid_test_file_path=self.data_ingestion_artifact.test_file_path,
                invalid_test_file_path=None,
                invalid_train_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )

            return data_validation_artifact

        except Exception as e:
            raise NetworkSecurityException(e,sys)