import numpy as np
import torch
from torch.utils.data import Dataset

class RollingStandardScaler:
    def __init__(self, eps=1e-6):
        self.mean_ = None
        self.std_ = None
        self.eps = eps
    def fit(self, X: np.ndarray):
        self.mean_ = X.mean(axis=0)
        self.std_ = X.std(axis=0) + self.eps
        return self
    def transform(self, X: np.ndarray):
        return (X - self.mean_) / self.std_

class SeqDataset(Dataset):
    def __init__(self, feats: np.ndarray, labels: np.ndarray, seq_len: int):
        self.X = feats
        self.y = labels
        self.seq_len = seq_len
    def __len__(self): 
        return max(0, len(self.X) - self.seq_len)
    def __getitem__(self, idx):
        x = self.X[idx:idx+self.seq_len]
        y = self.y[idx+self.seq_len-1]
        return torch.from_numpy(x).float(), torch.tensor(y).long()
