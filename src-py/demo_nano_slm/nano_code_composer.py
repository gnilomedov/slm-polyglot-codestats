import textwrap

from loguru import logger

import torch
from torch.optim import AdamW
from torch.utils.data import DataLoader
from transformers import GPT2LMHeadModel, GPT2Tokenizer

from demo_nano_slm.language_sequence_code_composer import LanguageSequenceCondeComposer
from demo_nano_slm.multi_file_content_code_dataset import MultiFileContentCodeDataset
from demo_nano_slm.utils import model_summary, train_model


class NanoCondeComposer(LanguageSequenceCondeComposer):
    '''GPT-2 based code generation model for training and text completion.'''

    def __init__(self, pretrained_model_name='microsoft/CodeGPT-small-py'):
        super().__init__()
        self._tokenizer = GPT2Tokenizer.from_pretrained(pretrained_model_name,
                                                        clean_up_tokenization_spaces=True)
        self._model = GPT2LMHeadModel.from_pretrained(pretrained_model_name)

    def get_model_summary(self) -> str:
        disclaimer = textwrap.dedent('''\
            Disclaimer: This model's code output is like what you'd get if a rat\033[90m
                          \033[93m   __\033[90m
                 (\\__/)   \033[93m  /  \\\033[90m
                 (o.o)    \033[93m /o . \\\033[90m
                  " "     \033[93m/  o O \\\033[90m
            \\____(")(")   \033[93m\\_._O_./\033[35m
            could learn programming overnight—basic and not sophisticated.
            Animals typically don't write code; most of their brain power is devoted to
            controlling movements, recognizing food, processing smells, and other vital needs.''')
        return f'\033[35m{disclaimer}\n\033[94m{model_summary(self._model)}\033[0m'

    def fit_model(self, file_contents: list[tuple[str, str]],
                  num_epochs: int = 8, batch_size: int = 16, learning_rate: float = 1e-5) -> None:
        code_dataset = MultiFileContentCodeDataset(file_contents, self._tokenizer)
        code_dataset.shuffle_and_cap(16) # Shrink the dataset to optimize finetune time.
        logger.info(
            f'Tokenizer fit files {len(file_contents)} '
            f'code tokens {len(code_dataset)} vocab {self._tokenizer.vocab_size}')
        data_loader = DataLoader(code_dataset, batch_size=batch_size, shuffle=True)
        optimizer = AdamW(self._model.parameters(), lr=learning_rate)

        train_model(self._model, data_loader, optimizer, num_epochs)

    def compose_code(self, code_text_begin: str, max_length: int = 16) -> str:
        self._model.eval()
        input_ids = self._tokenizer.encode(code_text_begin, return_tensors='pt')
        with torch.no_grad():
            output = self._model.generate(input_ids, max_length=max_length, num_return_sequences=1)
            return self._tokenizer.decode(output[0], skip_special_tokens=True)
