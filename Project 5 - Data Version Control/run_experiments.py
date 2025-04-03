import subprocess
import yaml
import os
import logging
import shutil

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('experiments.log'), logging.StreamHandler()]
)
logger = logging.getLogger('run_experiments')

# Dataset versions to test
dataset_versions = ['v1', 'v2', 'v3', 'v1+v2', 'v1+v2+v3']

# Random seeds to use
random_seeds = [42, 123, 456]

os.makedirs('experiments', exist_ok=True)

# All experiments
for seed in random_seeds:
    for version in dataset_versions:
        logger.info(f"Running experiment with seed={seed}, version={version}")
        
        # Update params.yaml
        with open('params.yaml', 'r') as f:
            params = yaml.safe_load(f)
        
        params['random_seed'] = seed
        params['dataset_version'] = version
        
        with open('params.yaml', 'w') as f:
            yaml.dump(params, f)
        
        # Run DVC pipeline
        exp_name = f"seed{seed}_{version}"
        try:
            subprocess.run(['dvc', 'repro'], check=True)
            logger.info(f"Pipeline completed successfully for {exp_name}")
            
            # Copy results to experiments directory
            os.makedirs(f'experiments/{exp_name}', exist_ok=True)
            if os.path.exists(f'evaluation/confusion_matrix_{version}.png'):
                shutil.copy(f'evaluation/confusion_matrix_{version}.png', f'experiments/{exp_name}/')
            if os.path.exists(f'evaluation/classification_report_{version}.txt'):
                shutil.copy(f'evaluation/classification_report_{version}.txt', f'experiments/{exp_name}/')
            
            # Save experiment as DVC experiment
            subprocess.run(['dvc', 'exp', 'save', '-n', exp_name], shell=True)
            logger.info(f"Saved experiment {exp_name}")
        except Exception as e:
            logger.error(f"Error running experiment {exp_name}: {e}")

logger.info("All experiments completed. Use 'dvc exp show' to compare results.")
