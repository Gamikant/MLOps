import yaml
import numpy as np
from sklearn.model_selection import train_test_split
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('pipeline.log'), logging.StreamHandler()]
)
logger = logging.getLogger('prepare_data')

def prepare_data():
    # Load parameters
    with open('params.yaml', 'r') as f:
        params = yaml.safe_load(f)
    
    random_seed = params['random_seed']
    train_size = params['data_split']['train_size']
    val_size = params['data_split']['val_size']
    test_size = params['data_split']['test_size']
    
    np.random.seed(random_seed)
    
    logger.info("Loading dataset")
    X = np.load('data/images.npy')
    y = np.load('data/labels.npy')
    
    # Normalize pixel values
    X = X.astype('float32') / 255.0
    
    # Split data
    logger.info(f"Splitting data with train={train_size}, val={val_size}, test={test_size}")
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_seed, stratify=y
    )
    
    relative_val_size = val_size / (train_size + val_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=relative_val_size, 
        random_state=random_seed, stratify=y_train_val
    )
    
    # Save splits
    os.makedirs('data/prepared', exist_ok=True)
    np.save('data/prepared/X_train.npy', X_train)
    np.save('data/prepared/y_train.npy', y_train)
    np.save('data/prepared/X_val.npy', X_val)
    np.save('data/prepared/y_val.npy', y_val)
    np.save('data/prepared/X_test.npy', X_test)
    np.save('data/prepared/y_test.npy', y_test)
    
    logger.info(f"Data prepared: train={X_train.shape[0]}, val={X_val.shape[0]}, test={X_test.shape[0]}")

if __name__ == "__main__":
    prepare_data()
