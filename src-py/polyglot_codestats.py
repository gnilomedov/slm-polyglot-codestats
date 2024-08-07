import glob
from loguru import logger
import pandas as pd
import sys
from tabulate import tabulate

from interop.cpp import analyze_files
from interop.kotlin import scan_folders


def parse_folder_masks(masks):
    folders = []
    for mask in masks:
        folders.extend(glob.glob(mask))
    logger.info(
        f'Scan folder_masks {len(masks)} {repr(masks)} -> folders {len(folders)} {repr(folders)}')
    return folders


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <folder_mask1> [ <folder_mask2> ... ]")
        sys.exit(1)

    folder_masks = sys.argv[1:]
    folders = parse_folder_masks(folder_masks)

    logger.info('Scan folders in kotlin ...')
    file_contents = scan_folders(folders)
    logger.info(f'Scan folders in kotlin ... Done. {len(file_contents)}\n' +
                (' ; '.join([f'{f}_{len(c.split())}ln' for f, c in file_contents[:3]])))

    logger.info('Analyze files in C++ ...')
    file_stats = analyze_files(file_contents)
    logger.info(f'Analyze files in C++ ... Done. {len(file_stats)}\n' +
                ('\n'.join([str(s) for s in file_stats[:3]])))

    df = pd.DataFrame(file_stats)
    df['language'] = df['path'].apply(lambda x: x.split('.')[-1])

    logger.info(
        '\nOverall Stats:\n' +
        tabulate(pd.DataFrame([
            ('total_files', len(df)),
            ('total_lines', df['total_lines'].sum()),
            ('total_classes', df['total_classes'].sum()),
        ],
        columns=['Metric', 'Value']), tablefmt='presto', showindex=False))

    table = pd.pivot_table(df,
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


if __name__ == '__main__':
    main()
