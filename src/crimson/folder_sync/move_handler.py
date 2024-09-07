import os
import shutil
from watchdog.events import FileSystemEventHandler
from typing import List, Union
from .filter import filter_path
from .debug import Debugger
import filecmp


class MoveHandler(FileSystemEventHandler):
    def __init__(
        self,
        source_dir: str,
        output_dir: str,
        include: Union[str, List[str]],
        exclude: Union[str, List[str]],
    ):
        self.source_dir: str = os.path.abspath(source_dir)
        self.output_dir: str = os.path.abspath(output_dir)
        self.include: Union[str, List[str]] = include
        self.exclude: Union[str, List[str]] = exclude

    def on_modified(self, event) -> None:
        if not event.is_directory:
            Debugger.push("Movehandler, on_modified", "called")
            self._move_file(event.src_path)

    def on_created(self, event) -> None:
        if not event.is_directory:
            Debugger.push("Movehandler, on_created", "called")
            self._move_file(event.src_path)

    def _move_file(self, src_path: str) -> None:
        filtered_path = filter_path(src_path, self.include, self.exclude)
        if filtered_path is None:
            return
        relative_path: str = os.path.relpath(
            self.source_dir, "/".join(src_path.split("/")[:-1])
        )

        destination_path: str = os.path.join(
            self.output_dir, relative_path, src_path.split("/")[-1]
        )

        if not os.path.exists(os.path.dirname(destination_path)):
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        if is_file_different(src_path, destination_path):
            try:
                shutil.copy2(src_path, destination_path)
                print(f"Moved '{src_path}' to '{destination_path}'.")
                Debugger.push("Movehandler, _move_file", open(src_path).read())
            except Exception as e:
                print(f"Error occurred while moving file: {e}")


def is_file_different(src_path: str, dst_path: str) -> bool:
    if not os.path.exists(dst_path):
        return True

    return not filecmp.cmp(src_path, dst_path, shallow=False)
