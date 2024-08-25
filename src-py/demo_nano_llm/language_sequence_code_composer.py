class LanguageSequenceCondeComposer:
    '''Base class for sequence-to-sequence code generation models.'''

    def __init__(self):
        pass

    def get_model_summary(self) -> str:
        '''Get a summary of the model's architecture and parameters.'''
        raise NotImplementedError()

    def fit_model(self, file_contents: list[tuple[str, str]],
                  num_epochs: int, batch_size: int, learning_rate: float) -> None:
        '''Train the code generation model on the provided file contents.

        :param file_contents: List of (file_path, file_content_text).
        :param num_epochs: Number of training epochs.
        :param batch_size: Number of samples per training batch.
        :param learning_rate: Step size for weight updates during training.

        :raises NotImplementedError: This method must be implemented by subclasses.
        '''
        raise NotImplementedError()

    def compose_code(self, code_text_begin: str, max_length: int) -> str:
        '''Generate new code based on the provided starting text.

        :param code_text_begin: The starting text for code generation.
        :param max_length: Maximum length of the generated code.
        :return: The generated code.
        '''
        raise NotImplementedError()
