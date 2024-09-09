import logging
from loguru import logger
import pandas as pd
import pytest
import sys
from typing import Generator
from unittest.mock import Mock, patch

from polyglot_pipeline import SlmPolyglotPipeline


@pytest.fixture(autouse=True)
def add_loguru_logger_to_caplog(caplog: pytest.LogCaptureFixture) -> Generator[None, None, None]:
    '''Redirect loguru logs to caplog for testing purposes.

    :param caplog: pytest's built-in fixture for capturing log messages.
    :yield: None. The fixture itself does not return any value, but allows the test to run
            between setting up the logger and resetting it afterward.
    '''
    class PropagateHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            logging.getLogger(record.name).handle(record)

    logger.remove()  # Remove existing loguru handlers
    logger.add(PropagateHandler(), level=logging.INFO)

    yield  # Allows the test function to execute

    # Reset loguru logger to its original state after test
    logger.remove()
    logger.add(sys.stderr, level=logging.INFO)


@pytest.fixture
def mock_args() -> Mock:
    '''Mock object simulating command-line arguments.'''
    return Mock(folder_masks=['src-py', 'src-cpp-*'],
                llm_api_url='http://test-url',
                llm_api_key='test-key')


@pytest.fixture
def mock_file_contents() -> list[tuple[str, str]]:
    '''Mock file contents for testing.'''
    return [('file1.py', 'content1'),
            ('file2.cpp', 'content2')]


@pytest.fixture
def mock_file_stats() -> list[dict[str, int | str]]:
    '''Mock file statistics for testing.'''
    return [
        {
            'path': 'file1.py',
            'total_lines': 10,
            'total_classes': 1,
            'empty_lines': 2,
            'trivial_lines': 1,
            'import_lines': 1,
            'comment_lines': 1,
            'multistring_lines': 0,
            'logging_lines': 1,
            'code_lines': 4
        },
        {
            'path': 'file2.cpp',
            'total_lines': 20,
            'total_classes': 2,
            'empty_lines': 3,
            'trivial_lines': 2,
            'import_lines': 2,
            'comment_lines': 2,
            'multistring_lines': 1,
            'logging_lines': 1,
            'code_lines': 9
        }
    ]


@pytest.fixture
def pipeline(mock_args: Mock) -> SlmPolyglotPipeline:
    '''Create an instance of SlmPolyglotPipeline for testing.

    :param mock_args: Mock object with simulated command-line arguments.
    '''
    return SlmPolyglotPipeline(mock_args)


@patch('polyglot_pipeline.glob.glob')
def test_parse_folder_masks(mock_glob: Mock, pipeline: SlmPolyglotPipeline,
                            caplog: pytest.LogCaptureFixture) -> None:
    mock_glob.side_effect = [['src-py'], ['src-cpp-1', 'src-cpp-2']]

    with caplog.at_level(logging.INFO):
        pipeline.parse_folder_masks()

    assert pipeline.folders == ['src-py', 'src-cpp-1', 'src-cpp-2']

    # Check if the log contains the essential information
    assert 'Scan folder_masks' in caplog.text
    assert "['src-py', 'src-cpp-*']" in caplog.text
    assert 'folders 3' in caplog.text
    assert "['src-py', 'src-cpp-1', 'src-cpp-2']" in caplog.text


@patch('polyglot_pipeline.scan_folders')
def test_scan_folders(mock_scan_folders: Mock, pipeline: SlmPolyglotPipeline,
                      mock_file_contents: list[tuple[str, str]],
                      caplog: pytest.LogCaptureFixture) -> None:
    mock_scan_folders.return_value = mock_file_contents

    with caplog.at_level(logging.INFO):
        pipeline.scan_folders()

    assert pipeline.file_contents == mock_file_contents
    assert 'Scan folders in kotlin ...' in caplog.text
    assert 'Scan folders in kotlin ... Done. 2' in caplog.text
    assert 'file1.py_1ln ; file2.cpp_1ln' in caplog.text


@patch('polyglot_pipeline.analyze_files')
def test_analyze_files(mock_analyze_files: Mock, pipeline: SlmPolyglotPipeline,
                       mock_file_stats: list[dict[str, int | str]],
                       caplog: pytest.LogCaptureFixture) -> None:
    mock_analyze_files.return_value = mock_file_stats

    with caplog.at_level(logging.INFO):
        pipeline.analyze_files()

    assert pipeline.file_stats == mock_file_stats
    assert 'Analyze files in C++ ...' in caplog.text
    assert 'Analyze files in C++ ... Done. 2' in caplog.text


