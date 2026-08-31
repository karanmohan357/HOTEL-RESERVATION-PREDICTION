import os
import pandas as pd
import joblib
from sklearn.model_selection import RandomizedSearchCV
import lightgbm as lgb
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from config.model_params import *
from utils.common_functions import read_yaml, load_data
from scipy.stats import randint
import mlflow
import mlflow.sklearn

logger = get_logger(__name__)

class ModelTraining:

    def __init__(self,train_path,test_path,model_output_path):
        self.train_path = train_path
        self.test_path = test_path
        self.model_output_path = model_output_path

        self.params_dist = LIGHTGBM_PARAMS
        self.random_search_params = RANDOM_SEARCH_PARAMS

    def load_and_split_data(self):
        try:
            logger.info(f"Loading training from {self.train_path} and testing data from {self.test_path}.")
            train_df = load_data(self.train_path)
            test_df = load_data(self.test_path)

            X_train = train_df.drop('booking_status', axis=1)
            y_train = train_df['booking_status']

            X_test = test_df.drop('booking_status', axis=1)
            y_test = test_df['booking_status']

            logger.info("Data loaded and split successfully for Model Training.")

            return X_train, y_train, X_test, y_test
        
        except Exception as e:
            logger.error(f"Error in loading and splitting data: {e}")
            raise CustomException(f"Failed to load and split data" , e)

    def train_lgbm(self, X_train, y_train):
        try:
            logger.info("Starting LightGBM model training with RandomizedSearchCV.")
            lgbm_model = lgb.LGBMClassifier(random_state=self.random_search_params['random_state'])
            logger.info("Starting our Hyperparameter tuning using RandomizedSearchCV.")
            random_search = RandomizedSearchCV(
                estimator=lgbm_model, 
                param_distributions=self.params_dist, 
                **self.random_search_params)

            logger.info("Starting our Hyperparameter tuning")

            random_search.fit(X_train, y_train)

            logger.info("Hyperparameter Tuning completed successfully.")

            best_params = random_search.best_params_
            best_lgbm_model = random_search.best_estimator_

            logger.info(f"Best Hyperparameters are: {best_params}")

            return best_lgbm_model
        
        except Exception as e:
            logger.error(f"Error during model training: {e}")
            raise CustomException(f"Failed to train the model", e)

    def evaluate_model(self, model, X_test, y_test):
        try:
            logger.info("Evaluating the model on test data.")
            y_pred = model.predict(X_test)

            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')
            f1 = f1_score(y_test, y_pred, average='weighted')

            logger.info(f"Model Evaluation Metrics - Accuracy: {accuracy}, Precision: {precision}, Recall: {recall}, F1 Score: {f1}")

            return {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1
            }
        
        except Exception as e:
            logger.error(f"Error during model evaluation: {e}")
            raise CustomException(f"Failed to evaluate the model", e)

    def save_model(self, model):
        try:
            os.makedirs(os.path.dirname(self.model_output_path), exist_ok=True)

            logger.info(f"Saving the trained model to {self.model_output_path}.")
            joblib.dump(model, self.model_output_path)
            logger.info(f"Model saved successfully to {self.model_output_path}.")
        
        except Exception as e:
            logger.error(f"Error saving the model: {e}")
            raise CustomException(f"Failed to save the model", e)
      
    def run(self):
        try:
            mlflow.set_tracking_uri("file:./mlruns")
            mlflow.set_experiment("Hotel_Booking_Cancellation_Prediction")
            with mlflow.start_run():

                logger.info("Starting the model training pipeline.")
                logger.info("Starting ot MLflow experimentation.")

                logger.info("Logging the training and  testing dataset to MLflow.")
                mlflow.log_artifact(self.train_path, artifact_path="datasets")
                mlflow.log_artifact(self.test_path, artifact_path="datasets")

                X_train, y_train, X_test, y_test = self.load_and_split_data()
                best_model = self.train_lgbm(X_train, y_train)
                metrics = self.evaluate_model(best_model, X_test, y_test)
                self.save_model(best_model)

                logger.info("Logging the model to MLflow.")
                mlflow.log_artifact(self.model_output_path)

                logger.info("Logging the model parameters and metrics to MLflow.")
                mlflow.log_params(best_model.get_params())
                mlflow.log_metrics(metrics)

                logger.info("Model training completed successfully.")
        
        except Exception as e:
            logger.error(f"Error in the model training pipeline: {e}")
            raise CustomException(f"Failed to complete the model training pipeline", e)

if __name__ == "__main__":
    trainer = ModelTraining(PROCESSED_TRAIN_DATA_PATH, PROCESSED_TEST_DATA_PATH, MODEL_OUTPUT_PATH)
    trainer.run()