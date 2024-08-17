from ctypes import cast, c_char, c_char_p, c_int, Structure
from dataclasses import dataclass

from interop.cpp_utils import decode_pointer_c_char_str


# This module should be kept in sync with src-cpp/analysis_extern_c.h

class FileStats(Structure):
    '''
    C-compatible structure for file statistics.
    
    This class corresponds to the C struct defined in analysis_extern_c.h.
    '''
    _fields_ = [
        ('path_cstr', c_char_p), # Pointer to char for dynamic string
        ('empty_lines', c_int),
        ('trivial_lines', c_int),
        ('import_lines', c_int),
        ('comment_lines', c_int),
        ('multistring_lines', c_int),
        ('logging_lines', c_int),
        ('code_lines', c_int),
        ('total_lines', c_int),
        ('total_classes', c_int),
    ]

@dataclass
class PyFileStats:
    '''
    Python dataclass for file statistics.
    
    This class provides a more Pythonic interface to the file statistics data.
    '''
    path: str
    empty_lines: int
    trivial_lines: int
    import_lines: int
    comment_lines: int
    multistring_lines: int
    logging_lines: int
    code_lines: int
    total_lines: int
    total_classes: int

    @classmethod
    def from_c_struct(cls, c_file_stats: FileStats) -> 'PyFileStats':
        return cls(
            path=decode_pointer_c_char_str(c_file_stats.path_cstr),
            empty_lines=c_file_stats.empty_lines,
            trivial_lines=c_file_stats.trivial_lines,
            import_lines=c_file_stats.import_lines,
            comment_lines=c_file_stats.comment_lines,
            multistring_lines=c_file_stats.multistring_lines,
            logging_lines=c_file_stats.logging_lines,
            code_lines=c_file_stats.code_lines,
            total_lines=c_file_stats.total_lines,
            total_classes=c_file_stats.total_classes
        )
