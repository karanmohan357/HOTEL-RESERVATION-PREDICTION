import os
import pandas as pd
import boto3
from sklearn.model_selection import train_test_split
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml


logger = get_logger(__name__)

class DataIngestion:

    def __init__(self,config):
        self.config = config["data_ingestion"]
        self.bucket_name = self.config["bucket_name"]
        self.file_name = self.config["bucket_file_name"]
        self.train_test_ratio = self.config["train_ratio"]

        os.makedirs(RAW_DIR, exist_ok=True)

        logger.info(f"Data Ingestion started with {self.bucket_name} and file is {self.file_name}")

    def download_csv_from_s3(self):
        try:
            client =boto3.client('s3')
            client.download_file(self.bucket_name,self.file_name, RAW_FILE_PATH)

            logger.info(f"CSV file is successfully downloaded to {RAW_FILE_PATH}")

        except Exception as e:
            logger.error("Error while downlaoding the CSV file")
            raise CustomException("Filed to download csv file" , e)

    def split_data(self):
        try:
            logger.info("Starting the splitting process")
            data = pd.read_csv(RAW_FILE_PATH)

            train_data , test_data = train_test_split(data, test_size = 1 - self.train_test_ratio, random_state=42)

            train_data.to_csv(TRAIN_FILE_PATH)
            test_data.to_csv(TEST_FILE_PATH)

            logger.info(f" Train data saved to {TRAIN_FILE_PATH} and Test data saved to {TEST_FILE_PATH}")

        except Exception as e:
            logger.error("Error while splitting the data")
            raise CustomException("Failed to split data into training and test sets ", e)

    def run(self):

        try:
            logger.info("Starting data ingestion process")
            self.download_csv_from_s3()
            self.split_data()

            logger.info("Data Ingestion completed successfully")

        except CustomException as ce:
            logger.error(f"Custom Exception : {str(ce)}")

        finally:
            logger.info("Data Ingestion completed")

if __name__=="__main__":

    data_ingestion = DataIngestion(read_yaml(CONFIG_PATH))
    data_ingestion.run()