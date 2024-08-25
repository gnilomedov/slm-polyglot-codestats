import random

import torch
from torch.utils.data import Dataset
from transformers import PreTrainedTokenizer


class MultiFileContentCodeDataset(Dataset):
    '''Dataset for tokenized code snippets using sliding window with shifted labels.'''

    def __init__(self, file_contents: list[tuple[str, str]], tokenizer: PreTrainedTokenizer,
                 seq_length: int = 48):
        '''
        :param file_contents: List of (file_path, file_content_text).
        :param tokenizer: Tokenizer to process the content.
        :param seq_length: Length of sequences to be used for training.
        '''
        self._seq_length = seq_length
        self._tokenized_contents = []
        file_lengths = []
        for _, content in file_contents:
            tokenized = (tokenizer(content, return_tensors='pt')['input_ids']
                             .squeeze(0)) # Remove 1st dim of the tensor
            self._tokenized_contents.append(tokenized)
            # Subtract (seq_length-1) to fit the sliding window and subtract 1 to fit the last label
            #   => -= (seq_length-1) - 1 equivalent to -= seq_length
            train_input_length = max(0, len(tokenized) - seq_length)
            file_lengths.append(train_input_length)
        # Calculate cumulative lengths for efficient indexing
        self._cumulative_lengths = torch.cumsum(torch.tensor([0] + file_lengths), dim=0)
        self._reshuffled_indices: list[int] | None = None

    def shuffle_and_cap(self, length: int) -> None:
        '''Shuffle indices and cap the dataset length.

        :param length: The number of items to include after shuffling and capping.
        '''
        total_length = self._cumulative_lengths[-1].item()
        all_indices = list(range(total_length))
        random.shuffle(all_indices)
        self._reshuffled_indices = all_indices[:length]

    def __len__(self) -> int:
        '''Return the total number of valid sliding windows across all files.'''
        if self._reshuffled_indices is not None:
            return len(self._reshuffled_indices)
        return self._cumulative_lengths[-1].item()

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        '''Get a single item from the dataset.

        :param idx: Index of the item to retrieve.
        :return: Dictionary of tensors representing the tokenized input and shifted labels.
        '''
        if self._reshuffled_indices is not None:
            idx = self._reshuffled_indices[idx]

        file_idx = torch.searchsorted(self._cumulative_lengths, idx, right=True) - 1
        local_idx = idx - self._cumulative_lengths[file_idx].item()
        tokenized = self._tokenized_contents[file_idx]
        input_ids = tokenized[local_idx:local_idx + self._seq_length]
        labels = tokenized[local_idx + 1:local_idx + self._seq_length + 1]

        return {'input_ids': input_ids,
                'labels': labels}  # 'attention_mask': torch.ones_like(input_ids),
