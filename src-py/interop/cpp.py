import ctypes
from ctypes import c_char_p, c_int, POINTER
from dataclasses import dataclass

from interop.analysis_extern_c_h import FileStats, PyFileStats


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
