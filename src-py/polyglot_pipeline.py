import argparse
import glob
from loguru import logger
import pandas as pd
from tabulate import tabulate
from typing import Optional, Tuple, List

from interop.analysis_extern_c_h import PyFileStats
from interop.cpp import analyze_files, compose_code_improve_prompt
from interop.kotlin import execute_llm_query, scan_folders


class LlmPolyglotPipeline:
    '''
    A pipeline class to scan, analyze, and process code files across multiple languages
    and generate improvements using a Language Model (LLM).
    '''

    def __init__(self, args: argparse.Namespace):
        '''
        Initialize the pipeline with given arguments.

        Args:
            args: An object containing command-line arguments like folder masks, LLM API URL, and
                  API key.
        '''
        self.folder_masks: List[str] = args.folder_masks
        self.llm_api_url: str = args.llm_api_url
        self.llm_api_key: str = args.llm_api_key
        self.folders: List[str] = []
        self.file_contents: List[Tuple[str, str]] = []
        self.file_stats: List[PyFileStats] = []
        self.df: Optional[pd.DataFrame] = None
        self.llm_response: str = ''

    def parse_folder_masks(self) -> None:
        '''Parse the folder masks to identify the folders to be processed.'''
        self.folders = []
        for mask in self.folder_masks:
            self.folders.extend(glob.glob(mask))
        logger.info(
            f'Scan folder_masks {len(self.folder_masks)} {repr(self.folder_masks)} '
            f'-> folders {len(self.folders)} {repr(self.folders)}'
        )

    def scan_folders(self) -> None:
        '''Scan the identified folders and retrieve the contents of the files.'''
        logger.info('Scan folders in kotlin ...')
        self.file_contents = scan_folders(self.folders)
        logger.info(
            f'Scan folders in kotlin ... Done. {len(self.file_contents)}\n' +
            (' ; '.join([f'{f}_{len(c.split())}ln' for f, c in self.file_contents[:3]]))
        )

    def analyze_files(self) -> None:
        '''Analyze the scanned files and collect statistics.'''
        logger.info('Analyze files in C++ ...')
        self.file_stats = analyze_files(self.file_contents)
        logger.info(
            f'Analyze files in C++ ... Done. {len(self.file_stats)}\n' +
            ('\n'.join([str(s) for s in self.file_stats[:3]]))
        )

    def create_dataframe(self) -> None:
        '''Convert the collected file statistics into a pandas DataFrame.'''
        self.df = pd.DataFrame(self.file_stats)
        self.df['language'] = self.df['path'].apply(lambda x: x.split('.')[-1])

    def print_overall_stats(self) -> None:
        '''Print overall statistics of the analyzed files.'''
        logger.info(
            '\nOverall Stats:\n' +
            tabulate(pd.DataFrame([
                ('total_files', len(self.df)),
                ('total_lines', self.df['total_lines'].sum()),
                ('total_classes', self.df['total_classes'].sum()),
            ],
            columns=['Metric', 'Value']), tablefmt='presto', showindex=False)
        )

    def print_detailed_stats(self) -> None:
        '''Print detailed statistics broken down by language.'''
        table = pd.pivot_table(
            self.df,
            values=[
                'empty_lines',
                'trivial_lines',
                'import_lines',
                'comment_lines',
                'multistring_lines',
                'logging_lines',
                'code_lines',
                'total_classes',
            ],
            index='language',
            aggfunc='sum'
        )
        logger.info(
            '\nDetailed Stats:\n' +
            tabulate(table, headers='keys', tablefmt='presto')
        )

    def execute_llm_query(self) -> None:
        '''Execute a query to an LLM for code improvement suggestions.'''
        self.llm_response = execute_llm_query(
            self.llm_api_url,
            self.llm_api_key,
            compose_code_improve_prompt(self.file_contents)
        )
        logger.info(f'LLM Response:\n\n=== === ===\n{self.llm_response}\n=== === ===\n\n')

    def run(self) -> None:
        '''
        Execute the entire pipeline: parse folders, scan files, analyze contents,
        generate statistics, and query the LLM for improvements.
        '''
        self.parse_folder_masks()
        self.scan_folders()
        self.analyze_files()
        self.create_dataframe()
        self.print_overall_stats()
        self.print_detailed_stats()
        self.execute_llm_query()
