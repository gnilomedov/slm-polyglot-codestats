import argparse
import glob
from loguru import logger
import pandas as pd
from tabulate import tabulate
import textwrap

from demo_nano_llm.nano_code_composer import NanoCondeComposer
from demo_nano_llm.pico_code_composer import PicoCondeComposer
from interop.analysis_extern_c_h import PyFileStats
from interop.cpp import analyze_files, compose_code_improve_prompt
from interop.kotlin import execute_llm_query, scan_folders


class LlmPolyglotPipeline:
    '''Scans and analyzes code files in multiple languages, generating improvements using an LLM.'''

    def __init__(self, args: argparse.Namespace):
        '''Initialize the pipeline with given arguments.

        :param args: An object containing command-line arguments like folder masks, LLM API URL, and
                     API key.
        '''
        self.folder_masks: list[str] = args.folder_masks
        self.llm_api_url: str = args.llm_api_url
        self.llm_api_key: str = args.llm_api_key
        self.folders: list[str] = []
        self.file_contents: list[tuple[str, str]] = []
        self.file_stats: list[PyFileStats] = []
        self.df: pd.DataFrame | None = None
        self.llm_response: str = ''

    def parse_folder_masks(self) -> None:
        '''Parse the folder masks to identify the folders to be processed.'''
        self.folders = []
        for mask in self.folder_masks:
            self.folders.extend(glob.glob(mask))
        logger.info(
            f'Scan folder_masks {len(self.folder_masks)} {repr(self.folder_masks)} '
            f'-> folders {len(self.folders)} {repr(self.folders)}')

    def scan_folders(self) -> None:
        '''Scan the identified folders and retrieve the contents of the files.'''
        logger.info('Scan folders in kotlin ...')
        self.file_contents = scan_folders(self.folders)
        logger.info(
            f'Scan folders in kotlin ... Done. {len(self.file_contents)}\n' +
            (' ; '.join([f'{f}_{len(c.split())}ln' for f, c in self.file_contents[:3]])))

    def analyze_files(self) -> None:
        '''Analyze the scanned files and collect statistics.'''
        logger.info('Analyze files in C++ ...')
        self.file_stats = analyze_files(self.file_contents)
        logger.info(
            f'Analyze files in C++ ... Done. {len(self.file_stats)}\n' +
            ('\n'.join([str(s) for s in self.file_stats[:3]])))

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
            columns=['Metric', 'Value']), tablefmt='presto', showindex=False))

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
            aggfunc='sum')
        logger.info(
            '\nDetailed Stats:\n' +
            tabulate(table, headers='keys', tablefmt='presto'))

    def execute_llm_query(self) -> None:
        '''Execute a query to an LLM for code improvement suggestions.'''
        self.llm_response = execute_llm_query(
            self.llm_api_url,
            self.llm_api_key,
            compose_code_improve_prompt(self.file_contents))
        logger.info(f'LLM Response:\n\n=== === ===\n{self.llm_response}\n=== === ===\n\n')

    def train_demo_nano_llm(self):
        '''Train demo LLMs using the file contents.'''
        for composer in [
                    NanoCondeComposer(),
                    PicoCondeComposer(),
                ]:
            composer.fit_model(self.file_contents)
            logger.info(f'Compose code with\n{composer.get_model_summary()}')
            start_code_snippets = [
                    textwrap.dedent('''\
                          class FibonacciCalculator:
                              def __init__(self, name):
                                  self._name = name
                              def calculate(n: int):
                                  raise NotImplementedError()'''),
                    textwrap.dedent('''\
                          class FibonacciCalculator {
                          public:
                              FibonacciCalculator(const char* name): name(name) { }
                              int calculate(int n) {'''),
                    textwrap.dedent('''\
                          open class FibonacciCalculator(private val name: String) {
                              open fun calculate(n: Int): Int {
                                  throw NotImplementedError("not implemented")'''),
                    textwrap.dedent('''\
                          def main():
                              fc = FibonacciCalculator()
                              fc.calculate('''),
                    textwrap.dedent('''\
                          int main(const char*) {
                              FibonacciCalculator cf();
                              fc.calculate'''),
                    textwrap.dedent('''\
                          fun main() {
                              val calculator = FibonacciCalculator()
                              calculator.calculate('''),
                    textwrap.dedent('''\
                          class TestFibonacciCalculator(unittest.TestCase):
                              def setUp(self):
                                  self.calculator = FibonacciCalculator()
                                  def test_fibonacci(self):
                                      self.assertEqual(self.calculator'''),
                    textwrap.dedent('''\
                          TEST_F(FibonacciCalculatorTest, Calculate) {
                              Fibonacci calculator;
                              EXPECT_EQ(calculator.calculate
                          '''),
                    textwrap.dedent('''\
                          class FibonacciCalculatorTest {
                              private class TestFibonacciCalculator(name: String):
                                  FibonacciCalculator(name)
                              @Test
                              fun testCalculate() {
                                  val calculator = TestFibonacciCalculator("TestCalculator")'''),
                ]
            for start_text in start_code_snippets:
                generated_text = composer.compose_code(start_text, max_length=256)
                code_separator = '=== === ==='
                logger.info(
                    f'\nSample text: {code_separator}\n{start_text}\n{code_separator}\n\n'
                    f'generated: {code_separator}\n{generated_text}\n{code_separator}')

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
        self.train_demo_nano_llm()
