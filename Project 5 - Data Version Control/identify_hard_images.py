import numpy as np
import matplotlib.pyplot as plt
import os
import yaml
from tensorflow.keras.models import load_model
import seaborn as sns
import pandas as pd
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('hard_images_analysis.log'), logging.StreamHandler()]
)
logger = logging.getLogger('identify_hard_images')

def identify_hard_images():
    # Load original v1 dataset
    with open('params.yaml', 'r') as f:
        params = yaml.safe_load(f)

    # Set dataset version to v1 temporarily
    params['dataset_version'] = 'v1'
    with open('params.yaml', 'w') as f:
        yaml.dump(params, f)

    # Run pull_data.py to get v1 dataset
    os.system('python pull_data.py')

    # Load v1 images and labels
    v1_images = np.load('data/images.npy')
    v1_labels = np.load('data/labels.npy')

    # Load predictions from different models
    v1_preds = np.load('evaluation/y_pred_v1.npy')
    v1_v2_preds = np.load('evaluation/y_pred_v1+v2.npy')
    v1_v2_v3_preds = np.load('evaluation/y_pred_v1+v2+v3.npy')

    # Find hard-to-learn images (misclassified by all models)
    hard_indices = []
    for i in range(len(v1_labels)):
        if (v1_preds[i] != v1_labels[i] and 
            v1_v2_preds[i] != v1_labels[i] and 
            v1_v2_v3_preds[i] != v1_labels[i]):
            hard_indices.append(i)

    logger.info(f"Found {len(hard_indices)} hard-to-learn images")

    # Analyze class distribution of hard-to-learn images
    class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer', 
                   'dog', 'frog', 'horse', 'ship', 'truck']

    hard_labels = v1_labels[hard_indices]
    class_counts = np.bincount(hard_labels, minlength=10)

    # Plot class distribution
    plt.figure(figsize=(12, 6))
    sns.barplot(x=class_names, y=class_counts)
    plt.title('Class Distribution of Hard-to-Learn Images')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('evaluation/hard_images_class_distribution.png')

    # Create misclassification table
    misclass_table = np.zeros((10, 10), dtype=int)
    for i in hard_indices:
        true_label = v1_labels[i]
        # Use v1+v2+v3 model predictions for the misclassification table
        pred_label = v1_v2_v3_preds[i]
        misclass_table[true_label][pred_label] += 1

    # Plot misclassification table as heatmap
    plt.figure(figsize=(12, 10))
    sns.heatmap(misclass_table, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names)
    plt.xlabel('Predicted Class')
    plt.ylabel('True Class')
    plt.title('Misclassification Table for Hard-to-Learn Images')
    plt.tight_layout()
    plt.savefig('evaluation/hard_images_misclassification_table.png')

    # Save hard-to-learn images indices for further analysis
    np.save('evaluation/hard_images_indices.npy', np.array(hard_indices))

    logger.info("Hard-to-learn images analysis completed.")

if __name__ == "__main__":
    identify_hard_images()
