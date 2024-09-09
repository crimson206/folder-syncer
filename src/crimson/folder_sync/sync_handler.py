import os
import shutil
from watchdog.events import FileSystemEventHandler
from typing import List, Union
from .filter import filter_path
from .debug import Debugger
from .logger import get_logger
import filecmp


class SyncHandler(FileSystemEventHandler):
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
        self.logger = get_logger("SyncHandler")
        self.cwd = os.getcwd()

    def on_modified(self, event) -> None:
        if not event.is_directory:
            Debugger.push("SyncHandler, on_modified", "called")
            self._sync_file(event.src_path)

    def on_created(self, event) -> None:
        if not event.is_directory:
            Debugger.push("SyncHandler, on_created", "called")
            self._sync_file(event.src_path)

    def on_deleted(self, event) -> None:
        if not event.is_directory:
            Debugger.push("SyncHandler, on_deleted", "called")
            self._delete_file(event.src_path)

    def _sync_file(self, src_path: str) -> None:
        filtered_path = filter_path(src_path, self.include, self.exclude)
        if filtered_path is None:
            return

        relative_path: str = os.path.relpath(src_path, self.source_dir)
        destination_path: str = os.path.join(self.output_dir, relative_path)

        if not os.path.exists(os.path.dirname(destination_path)):
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        if is_file_different(src_path, destination_path):
            try:
                shutil.copy2(src_path, destination_path)
                rel_src_path = os.path.relpath(src_path, self.cwd)
                rel_dst_path = os.path.relpath(destination_path, self.cwd)
                self.logger.info(f"Synced './{rel_src_path}' to './{rel_dst_path}'.")
                Debugger.push("SyncHandler, _sync_file", open(src_path).read())
            except Exception as e:
                self.logger.error(f"Error occurred while syncing file: {e}")

    def _delete_file(self, src_path: str) -> None:
        filtered_path = filter_path(src_path, self.include, self.exclude)
        if filtered_path is None:
            return

        relative_path: str = os.path.relpath(src_path, self.source_dir)
        destination_path: str = os.path.join(self.output_dir, relative_path)

        if os.path.exists(destination_path):
            try:
                os.remove(destination_path)
                rel_dst_path = os.path.relpath(destination_path, self.cwd)
                self.logger.info(f"Deleted './{rel_dst_path}'.")
                Debugger.push("SyncHandler, _delete_file", f"Deleted ./{rel_dst_path}")
            except Exception as e:
                self.logger.error(f"Error occurred while deleting file: {e}")


def is_file_different(src_path: str, dst_path: str) -> bool:
    if not os.path.exists(dst_path):
        return True

    return not filecmp.cmp(src_path, dst_path, shallow=False)