def test_create_dataframe(pipeline: SlmPolyglotPipeline,
                          mock_file_stats: list[dict[str, int | str]]) -> None:
    pipeline.file_stats = mock_file_stats
    pipeline.create_dataframe()

    assert isinstance(pipeline.df, pd.DataFrame)
    assert len(pipeline.df) == 2
    assert 'language' in pipeline.df.columns
    assert pipeline.df['language'].tolist() == ['py', 'cpp']


def test_print_overall_stats(pipeline: SlmPolyglotPipeline,
                             mock_file_stats: list[dict[str, int | str]],
                             caplog: pytest.LogCaptureFixture) -> None:
    pipeline.file_stats = mock_file_stats
    pipeline.create_dataframe()

    with caplog.at_level(logging.INFO):
        pipeline.print_overall_stats()

    assert 'Overall Stats:' in caplog.text
    assert 'total_files' in caplog.text
    assert 'total_lines' in caplog.text
    assert 'total_classes' in caplog.text


def test_print_detailed_stats(pipeline: SlmPolyglotPipeline,
                              mock_file_stats: list[dict[str, int | str]],
                              caplog: pytest.LogCaptureFixture) -> None:
    pipeline.file_stats = mock_file_stats
    pipeline.create_dataframe()

    with caplog.at_level(logging.INFO):
        pipeline.print_detailed_stats()

    assert 'Detailed Stats:' in caplog.text
    assert 'empty_lines' in caplog.text
    assert 'trivial_lines' in caplog.text
    assert 'import_lines' in caplog.text
    assert 'comment_lines' in caplog.text
    assert 'multistring_lines' in caplog.text
    assert 'logging_lines' in caplog.text
    assert 'code_lines' in caplog.text
    assert 'total_classes' in caplog.text


@patch('polyglot_pipeline.execute_llm_query')
@patch('polyglot_pipeline.compose_code_improve_prompt')
def test_execute_llm_query(mock_compose_prompt: Mock, mock_execute_query: Mock,
                           pipeline: SlmPolyglotPipeline, mock_file_contents: list[tuple[str, str]],
                           caplog: pytest.LogCaptureFixture) -> None:
    pipeline.file_contents = mock_file_contents
    mock_compose_prompt.return_value = 'test prompt'
    mock_execute_query.return_value = 'LLM response'

    with caplog.at_level(logging.INFO):
        pipeline.execute_llm_query()

    mock_compose_prompt.assert_called_once_with(mock_file_contents)
    mock_execute_query.assert_called_once_with('http://test-url', 'test-key', 'test prompt')
    assert pipeline.llm_response == 'LLM response'
    assert 'LLM Response:' in caplog.text
    assert '=== === ===' in caplog.text
    assert 'LLM response' in caplog.text


@patch('polyglot_pipeline.SlmPolyglotPipeline.parse_folder_masks')
@patch('polyglot_pipeline.SlmPolyglotPipeline.scan_folders')
@patch('polyglot_pipeline.SlmPolyglotPipeline.analyze_files')
@patch('polyglot_pipeline.SlmPolyglotPipeline.create_dataframe')
@patch('polyglot_pipeline.SlmPolyglotPipeline.print_overall_stats')
@patch('polyglot_pipeline.SlmPolyglotPipeline.print_detailed_stats')
@patch('polyglot_pipeline.SlmPolyglotPipeline.execute_llm_query')
@patch('polyglot_pipeline.SlmPolyglotPipeline.train_demo_nano_slm')
def test_run(train_demo_nano_slm: Mock, mock_execute_llm: Mock, mock_print_detailed: Mock,
             mock_print_overall: Mock, mock_create_df: Mock, mock_analyze: Mock, mock_scan: Mock,
             mock_parse: Mock, pipeline: SlmPolyglotPipeline) -> None:
    pipeline.run()

    mock_parse.assert_called_once()
    mock_scan.assert_called_once()
    mock_analyze.assert_called_once()
    mock_create_df.assert_called_once()
    mock_print_overall.assert_called_once()
    mock_print_detailed.assert_called_once()
    mock_execute_llm.assert_called_once()
    train_demo_nano_slm.assert_called_once()
