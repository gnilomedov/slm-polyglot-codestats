import argparse

from polyglot_pipeline import SlmPolyglotPipeline


def get_args() -> argparse.Namespace:
    '''Parse and return command-line arguments.'''
    parser = argparse.ArgumentParser(description='Polyglot Code Stats')
    parser.add_argument('--llm_api_url', type=str, default='http://local+interactive',
                        help='URL for the LLM API')
    parser.add_argument('--llm_api_key', type=str, default='API_KEY',
                        help='API key for the LLM')
    parser.add_argument('folder_masks', nargs='+',
                        help='Folder masks to process e.g., \'src-*\'')
    return parser.parse_args()


def main() -> None:
    args = get_args()
    pipeline = SlmPolyglotPipeline(args)
    pipeline.run()


if __name__ == '__main__':
    main()
