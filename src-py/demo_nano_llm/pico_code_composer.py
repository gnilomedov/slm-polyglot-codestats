import textwrap

from loguru import logger
from types import SimpleNamespace

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

from demo_nano_llm.language_sequence_code_composer import LanguageSequenceCondeComposer
from demo_nano_llm.multi_file_content_code_dataset import MultiFileContentCodeDataset
from demo_nano_llm.simple_tokenizer import SimpleTokenizer
from demo_nano_llm.utils import model_summary, train_model


class PicoCondeComposer(LanguageSequenceCondeComposer):
    '''A lightweight code generation model based on an LSTM.'''

    def __init__(self):
        super().__init__()
        self._tokenizer = SimpleTokenizer()
        self._model: _PicoLSTM | None = None

    def get_model_summary(self) -> str:
        if not self._model:
            return 'Empty'
        honeybee = ''.join([f'\033[93m{c}' if i % 2 == 0 else f'\033[90m{c}'
                            for i, c in enumerate('honeybee')]) + '\033[35m'
        disclaimer = textwrap.dedent(f'''\
            Disclaimer: This model's code output is like what you'd get if a
            {honeybee} could learn programming in 5 minutes—basic and not sophisticated.
            Animals typically don't write code; most of their brain power is devoted to
            controlling movements, recognizing food, processing smells, and other vital needs.''')
        return f'\033[35m{disclaimer}\n\033[94m{model_summary(self._model)}\033[0m'

    def fit_model(self, file_contents: list[tuple[str, str]], num_epochs: int = 10,
                  batch_size: int = 32, learning_rate: float = 12e-4) -> None:
        self._tokenizer.fit(content for _, content in file_contents)
        self._model = _PicoLSTM(vocab_size=self._tokenizer.vocab_size)
        code_dataset = MultiFileContentCodeDataset(file_contents, self._tokenizer)
        logger.info(
            f'Tokenizer fit files {len(file_contents)} '
            f'code tokens {len(code_dataset)} vocab {self._tokenizer.vocab_size}')
        data_loader = DataLoader(code_dataset, batch_size=batch_size, shuffle=True)
        train_model(self._model, data_loader,
                    optim.Adam(self._model.parameters(), lr=learning_rate),
                    num_epochs)

    def compose_code(self, code_text_begin: str, max_length=16) -> str:
        self._model.eval()
        with torch.no_grad():
            current_ids = torch.tensor(self._tokenizer.encode(code_text_begin)).unsqueeze(0)
            for _ in range(max_length):
                outputs = self._model(current_ids)
                next_token_id = outputs.logits[0, -1, :].argmax().item()
                current_ids = torch.cat([current_ids, torch.tensor([[next_token_id]])], dim=1)
                if next_token_id == self._tokenizer.pad_token_id:
                    break
        return self._tokenizer.decode(current_ids.squeeze().tolist())


class _PicoLSTM(nn.Module):
    '''LSTM-based model for code generation, extremely lightweight to train and infer on CPU.'''

    def __init__(self, vocab_size: int, embedding_dim: int = 32, hidden_dim: int = 128,
                 num_layers: int = 3):
        '''
        :param vocab_size: Size of the vocabulary.
        :param embedding_dim: Dimension of the token embeddings.
        :param hidden_dim: Dimension of the hidden state in LSTM layers.
        :param num_layers: Number of LSTM layers.
        '''
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)
        self.criterion = nn.CrossEntropyLoss()

    def forward(self, input_ids: torch.Tensor, labels: torch.Tensor = None, **kwargs):
        '''Forward pass of the model.

        :param input_ids: Input tensor of token indices.
        :param labels: (optional) Target tensor of token indices.
        :return: A named tuple containing the output logits and (optionally) the loss.
        '''
        embedded = self.embedding(input_ids)
        lstm_out, _ = self.lstm(embedded)
        logits = self.fc(lstm_out)
        outputs = SimpleNamespace(logits=logits)
        if labels is not None:
            loss = self.criterion(logits.view(-1, logits.size(-1)), labels.view(-1))
            outputs.loss = loss
        return outputs
