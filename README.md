# Machine Learning for Model Driven Engineering 2025 project
### Authors: Calogero Carlino, Luca Francesco Macera

## Introduction
The goal of this project is to build a machine learning pipeline to auto-
matically classify source code comments into predefined categories. This task
presents several challenges, including short and ambiguous text, semantic over-
lap between categories, and class imbalance.
---

## How to Run

### 1. Environment Setup
Ensure you have **Python 3.9+** and a GPU (recommended) available.

```bash
# Clone the repository
git clone [https://github.com/LucaFraMacera/ML4SE-2025-Project.git](https://github.com/LucaFraMacera/ML4SE-2025-Project.git)
cd ML4SE-2025-Project

# Set up the environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Running the project
### 2.1 Run the complete pipeline
You can run the whole pipeline starting from the dataset cleaning all the way to the model training
by executing
```bash
jupyter notebook complete-pipeline.ipynb
```
### 2.2 Run each step independently
Make sure to run them sequentially as each step uses the output of the previous one.
```bash
# 1. Clean data and merge categories
jupyter notebook data_cleaning.ipynb

# 2. Encode features
jupyter notebook encoding.ipynb

# 3. Train baseline model
jupyter notebook model_training.ipynb

# 4. Compare multiple models
jupyter notebook multi_model_training.ipynb

# 5. View results summary
jupyter notebook results_summary.ipynb
```

### 3 Load and use the trained model
To use the model to predict on new data, update the raw_data variable in the script *main.py* and run:
```bash
cd utils
python main.py
```