import jpype
import jpype.imports
from loguru import logger

if not jpype.isJVMStarted():
    import os, re
    build_out_libs = 'build-out/libs'
    jar_files = {
        os.path.join(build_out_libs, re.sub(r'-\d+(\.\d+)*([.-]\w+)?\.jar$', '.jar', jar))
        for jar in os.listdir(build_out_libs) if jar.endswith('.jar')
    }
    classpath = sorted(list(jar_files) + ['build-out/polyglot.jar'])
    logger.info('Starting JVM with classpath:\n' + '\n'.join(classpath))
    jpype.startJVM(classpath=classpath)
from demo.polyglot import FolderScannerKt
from demo.polyglot import LlmQueryExecutorKt


def execute_llm_query(api_url: str, api_key: str, prompt_txt: str) -> list[tuple[str, str]]:
    query_result = LlmQueryExecutorKt.executeQuery(api_url, api_key, prompt_txt)
    return query_result.getResponse()


def scan_folders(folders: list[str]) -> list[tuple[str, str]]:
    '''Scan the given folders for files with specific extensions using Java code via JPype.

    :param folders: List of folder paths to scan.
    :return: List of tuples containing file paths and their contents.
    '''

    extensions = ['.cpp', '.h', '.kt', '.kts', '.py', '.sh']
    file_contents_java = FolderScannerKt.scanFolders(_list_py2java(folders),
                                                     _list_py2java(extensions))

    return [(str(f.getPath()), str(f.getContent())) for f in file_contents_java]


def _list_py2java(pylist: list[str]) -> 'jpype.java.util.ArrayList':
    '''Convert a Python list to a Java ArrayList.

    :param pylist: Python list to convert.
    :return: Converted Java ArrayList.
    '''
    java_list = jpype.java.util.ArrayList()
    for e in pylist:
        java_list.add(e)
    return java_list
