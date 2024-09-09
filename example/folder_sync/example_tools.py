import os
import shutil
from pathlib import Path
from typing import NamedTuple
import sys
from crimson.folder_sync.logger import get_logger


logger = get_logger(name="example")

source_contents = {
    "./file1.py": 'print("Hello world")\n',
    "./file2.py": 'print("What a wonderful day!")\n',
    "./lvl2/file3.py": 'print("File from lvl2.")\n',
}


def synchronized_print(message):
    print(message)
    sys.stdout.flush()


SOURCE_DIR = Path(__file__).parent / "syncer/folder_example/source"
OUTPUT_DIR = Path(__file__).parent / "syncer/folder_example/output"

_current_dir = Path(__file__).parent


class ExampleDirs(NamedTuple):
    source_dir: str
    output_dir: str


def get_dir(path: str):
    return Path(path).parent


def delete_dir(dir: str):
    abs_dir = os.path.abspath(dir)
    if os.path.exists(abs_dir):
        shutil.rmtree(abs_dir)
        logger.info(f"Directory, '{dir}',  deleted")
    else:
        logger.info(f"Path, {dir}, doesn't exist.")


def get_example_dirs() -> ExampleDirs:
    return (SOURCE_DIR, dir)


def generate_source_dir():
    for relative_path, content in source_contents.items():
        path = f'{SOURCE_DIR}/{relative_path.replace("./", "")}'
        if not os.path.exists(get_dir(path)):
            os.makedirs(get_dir(path))

        open(path, "w").write(content)


def get_dir_structure(directory):
    dir_structure = {}
    for root, _, files in os.walk(directory):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), directory)

            dir_structure[rel_path] = open(directory + "/" + rel_path).read()
    return dir_structure
