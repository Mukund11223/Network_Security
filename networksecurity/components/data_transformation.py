import os 
import sys
import numpy as np 
import pandas as pd
from networksecurity.logging.logger import logging
from networksecurity.exception.exception import NetworkSecurityException
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline
from networksecurity.constant.training_pipeline import TARGET_COLUMN
from networksecurity.constant.training_pipeline import DATA_TRANSFORMATION_IMPUTER_PARAMS
from networksecurity.entity.config_entity import DataTransformationConfig
from networksecurity.entity.artifact_entity import DataValidationArtifact,DataTransformationArtifact
from networksecurity.utils.main_utils.utils import save_numpy_array_data,save_obj

class DataTransformation:
    def __init__(self,data_validation_artifact:DataValidationArtifact,
                 data_transformation_config:DataTransformationConfig):
        try:
            self.data_transformation_config=data_transformation_config
            self.data_validation_artifact=data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    @staticmethod
    def read_data(file_path)->pd.DataFrame:
        try:
            df=pd.read_csv(file_path)
            return df
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def get_data_transformer_object(self)->Pipeline:
        """
        it initialises KNN imputer object with the parameters specified in training_pipeline.py file
        and returns a Pipeline object with KNNimputer object as the first step 

        args:
            cls:DataTransformation
        
        returns : a pipepline object
        """
        try:
            imputer:KNNImputer=KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS) ## ** to specify it is a key value pair 
            logging.info("initialize the KNN imputer")
            processor:Pipeline=Pipeline([("imputer",imputer)])
            return processor
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    
        
    def initiate_data_transformation(self)->DataTransformationArtifact:
        logging.info("entered initiate_data_transformation method of Data Transformation Class")
        try:
            train_df=DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df=DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)

            ## training dataframe 
            input_feature_train_df=train_df.drop(columns=[TARGET_COLUMN],axis=1)
            target_feature_train_df=train_df[TARGET_COLUMN]
            target_feature_train_df=target_feature_train_df.replace(-1,0)

            ## testing dataframe
            input_feature_test_df=test_df.drop(columns=[TARGET_COLUMN],axis=1)
            target_feature_test_df=test_df[TARGET_COLUMN]
            target_feature_test_df=target_feature_test_df.replace(-1,0)

            # Convert all columns to numeric, forcing errors to NaN
            logging.info("Converting input features to numeric format")
            input_feature_train_df = input_feature_train_df.apply(pd.to_numeric, errors='coerce')
            input_feature_test_df = input_feature_test_df.apply(pd.to_numeric, errors='coerce')
            
            # Log data types after conversion
            logging.info(f"Train data types after conversion: {input_feature_train_df.dtypes}")
            logging.info(f"Test data types after conversion: {input_feature_test_df.dtypes}")

            preprocessor=self.get_data_transformer_object()
            preprocessor_obj=preprocessor.fit(input_feature_train_df)
            transformed_input_train_df=preprocessor_obj.transform(input_feature_train_df)
            transformed_input_test_df=preprocessor_obj.transform(input_feature_test_df)

            train_arr=np.c_[transformed_input_train_df,np.array(target_feature_train_df)] ## c_ helps to combine both 
            test_arr=np.c_[transformed_input_test_df,np.array(target_feature_test_df)]

            ## save the numpy array data 
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path,train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path,test_arr)
            save_obj(self.data_transformation_config.transformed_object_file_path,preprocessor_obj)

            ## preparing artifacts
            data_transformation_artifact=DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )

            return data_transformation_artifact


        except Exception as e:
            raise NetworkSecurityException(e,sys)