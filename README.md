# MLOps Project 1 - Hotel Reservation Cancellation Prediction

An end-to-end MLOps pipeline that predicts whether a hotel reservation will be cancelled, using the [Hotel Reservations dataset](https://www.kaggle.com/datasets/ahmedmohamed2000/hotel-booking-cancellation). The project demonstrates a modular, production-style ML workflow with experiment tracking via MLflow.

## Pipeline Overview

The training pipeline is orchestrated by `pipeline/training_pipeline.py` and runs in three stages:

### 1. Data Ingestion (`src/data_ingestion.py`)
- Downloads `Hotel Reservations.csv` from an S3 bucket using `boto3`
- Splits the data into training (80%) and test (20%) sets with a fixed `random_state=42`
- Saves raw data under `artifacts/raw/`

### 2. Data Preprocessing (`src/data_preprocessing.py`)
- Drops the `Unnamed: 0` and `Booking_ID` columns and removes duplicates
- Applies label encoding to categorical columns (mappings are logged)
- Handles skewness by applying `log1p` to skewed numerical columns
- Balances the training data using SMOTE
- Performs feature selection via Random Forest feature importance (top 10 features)

### 3. Model Training (`src/model_training.py`)
- Trains a LightGBM classifier with hyperparameter tuning using `RandomizedSearchCV`
- Evaluates on the test set using accuracy, precision, recall, and F1 score
- Saves the best model with `joblib` to `artifacts/model/lgbm_model.pkl`
- Logs datasets, parameters, metrics, and the model to **MLflow**

## Project Structure

```
PROJECT-1/
├── pipeline/
│   └── training_pipeline.py   # Main entry point
├── src/
│   ├── data_ingestion.py      # Download + train/test split
│   ├── data_preprocessing.py  # Cleaning, encoding, balancing, feature selection
│   ├── model_training.py      # LightGBM training + MLflow logging
│   ├── logger.py              # Logging configuration
│   └── custom_exception.py    # Custom exception handling
├── config/
│   ├── config.yaml            # Dataset + preprocessing configuration
│   ├── paths_config.py        # Central path definitions
│   └── model_params.py        # Hyperparameter search spaces
├── utils/
│   └── common_functions.py    # Shared helpers (read_yaml, load_data)
├── notebook/
│   ├── notebook.ipynb         # Exploratory data analysis
│   └── train.csv              # Sample dataset
├── artifacts/                 # Generated raw/processed data and model
├── logs/                      # Daily log files
├── mlruns/                    # MLflow experiment artifacts
├── mlartifacts/
├── mlflow.db                  # MLflow tracking database
├── requirements.txt
└── setup.py
```

## Installation

```bash
# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

# Install the package
pip install -e .
```

## Configuration

Key settings live in `config/config.yaml`:

| Setting | Value |
| --- | --- |
| `bucket_name` | `mlops-project-1-hotel-reservation` |
| `bucket_file_name` | `Hotel Reservations.csv` |
| `train_ratio` | `0.8` |
| `skewness_threshold` | `5` |
| `number_of_features` | `10` |

**Prerequisites for data ingestion:** the dataset must be available in an S3 bucket configured via your AWS credentials (default profile or environment variables), since ingestion downloads the CSV directly from S3.

## Usage

Run the complete pipeline:

```bash
python pipeline/training_pipeline.py
```

Individual stages can also be run on their own:

```bash
python src/data_ingestion.py
python src/data_preprocessing.py
python src/model_training.py
```

## MLflow Tracking

The training stage logs to MLflow under the experiment `Hotel_Booking_Cancellation_Prediction`. To view the runs:

```bash
mlflow ui --host 0.0.0.0 --port 5000
```

Each run tracks the training/test datasets, hyperparameters, model artifacts, and evaluation metrics (accuracy, precision, recall, F1).

## Logging

Daily logs are written to `logs/log_YYYY-MM-DD.log` in the format:

```
<module> - <timestamp> - <level> - <message>
```
