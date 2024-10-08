# -*- coding: utf-8 -*-
"""240417 Different Eval

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1vHbAuozJC46ikps9WIVeU7fUUhm54Axz

#Recall the Data from Previous Code(Same with 240308 YB Voting_modeling)

##Recall the Data
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.datasets as datasets
import torchvision.transforms as transforms
import random
from torch.utils.data import Dataset, DataLoader
import pandas as pd
!pip install pandas numpy scikit-learn tensorflow
import pandas as pd
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np

print(torch.__version__)

from google.colab import drive
drive.mount('/content/drive')

finaldata = pd.read_csv("/content/drive/MyDrive/capstone_yb/Voting ML/DATA/cleaned_finaldata.csv")

X = finaldata.drop(columns=['Geography', 'Geographic Area Name','Biden_proportion','Estimate!!Households!!Median income (dollars)','Vote Count', 'Precinct','County',
                            'Estimate!!Families!!Median income (dollars)','Estimate!!Nonfamily households!!Median income (dollars)', 'Estimate!!Married-couple families!!Median income (dollars)'])
X = X.astype(float)
X.dtypes

y = finaldata['Biden_proportion']

import copy
import tqdm
from sklearn.model_selection import train_test_split


# train-test split of the dataset / chaning split of data to Pytorch
X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.7, shuffle=True)
X_train = torch.tensor(X_train.values, dtype=torch.float32)
y_train = torch.tensor(y_train.values, dtype=torch.float32).reshape(-1, 1)
X_test = torch.tensor(X_test.values, dtype=torch.float32)
y_test = torch.tensor(y_test.values, dtype=torch.float32).reshape(-1, 1)

print(X_train.shape)
print(y_train.shape)

"""##Simple NN"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# Define the neural network class
'''class SimpleNN(nn.Module):
    def __init__(self):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(20, 32)
        self.fc2 = nn.Linear(32, 1)
        self.relu = nn.ReLU()''from sklearn.model_selection import train_test_split'''

class DeepNN(nn.Module):
    def __init__(self):
        super(DeepNN, self).__init__()
        self.fc1 = nn.Linear(20, 32)  # Input layer
        self.bn1 = nn.BatchNorm1d(32)  # Batch normalization after first linear layer
        self.fc2 = nn.Linear(32, 64)  # First hidden layer
        self.bn2 = nn.BatchNorm1d(64)  # Batch normalization after second linear layer
        self.dropout = nn.Dropout(0.5)  # Dropout for regularization
        self.fc3 = nn.Linear(64, 64)  # Second hidden layer
        self.bn3 = nn.BatchNorm1d(64)  # Batch normalization after third linear layer
        self.fc4 = nn.Linear(64, 1)    # Output layer
        self.relu = nn.ReLU()  # ReLU activation used throughout

    def forward(self, x):
        x = self.relu(self.bn1(self.fc1(x)))  # Activation -> BatchNorm
        x = self.relu(self.bn2(self.fc2(x)))  # Activation -> BatchNorm
        x = self.dropout(x)  # Applying dropout after activation
        x = self.relu(self.bn3(self.fc3(x)))  # Activation -> BatchNorm
        x = self.fc4(x)  # Output layer does not need activation if regression
        return x

# Instantiate the model
model = DeepNN()

county_info = finaldata['County'].unique().tolist()
len(county_info)

class CountyDataset(Dataset): #classcification
    def __init__(self, finaldata):
        f =  finaldata.drop(columns=['Geography', 'Geographic Area Name','Biden_proportion','Estimate!!Households!!Median income (dollars)','Vote Count', 'Precinct','County',
                            'Estimate!!Families!!Median income (dollars)','Estimate!!Nonfamily households!!Median income (dollars)', 'Estimate!!Married-couple families!!Median income (dollars)']).astype(float)
        self.X = f.values.tolist()
        self.y = finaldata['Biden_proportion'].tolist()
        self.county_info = finaldata['County'].tolist()

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return torch.tensor(self.X[idx], dtype=torch.float32), torch.tensor(self.y[idx], dtype=torch.float32), self.county_info[idx]

dataset = CountyDataset(finaldata)

