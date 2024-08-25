import pytest
import textwrap

from demo_nano_llm.simple_tokenizer import SimpleTokenizer


@pytest.fixture
def tokenizer() -> SimpleTokenizer:
    '''Create an instance of SimpleTokenizer for testing.'''
    return SimpleTokenizer()


def test_tokenize_line() -> None:
    tokens = list(SimpleTokenizer._tokenize_line('foo = {123: \'456\', 987: "654"}'))
    assert tokens == ['foo', ' ', '=', ' ', '{', '123', ':', ' ', '\'', '456', '\'', ',', ' ',
                      '987', ':', ' ', '"', '654', '"', '}']
    tokens = list(SimpleTokenizer._tokenize_line('foo += [123, 456] + ["789"]'))
    assert tokens == ['foo', ' ', '+=', ' ', '[', '123', ',', ' ', '456', ']', ' ', '+', ' ',
                      '[', '"', '789', '"', ']']


def test_tokenize(tokenizer: SimpleTokenizer) -> None:
    text = textwrap.dedent('''\
            class Foo:
                def __init__(self, a: int = 123):
                    self._b = a + 1
                @property
                def c(self):
                    return {self._b, 456}''')
    tokens = list(tokenizer._tokenize(text))
    assert tokens == [
        'class', ' ', 'Foo', ':', '<NEWLINE>',
        '<INDENT>', 'def', ' ', '__init__', '(', 'self', ',', ' ',
        'a', ':', ' ', 'int', ' ', '=', ' ', '123', ')', ':', '<NEWLINE>',
        '<INDENT>', '<INDENT>', 'self', '.', '_b', ' ', '=', ' ',
        'a', ' ', '+', ' ', '1', '<NEWLINE>',
        '<INDENT>', '@property', '<NEWLINE>',
        '<INDENT>', 'def', ' ', 'c', '(', 'self', ')', ':', '<NEWLINE>',
        '<INDENT>', '<INDENT>', 'return', ' ', '{', 'self', '.', '_b', ',', ' ',
        '456', '}', '<NEWLINE>']


def test_fit(tokenizer: SimpleTokenizer) -> None:
    texts = ['def foo():', '    return \'bar\' + " 123"']
    tokenizer.fit(texts)

    assert tokenizer.vocab_size == 18
    assert tokenizer._vocab[:4] == ['<PAD>', '<UNK>', '<NEWLINE>',
                                   '<INDENT>']

    assert 'def' in tokenizer._vocab
    assert 'foo' in tokenizer._vocab
    assert tokenizer._token_to_id['def'] == 8
    assert tokenizer._id_to_token[8] == 'def'

    assert '(' in tokenizer._vocab
    assert ':' in tokenizer._vocab
    assert ' ' in tokenizer._vocab
    assert '\'' in tokenizer._vocab
    assert '\"' in tokenizer._vocab


def test_encode(tokenizer: SimpleTokenizer) -> None:
    texts = ['def foo():', '    return \'bar\'']
    tokenizer.fit(texts)

    encoded = tokenizer.encode("def foo()")
    assert encoded == [tokenizer._token_to_id['def'],
                       tokenizer._token_to_id[' '],
                       tokenizer._token_to_id['foo'],
                       tokenizer._token_to_id['('],
                       tokenizer._token_to_id[')'],
                       tokenizer._token_to_id['<NEWLINE>']]

    encoded_with_unknown = tokenizer.encode('unknown_token')
    assert encoded_with_unknown == [tokenizer._token_to_id['<UNK>'],
                                    tokenizer._token_to_id['<NEWLINE>']]


def test_decode(tokenizer: SimpleTokenizer) -> None:
    texts = ['def foo():', '    return "bar"']
    tokenizer.fit(texts)

    encoded = tokenizer.encode('def foo()')
    decoded = tokenizer.decode(encoded)
    assert decoded == 'def foo()'

    encoded_with_indentation = tokenizer.encode('    return "bar"')
    decoded_with_indentation = tokenizer.decode(encoded_with_indentation)
    assert decoded_with_indentation == '    return "bar"'

    encoded_with_unknown = tokenizer.encode('    return "unknown"')
    decoded_with_unknown = tokenizer.decode(encoded_with_unknown)
    assert decoded_with_unknown == '    return "<UNK>"'
