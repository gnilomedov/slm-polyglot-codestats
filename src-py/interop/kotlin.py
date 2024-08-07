import jpype
import jpype.imports


def scan_folders(folders: list[str]) -> list[tuple[str, str]]:
    '''
    Scan the given folders for files with specific extensions using Java code via JPype.

    :folders: List of folder paths to scan.
    :return: List of tuples containing file paths and their contents.
    '''
    if not jpype.isJVMStarted():
        jpype.startJVM(classpath=['build-out/polyglot.jar'])
    from demo.polyglot import FolderScannerKt

    extensions = ['.cpp', '.h', '.kt', '.py', '.sh']
    file_contents_java = FolderScannerKt.scanFolders(_list_py2java(folders),
                                                     _list_py2java(extensions))

    return [(str(f.getPath()), str(f.getContent())) for f in file_contents_java]


def _list_py2java(pylist: list[str]) -> 'jpype.java.util.ArrayList':
    '''
    Convert a Python list to a Java ArrayList.

    :py_list: Python list to convert.
    :return: Converted Java ArrayList.
    '''
    java_list = jpype.java.util.ArrayList()
    for e in pylist:
        java_list.add(e)
    return java_list