class CountyDataLoader: #load the data with county
    def __init__(self, dataset, random_state=None):
        self.dataset = dataset
        self.counties = list(set(dataset.county_info))
        self.random_state = random_state

    def __iter__(self): #load the data with each county
        for county in self.counties:
            county_indices = [i for i, c in enumerate(self.dataset.county_info) if c == county]
            batch_X = [self.dataset.X[i] for i in county_indices]
            batch_y = [self.dataset.y[i] for i in county_indices]
            yield batch_X, batch_y

county_dataloader = CountyDataLoader(dataset)

# Define the custom loss function
def custom_loss(predictions, county_statistics):
    # Calculate the average prediction within the batch
    avg_prediction = torch.mean(predictions)

    # Assume county_statistics is a tuple containing the required statistics (e.g., Biden proportion)
    biden_proportion = county_statistics[0]

    # Calculate the MSE loss(Mean Squared Error)
    mse_loss = nn.MSELoss()(avg_prediction, biden_proportion)

    return mse_loss

# Define the loss function
class LossFunction(nn.Module):
    def __init__(self):
        super(LossFunction, self).__init__()

    def forward(self, predictions, mean_l): #calculate MSE
        mean_p = torch.mean(predictions)
        mean_l = torch.tensor(mean_l, dtype=torch.float32)

        return torch.square(mean_p - mean_l)

"""##Optimizer: SGD"""

optimizer = torch.optim.SGD(model.parameters(), lr=0.001)
import torch
num_epochs = 500
losses = []
for epoch in range(num_epochs):
    for i,(train_X, train_y)  in enumerate(county_dataloader):
      epoch_loss = 0.0
      if i<32:

        # Convert lists to PyTorch tensors
        features = torch.tensor(train_X)
        target = torch.tensor(train_y)

        # Forward pass, loss computation, and backward pass
        outputs = model(features)
        # print(outputs) # issue here
        loss = custom_loss(outputs, target)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        epoch_loss += loss.item()
        average_epoch_loss = epoch_loss /50
       # losses.append(loss.item())
        losses.append(average_epoch_loss)

    if epoch % 10 == 0:
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item()}')

import matplotlib.pyplot as plt

plt.plot(losses[10:], label='Training Loss') #The code plots only the data points for the training loss after excluding the first 10 epochs.
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()

model.eval()

"""#Different Evaluation: Model evaluation metrics:
1. Cross-validation
2. RMSE on tract-level data, MAE
3. R^2



"""

import numpy as np
import time
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# 초기화
rmse_scores = []
mae_scores = []
r2_scores = []
num_batches = 0
losses = []
timestamps = []

for i, (val_X, val_y) in enumerate(county_dataloader):
    if i >= 32:
        start_time = time.time()

        features = torch.tensor(val_X)
        target = torch.tensor(val_y)

        model.train()
        outputs = model(features)

        # Loss
        loss = custom_loss(outputs, target)
        losses.append(loss.item())

        # RMSE, MAE, R^2
        actuals = target.cpu().numpy()  # Actual
        predictions = outputs.detach().cpu().numpy()  # Prediction
        rmse_scores.append(np.sqrt(mean_squared_error(actuals, predictions)))
        mae_scores.append(mean_absolute_error(actuals, predictions))
        r2_scores.append(r2_score(actuals, predictions))

        # Optimizer backing and Zero
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # Recoding the time
        end_time = time.time()
        timestamps.append(end_time - start_time)
        num_batches += 1

# Evaluation
print("Average RMSE:", np.mean(rmse_scores))
print("Average MAE:", np.mean(mae_scores))
print("Average R^2:", np.mean(r2_scores))

# Plotting the loss versus time for both training and test data
plt.plot(timestamps, losses, marker='o')
plt.xlabel('Time (seconds)')
plt.ylabel('Loss')
plt.title('Loss Versus Time for Test Data')

from torch.utils.data import DataLoader, Subset
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Prepare the dataset (using the previously defined CountyDataset class)
dataset = CountyDataset(finaldata)  # Using the dataset defined earlier

# Set up K-Fold cross-validation
kf = KFold(n_splits=5, shuffle=True, random_state=42)  # 5-fold cross-validation

# Lists to store cross-validation results
cv_results = {'rmse': [], 'mae': [], 'r2': []}

