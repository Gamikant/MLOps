import random
import shutil
import subprocess
import os

classes = ['airplane', 'automobile', 'bird', 'cat', 'deer',
           'dog', 'frog', 'horse', 'ship', 'truck']

base_dir = 'cifar10_dataset'
partitions_dir = 'dataset_partitions'
os.makedirs(partitions_dir, exist_ok=True)

# Get all image paths
all_images = []
for class_name in classes:
    class_dir = os.path.join(base_dir, class_name)
    for img_name in os.listdir(class_dir):
        all_images.append(os.path.join(class_dir, img_name))

# Shuffle images
random.seed(42)
random.shuffle(all_images)

# Create three partitions (20000 images each)
partitions = [
    {'name': 'v1', 'images': all_images[:20000]},
    {'name': 'v2', 'images': all_images[20000:40000]},
    {'name': 'v3', 'images': all_images[40000:60000]}
]

# Copy images to partition directories
for partition in partitions:
    partition_dir = os.path.join(partitions_dir, partition['name'])
    os.makedirs(partition_dir, exist_ok=True)
    
    # Create class directories
    for class_name in classes:
        os.makedirs(os.path.join(partition_dir, class_name), exist_ok=True)
    
    # Copy images
    for img_path in partition['images']:
        class_name = os.path.basename(os.path.dirname(img_path))
        dest_dir = os.path.join(partition_dir, class_name)
        shutil.copy(img_path, dest_dir)
    
    # Track the partition with DVC
    subprocess.run(['dvc', 'add', partition_dir])
    
    # Add the .dvc file to Git
    subprocess.run(['git', 'add', f'{partition_dir}.dvc'])
    subprocess.run(['git', 'commit', '-m', f'Add {partition["name"]} dataset'])

print("Partitions created and pushed to DVC successfully!")
