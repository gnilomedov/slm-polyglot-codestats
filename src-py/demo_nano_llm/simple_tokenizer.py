from collections import Counter
import re
from typing import Generator, Iterable

import torch


class SimpleTokenizer:
    '''A tokenizer for code that handles newlines, indentation blocks, and braces.'''

    def __init__(self) -> None:
        self._vocab: list[str] = None
        self._token_to_id: dict[str, int] = None
        self._id_to_token: dict[int, str] = None

    def fit(self, texts: Iterable[str]) -> None:
        '''Fit the tokenizer on the given texts.

        :param texts: Code snippets to fit the tokenizer on.
        '''
        token_counts = Counter(token for text in texts for token in self._tokenize(text))
        self._vocab = (['<PAD>', '<UNK>', '<NEWLINE>', '<INDENT>'] +
                       [token for token, _ in token_counts.most_common()])
        self._token_to_id = {token: i for i, token in enumerate(self._vocab)}
        self._id_to_token = {i: token for token, i in self._token_to_id.items()}

    def __call__(self, text: str, return_tensors: str | None = None) -> (
            dict[str, list[int] | torch.Tensor]):
        '''Tokenize the input text and return a dictionary with input_ids.'''
        input_ids = self.encode(text)
        if return_tensors == 'pt':
            return {'input_ids': torch.tensor([input_ids])}
        return {'input_ids': input_ids}

    def encode(self, text: str) -> list[int]:
        '''Encode a text string into a list of token IDs.

        :param text: Input text to encode.
        :return: List of token IDs.
        '''
        return [self._token_to_id.get(token, self._token_to_id['<UNK>'])
                for token in self._tokenize(text)]

    def decode(self, ids: list[int]) -> str:
        '''Decode a list of token IDs into a text string.

        :param ids: List of token IDs to decode.
        :return: Decoded text with proper indentation and newlines.
        '''
        tokens = [self._id_to_token[id] for id in ids]
        text = ''
        for token in tokens:
            if token == '<NEWLINE>':
                text += '\n'
            elif token == '<INDENT>':
                text += '    '
            else:
                text += token
        return text.rstrip()

    @property
    def vocab_size(self) -> int:
        return len(self._vocab)

    @property
    def pad_token_id(self) -> int:
        return self._token_to_id['<PAD>']

    def _tokenize(self, text: str) -> Generator[str, None, None]:
        lines = text.split('\n')
        for line in lines:
            indent_level = 0
            while line.startswith('    '):
                indent_level += 1
                line = line[4:]
                yield '<INDENT>'
            yield from self._tokenize_line(line)
            yield '<NEWLINE>'

    @staticmethod
    def _tokenize_line(line: str) -> Generator[str, None, None]:
        separators_str = ' :;.,\'"{}[]()'
        separators_re = '(' + '|'.join([re.escape(char) for char in separators_str]) + ')'

        for part in re.split(separators_re, line):
            if not part:
                continue
            if part in separators_str:
                yield part
                continue
            part = part.strip()
            if part:
                yield from part.split()
