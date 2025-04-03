import yaml
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.utils import to_categorical
import os
import logging
from sklearn.model_selection import ParameterGrid

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('pipeline.log'), logging.StreamHandler()]
)
logger = logging.getLogger('train_model')

def build_model(input_shape, num_classes, conv_layers, conv_filters, kernel_sizes, dropout_rate, learning_rate):
    model = Sequential()
    
    # Add convolutional layers
    for i in range(conv_layers):
        if i == 0:
            model.add(Conv2D(conv_filters[i], kernel_size=(kernel_sizes[i], kernel_sizes[i]), 
                             activation='relu', padding='same', input_shape=input_shape))
        else:
            model.add(Conv2D(conv_filters[i], kernel_size=(kernel_sizes[i], kernel_sizes[i]), 
                             activation='relu', padding='same'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
    
    # Add fully connected layers
    model.add(Flatten())
    model.add(Dense(512, activation='relu'))
    model.add(Dropout(dropout_rate))
    model.add(Dense(num_classes, activation='softmax'))
    
    # Compile model
    model.compile(
        loss='categorical_crossentropy',
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        metrics=['accuracy']
    )
    
    return model

def train_model():
    # Load parameters
    with open('params.yaml', 'r') as f:
        params = yaml.safe_load(f)
    
    random_seed = params['random_seed']
    learning_rate = params['model']['learning_rate']
    conv_layers = params['model']['conv_layers']
    conv_filters = params['model']['conv_filters']
    kernel_sizes = params['model']['kernel_sizes']
    dropout_rate = params['model']['dropout_rate']
    batch_size = params['model']['batch_size']
    epochs = params['model']['epochs']
    
    np.random.seed(random_seed)
    tf.random.set_seed(random_seed)
    
    # Load data
    logger.info("Loading prepared data")
    X_train = np.load('data/prepared/X_train.npy')
    y_train = np.load('data/prepared/y_train.npy')
    X_val = np.load('data/prepared/X_val.npy')
    y_val = np.load('data/prepared/y_val.npy')
    
    # Convert labels to one-hot encoding
    num_classes = 10
    y_train_cat = to_categorical(y_train, num_classes)
    y_val_cat = to_categorical(y_val, num_classes)
    
    # Define hyperparameter grid for tuning
    param_grid = {
        'learning_rate': [0.0001, 0.001, 0.01],
        'dropout_rate': [0.2, 0.3, 0.4]
    }
    
    # Hyperparameter tuning
    logger.info("Starting hyperparameter tuning")
    best_val_acc = 0
    best_params = {}
    best_model = None
    
    for params_comb in ParameterGrid(param_grid):
        curr_lr = params_comb['learning_rate']
        curr_dropout = params_comb['dropout_rate']
        
        logger.info(f"Training with lr={curr_lr}, dropout={curr_dropout}")
        
        model = build_model(
            input_shape=X_train.shape[1:],
            num_classes=num_classes,
            conv_layers=conv_layers,
            conv_filters=conv_filters,
            kernel_sizes=kernel_sizes,
            dropout_rate=curr_dropout,
            learning_rate=curr_lr
        )
        
        # Train model
        history = model.fit(
            X_train, y_train_cat,
            batch_size=batch_size,
            epochs=epochs,
            validation_data=(X_val, y_val_cat),
            verbose=1
        )
        
        # Check if this model is better
        val_acc = max(history.history['val_accuracy'])
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_params = params_comb
            best_model = model
    
    # Save best model and parameters
    os.makedirs('models', exist_ok=True)
    best_model.save('models/best_model.h5')
    logger.info("Best model saved successfully!")
    
    with open('models/best_params.yaml', 'w') as f:
        yaml.dump(best_params, f)
    
    logger.info(f"Best model saved with params: {best_params}, val_accuracy: {best_val_acc:.4f}")

if __name__ == "__main__":
    train_model()
