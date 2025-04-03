# CIFAR-10 Image Classification with DVC Pipeline

This project implements a complete MLOps pipeline for training and evaluating CNN models on the CIFAR-10 dataset using DVC (Data Version Control).

## Project Structure

```
├── cifar10_dataset/           # Original CIFAR-10 dataset with class folders
├── dataset_partitions/        # Dataset partitions tracked by DVC
│   ├── v1/                    # First 20k images
│   ├── v2/                    # Second 20k images
│   ├── v3/                    # Third 20k images
├── data/                      # Processed data
│   ├── prepared/              # Train/val/test splits
├── models/                    # Trained models
├── evaluation/                # Evaluation results
├── experiments/               # Experiment tracking
├── *.py                       # Pipeline scripts
├── params.yaml                # Hyperparameters
├── dvc.yaml                   # DVC pipeline definition
```


## Pipeline Stages

1. **pull_data.py**: Loads data from dataset partitions based on version in params.yaml
2. **prepare_data.py**: Creates train/val/test splits
3. **train_model.py**: Builds and trains CNN with hyperparameter tuning
4. **evaluate_model.py**: Evaluates model performance and generates metrics
5. **identify_hard_images.py**: Analyzes hard-to-learn images (brownie task)

## Running the Pipeline

```bash
# Run full pipeline
dvc repro

# Run experiments with different dataset versions and seeds
python run_experiments.py

# Analyze hard-to-learn images
python identify_hard_images.py
```


## Experiments

I ran experiments with different dataset combinations:

- v1: First 20k images
- v2: Second 20k images
- v3: Third 20k images
- v1+v2: Combined 40k images
- v1+v2+v3: All 60k images

Each experiment used multiple random seeds (42, 123, 456) to ensure reproducibility.

## Results

The model achieved best performance when trained on the full dataset (v1+v2+v3), with cats and dogs being the most challenging classes to classify correctly.

Analysis of hard-to-learn images revealed common patterns in misclassifications, which could guide future model improvements.