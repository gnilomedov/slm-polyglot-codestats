from loguru import logger
from tabulate import tabulate
import pandas as pd

import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from transformers import get_linear_schedule_with_warmup


def model_summary(model: nn.Module) -> str:
    '''Compose summary of the model including total parameters and per-layer parameters.'''
    total_params = 0
    layer_params = {}
    for name, param in model.named_parameters():
        total_params += param.numel()
        layer_name = name.split('.')[0]
        if layer_name not in layer_params:
            layer_params[layer_name] = 0
        layer_params[layer_name] += param.numel()

    table_data = [(layer, f'{params / 1e6:.2f}M') for layer, params in layer_params.items()]
    table_data.append(('Total', f'{total_params / 1e6:.2f}M'))
    table_df = pd.DataFrame(table_data, columns=['Layer', 'Parameters'])
    return tabulate(table_df, headers='keys', tablefmt='presto', showindex=False)


def train_model(model: nn.Module, data_loader: DataLoader, optimizer: optim.Optimizer,
                num_epochs: int) -> None:
    '''Train the given model on the provided dataset.

    :param model: The model to be trained.
    :param data_loader: The data loader providing batches of training data.
    :param optimizer: The optimizer used for weight updates.
    :param num_epochs: The number of training epochs.
    '''
    num_training_steps = len(data_loader) * num_epochs
    # Warmup steps (10% of total) to gradually increase the learning rate and stabilize training
    num_warmup_steps = num_training_steps // 10
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=num_warmup_steps,
                                                num_training_steps=num_training_steps)
    model.train()
    logger.info(f'Will run {num_epochs} epochs ...')
    for epoch in range(num_epochs):
        total_loss = 0
        for batch in data_loader:
            outputs = model(**batch)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()
            total_loss += loss.item()
        logger.info(f'Epoch {epoch + 1}/{num_epochs}, loss {total_loss / len(data_loader):.4f}')
