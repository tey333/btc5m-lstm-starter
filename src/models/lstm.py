import torch
import torch.nn as nn

class LSTMClf(nn.Module):
    def __init__(self, in_ch: int, hidden: int=64, layers: int=2, num_classes: int=3):
        super().__init__()
        self.lstm = nn.LSTM(input_size=in_ch, hidden_size=hidden, num_layers=layers, batch_first=True)
        self.head = nn.Linear(hidden, num_classes)
    def forward(self, x):
        out, _ = self.lstm(x)   # [B,T,F] -> [B,T,H]
        h = out[:, -1, :]       # last step
        return self.head(h)     # [B,C]
