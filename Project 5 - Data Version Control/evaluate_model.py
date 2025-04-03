import yaml
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import to_categorical
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('pipeline.log'), logging.StreamHandler()]
)
logger = logging.getLogger('evaluate_model')

def evaluate_model():
    # Load parameters
    with open('params.yaml', 'r') as f:
        params = yaml.safe_load(f)
    
    random_seed = params['random_seed']
    dataset_version = params['dataset_version']
    
    np.random.seed(random_seed)
    tf.random.set_seed(random_seed)
    
    # Load test data
    logger.info("Loading test data")
    X_test = np.load('data/prepared/X_test.npy')
    y_test = np.load('data/prepared/y_test.npy')
    
    # Load model
    logger.info("Loading best model")
    model = load_model('models/best_model.h5')
    
    # Convert labels to one-hot encoding
    num_classes = 10
    y_test_cat = to_categorical(y_test, num_classes)
    
    # Evaluate model
    logger.info("Evaluating model on test data")
    test_loss, test_acc = model.evaluate(X_test, y_test_cat, verbose=1)
    logger.info(f"Test accuracy: {test_acc:.4f}")
    
    # Get predictions
    y_pred = model.predict(X_test)
    y_pred_classes = np.argmax(y_pred, axis=1)
    
    # Calculate confusion matrix
    cm = confusion_matrix(y_test, y_pred_classes)
    
    # Plot confusion matrix
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['airplane', 'automobile', 'bird', 'cat', 'deer', 
                             'dog', 'frog', 'horse', 'ship', 'truck'],
                yticklabels=['airplane', 'automobile', 'bird', 'cat', 'deer', 
                             'dog', 'frog', 'horse', 'ship', 'truck'])
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title(f'Confusion Matrix - {dataset_version}')
    
    # Save results
    os.makedirs('evaluation', exist_ok=True)
    plt.savefig(f'evaluation/confusion_matrix_{dataset_version}.png')
    
    # Generate classification report
    class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer', 
                   'dog', 'frog', 'horse', 'ship', 'truck']
    report = classification_report(y_test, y_pred_classes, target_names=class_names)
    
    with open(f'evaluation/classification_report_{dataset_version}.txt', 'w') as f:
        f.write(f"Test Accuracy: {test_acc:.4f}\n\n")
        f.write(report)
    
    # Save predictions for later analysis
    np.save(f'evaluation/y_test_{dataset_version}.npy', y_test)
    np.save(f'evaluation/y_pred_{dataset_version}.npy', y_pred_classes)
    
    logger.info("Evaluation completed and results saved")

if __name__ == "__main__":
    evaluate_model()
