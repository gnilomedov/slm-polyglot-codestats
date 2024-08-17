import ctypes
from ctypes import cast, c_char, c_char_p, c_int, POINTER
from dataclasses import dataclass

from interop.analysis_extern_c_h import FileStats, PyFileStats
from interop.cpp_utils import decode_pointer_c_char_str


lib = ctypes.CDLL('./build-out/polyglot.so')

lib.analyzeFiles.argtypes = [POINTER(c_char_p), POINTER(c_char_p), c_int]
lib.analyzeFiles.restype = POINTER(FileStats)

lib.freeFileStats.argtypes = [POINTER(FileStats)]
lib.freeFileStats.restype = None


class _AnalyseFilesGuard:
    def __init__(self, analyse_files_result, count):
        self._analyse_files_result = analyse_files_result
        self._count = count

    def __getitem__(self, i: int) -> FileStats:
        return self._analyse_files_result[i]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        lib.freeFileStats(self._analyse_files_result, self._count)


def analyze_files(file_contents: list[tuple[str, str]]) -> list[PyFileStats]:
    '''
    Analyze file contents using a C library function.

    :file_contents: List of tuples containing file path and content.
    :return: List of PyFileStats objects containing analysis results.
    '''
    paths = (c_char_p * len(file_contents))(*[path.encode('utf-8') for path, _ in file_contents])
    contents = (c_char_p * len(file_contents))(*[content.encode('utf-8') for _, content in file_contents])

    paths_ptr = ctypes.cast(paths, POINTER(c_char_p))
    contents_ptr = ctypes.cast(contents, POINTER(c_char_p))

    with _AnalyseFilesGuard(lib.analyzeFiles(paths_ptr, contents_ptr, len(file_contents)),
                            len(file_contents)) as result:
        return [PyFileStats.from_c_struct(result[i]) for i in range(len(file_contents))]


lib.composeCodeImprovePrompt.argtypes = [POINTER(c_char_p), POINTER(c_char_p), c_int]
lib.composeCodeImprovePrompt.restype = POINTER(c_char)

lib.freeComposedPrompt.argtypes = [c_char_p]
lib.freeComposedPrompt.restype = None


class _CCharPGuard:
    def __init__(self, c_char_p_val: c_char_p):
        self._c_char_p_val = c_char_p_val

    def get(self) -> str:
        return decode_pointer_c_char_str(self._c_char_p_val)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        lib.freeComposedPrompt(cast(self._c_char_p_val, POINTER(c_char)))


def compose_code_improve_prompt(file_contents: list[tuple[str, str]]) -> str:
    '''
    Wrapper function for composeCodeImprovePrompt.

    Args:
    paths (List[str]): List of file paths.
    contents (List[str]): List of file contents corresponding to the paths.

    Returns:
    str: The composed prompt for code improvement.

    Raises:
    ValueError: If the lengths of paths and contents don't match.
    '''
    paths = (c_char_p * len(file_contents))(*[path.encode('utf-8') for path, _ in file_contents])
    contents = (c_char_p * len(file_contents))(*[content.encode('utf-8') for _, content in file_contents])

    paths_ptr = ctypes.cast(paths, POINTER(c_char_p))
    contents_ptr = ctypes.cast(contents, POINTER(c_char_p))

    with _CCharPGuard(lib.composeCodeImprovePrompt(paths_ptr, contents_ptr, len(file_contents))) as result:
        return result.get()
