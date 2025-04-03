import numpy as np
import tensorflow as tf
from tensorflow.keras.datasets import cifar10
import os
from PIL import Image

# Create directories for each class
classes = ['airplane', 'automobile', 'bird', 'cat', 'deer', 
           'dog', 'frog', 'horse', 'ship', 'truck']

# Load CIFAR-10 dataset
(x_train, y_train), (x_test, y_test) = cifar10.load_data()
x_all = np.concatenate([x_train, x_test])
y_all = np.concatenate([y_train, y_test]).flatten()

# Create base directory
base_dir = 'cifar10_dataset'
os.makedirs(base_dir, exist_ok=True)

# Create class directories and save images
for class_idx, class_name in enumerate(classes):
    class_dir = os.path.join(base_dir, class_name)
    os.makedirs(class_dir, exist_ok=True)
    
    # Get indices for current class
    indices = np.where(y_all == class_idx)[0]
    
    # Save images
    for i, idx in enumerate(indices):
        img = Image.fromarray(x_all[idx])
        img.save(os.path.join(class_dir, f'{class_name}_{i}.png'))

print("Dataset organized into class folders successfully!")
