import yaml
import os
import numpy as np
from PIL import Image
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('pipeline.log'), logging.StreamHandler()]
)
logger = logging.getLogger('pull_data')

def pull_data():
    # Load parameters
    with open('params.yaml', 'r') as f:
        params = yaml.safe_load(f)
    
    dataset_version = params['dataset_version']
    random_seed = params['random_seed']
    np.random.seed(random_seed)
    
    logger.info(f"Pulling dataset version: {dataset_version}")
    
    # Pull data from partitions
    versions = dataset_version.split('+')
    all_images = []
    all_labels = []
    
    for version in versions:
        logger.info(f"Processing version: {version}")
        
        # Load images and labels from the partition
        for class_idx, class_name in enumerate(['airplane', 'automobile', 'bird', 'cat', 'deer', 
                                               'dog', 'frog', 'horse', 'ship', 'truck']):
            class_dir = os.path.join('dataset_partitions', version, class_name)
            if os.path.exists(class_dir):
                for img_name in os.listdir(class_dir):
                    img_path = os.path.join(class_dir, img_name)
                    try:
                        img = np.array(Image.open(img_path))
                        all_images.append(img)
                        all_labels.append(class_idx)
                    except Exception as e:
                        logger.error(f"Error loading image {img_path}: {e}")
    
    # Convert to numpy arrays
    X = np.array(all_images)
    y = np.array(all_labels)
    
    # Save as numpy arrays
    os.makedirs('data', exist_ok=True)
    np.save('data/images.npy', X)
    np.save('data/labels.npy', y)
    
    logger.info(f"Dataset pulled successfully with {len(X)} images")

if __name__ == "__main__":
    pull_data()
