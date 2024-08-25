from ctypes import cast, c_char, c_char_p, POINTER


def decode_pointer_c_char_str(pointer_c_char_str: POINTER(c_char), encoding: str = 'utf-8') -> str:
    '''
    Convert a ctypes POINTER(c_char) to a Python string using the specified encoding.

    :arg pointer_c_char_str: Pointer to a null-terminated string.
    :arg encoding: The encoding to use for decoding the string (default is 'utf-8').

    :return: The decoded Python string.
    :rtype: str
    '''
    return cast(pointer_c_char_str, c_char_p).value.decode(encoding)
