import pytest

import torch

from demo_nano_slm.multi_file_content_code_dataset import MultiFileContentCodeDataset


# Constants for test file contents
FILE_CONTENT_1 = 'abcdefghijklmnopqrstuvwxyz'
FILE_CONTENT_2 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
FILE_CONTENTS = [('file1.py', FILE_CONTENT_1), ('file2.py', FILE_CONTENT_2)]

# Calculate expected lengths
SEQ_LENGTH = 10
EXPECTED_TRAIN_INPUT_LENGTH_1 = max(0, len(FILE_CONTENT_1) - SEQ_LENGTH)
EXPECTED_TRAIN_INPUT_LENGTH_2 = max(0, len(FILE_CONTENT_2) - SEQ_LENGTH)
TOTAL_EXPECTED_LENGTH = EXPECTED_TRAIN_INPUT_LENGTH_1 + EXPECTED_TRAIN_INPUT_LENGTH_2


class MockTokenizer:
    '''Mock tokenizer for testing.'''
    def __call__(self, text: str, return_tensors: str | None = None):
        return {'input_ids': torch.tensor([ord(char) for char in text])}


@pytest.fixture
def dataset() -> MultiFileContentCodeDataset:
    '''Create an instance of MultiFileContentCodeDataset for testing.'''
    tokenizer = MockTokenizer()
    return MultiFileContentCodeDataset(FILE_CONTENTS, tokenizer,
                                       seq_length=SEQ_LENGTH)


def test_len(dataset: MultiFileContentCodeDataset) -> None:
    assert len(dataset) == min(128, TOTAL_EXPECTED_LENGTH)
    assert list(dataset._cumulative_lengths) == [
        0,
        len(FILE_CONTENT_1) - SEQ_LENGTH,
        len(FILE_CONTENT_1) - SEQ_LENGTH + len(FILE_CONTENT_2) - SEQ_LENGTH]


def test_getitem_middle_file_1(dataset: MultiFileContentCodeDataset) -> None:
    p = EXPECTED_TRAIN_INPUT_LENGTH_1 // 2
    item = dataset[p]
    assert isinstance(item, dict)
    assert set(item.keys()) == {'input_ids', 'labels'}
    assert len(item['input_ids']) == len(item['labels']) == SEQ_LENGTH
    assert chr(item['input_ids'][-1]) == FILE_CONTENT_1[p + SEQ_LENGTH - 1]
    assert chr(item['labels'][-1]) == FILE_CONTENT_1[p + SEQ_LENGTH]


def test_getitem_beg_file_1(dataset: MultiFileContentCodeDataset) -> None:
    item = dataset[0]
    assert len(item['input_ids']) == len(item['labels']) == SEQ_LENGTH
    assert chr(item['input_ids'][-1]) == FILE_CONTENT_1[SEQ_LENGTH - 1]
    assert chr(item['labels'][-1]) == FILE_CONTENT_1[SEQ_LENGTH]


def test_getitem_end_file_1(dataset: MultiFileContentCodeDataset) -> None:
    idx = EXPECTED_TRAIN_INPUT_LENGTH_1 - 1
    item = dataset[idx]
    assert len(item['input_ids']) == len(item['labels']) == SEQ_LENGTH
    assert chr(item['input_ids'][-1]) == FILE_CONTENT_1[-2]
    assert chr(item['labels'][-1]) == FILE_CONTENT_1[-1]


def test_getitem_beg_file_2(dataset: MultiFileContentCodeDataset) -> None:
    idx = EXPECTED_TRAIN_INPUT_LENGTH_1
    item = dataset[idx]
    assert len(item['input_ids']) == len(item['labels']) == SEQ_LENGTH
    assert chr(item['input_ids'][-1]) == FILE_CONTENT_2[SEQ_LENGTH - 1]
    assert chr(item['labels'][-1]) == FILE_CONTENT_2[SEQ_LENGTH]


def test_getitem_end_file_2(dataset: MultiFileContentCodeDataset) -> None:
    idx = TOTAL_EXPECTED_LENGTH - 1
    item = dataset[idx]
    assert len(item['input_ids']) == len(item['labels']) == SEQ_LENGTH
    assert chr(item['input_ids'][-1]) == FILE_CONTENT_2[-2]
    assert chr(item['labels'][-1]) == FILE_CONTENT_2[-1]


def test_shuffle_and_cap(dataset: MultiFileContentCodeDataset) -> None:
    original_len = len(dataset)
    dataset.shuffle_and_cap(length=5)
    assert len(dataset) == 5
    assert dataset._reshuffled_indices is not None
    assert all(0 <= idx < original_len for idx in dataset._reshuffled_indices)