# Train and validate across each fold
for fold, (train_idx, val_idx) in enumerate(kf.split(dataset)):
    # Split dataset
    train_subs = Subset(dataset, train_idx)
    val_subs = Subset(dataset, val_idx)

    # Create data loaders
    train_loader = DataLoader(train_subs, batch_size=10, shuffle=True)
    val_loader = DataLoader(val_subs, batch_size=10)

    # Initialize the model
    model = DeepNN()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.001)

    # Train the model
    for epoch in range(100):  # For simplicity, training for 100 epochs
        model.train()
        for X_batch, y_batch, _ in train_loader:
            optimizer.zero_grad()
            output = model(X_batch)
            loss = torch.nn.functional.mse_loss(output, y_batch)
            loss.backward()
            optimizer.step()

    # Evaluate the model on the validation set
    model.eval()
    val_rmse, val_mae, val_r2 = [], [], []
    with torch.no_grad():
        for X_batch, y_batch, _ in val_loader:
            output = model(X_batch)
            val_rmse.append(np.sqrt(mean_squared_error(y_batch.numpy(), output.numpy())))
            val_mae.append(mean_absolute_error(y_batch.numpy(), output.numpy()))
            val_r2.append(r2_score(y_batch.numpy(), output.numpy()))

    # Calculate and store average scores
    cv_results['rmse'].append(np.mean(val_rmse))
    cv_results['mae'].append(np.mean(val_mae))
    cv_results['r2'].append(np.mean(val_r2))

    print(f'Fold {fold+1} - RMSE: {cv_results["rmse"][-1]}, MAE: {cv_results["mae"][-1]}, R^2: {cv_results["r2"][-1]}')

# Print average scores across all folds
print(f"Average RMSE across folds: {np.mean(cv_results['rmse'])}")
print(f"Average MAE across folds: {np.mean(cv_results['mae'])}")
print(f"Average R^2 across folds: {np.mean(cv_results['r2'])}")

merged_df = pd.read_csv("/content/drive/MyDrive/processed_data.csv")

class CountyDataset2(Dataset):
    def __init__(self, finaldata):
        f =  finaldata.drop(columns=['Geography', 'Geographic Area Name','Precinct','County', 'Vote Count','Estimate!!Households!!Median income (dollars)','average_Biden_proportion',
                            'Estimate!!Families!!Median income (dollars)','Estimate!!Nonfamily households!!Median income (dollars)', 'Estimate!!Married-couple families!!Median income (dollars)']).astype(float)
        self.X = f.values.tolist()
        self.y = finaldata['average_Biden_proportion'].tolist()
        self.county_info = finaldata['County'].tolist()

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return torch.tensor(self.X[idx], dtype=torch.float32), torch.tensor(self.y[idx], dtype=torch.float32), self.county_info[idx]

dataset_evaluation = CountyDataset2(merged_df)
county_dataloader2 = CountyDataLoader(dataset_evaluation)

# Initialization
rmse_scores = []
mae_scores = []
r2_scores = []
num_batches = 0
losses1 = [] # Use losses1 instead of losses
timestamps1 = [] # Use timestamps1 instead of timestamps

for i, (val_X, val_y) in enumerate(county_dataloader2):
    if i >= 32:
        start_time = time.time()

        features = torch.tensor(val_X)
        target = torch.tensor(val_y)

        model.train()
        outputs = model(features)

        # Loss
        loss = custom_loss(outputs, target)
        losses1.append(loss.item()) # Store loss in losses1

        # RMSE, MAE, R^2
        actuals = target.cpu().numpy()  # Actual
        predictions = outputs.detach().cpu().numpy()  # Prediction
        rmse_scores.append(np.sqrt(mean_squared_error(actuals, predictions)))
        mae_scores.append(mean_absolute_error(actuals, predictions))
        r2_scores.append(r2_score(actuals, predictions))

        # Optimizer backing and Zero
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # Recoding the time
        end_time = time.time()
        timestamps1.append(end_time - start_time)  # Store time in timestamps1
        num_batches += 1

# Evaluation
print("Average RMSE:", np.mean(rmse_scores))
print("Average MAE:", np.mean(mae_scores))
print("Average R^2:", np.mean(r2_scores))

# Plotting the loss versus time
plt.plot(timestamps1, losses1, marker='o')
plt.xlabel('Time (seconds)')
plt.ylabel('Loss')
plt.title('Loss Versus Time for Evaluation Data')
plt.show()