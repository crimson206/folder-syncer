import os
import shutil
from watchdog.observers import Observer
from .move_handler import MoveHandler
from typing import List, Union, Generic, TypeVar
import time
import threading

TypeHolder = TypeVar("TypeHolder")


class SourceDir_(str, Generic[TypeHolder]):
    """
    Docstring
    """


class FolderSyncer:
    """
    이 함수는 특별한 작업을 수행합니다.

    see: :class:`crimson.folder_sync.move_handler.MoveHandler`
    """

    def __init__(
        self,
        source_dir: SourceDir_[str],
        output_dir: str,
        include: Union[str, List[str]] = [],
        exclude: Union[str, List[str]] = [],
    ):
        """
        Some Docstring

        see: class:`crimson.folder_sync.move_handler.MoveHandler`
        """
        self.source_dir = os.path.abspath(source_dir)
        self.output_dir = output_dir
        self.include = include
        self.exclude = exclude
        self.event_handler = MoveHandler(source_dir, output_dir, include, exclude)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, path=self.source_dir, recursive=True)
        self.is_running = False
        self.thread = None

    def start(self):
        """
        start function
        """
        if not self.is_running:
            self.observer.start()
            self.is_running = True
            self.thread = threading.Thread(target=self._run)
            self.thread.start()
            print(f"Watching '{self.source_dir}' for changes...")

    def stop(self):
        """
        stopp function
        """
        if self.is_running:
            self.is_running = False
            self.observer.stop()
            self.observer.join()
            if self.thread:
                self.thread.join()
            print("Stopped watching for changes.")

    def _run(self):
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def perform_initial_sync(self):
        """
        force sync
        """
        print("Performing initial sync...")
        initial_sync(self.source_dir, self.output_dir)
        print("Initial sync completed.")


def use_folder_syncer(
    source_dir: str,
    output_dir: str,
    include: Union[str, List[str]] = [],
    exclude: Union[str, List[str]] = [],
    initial_sync_flag: bool = False,
    dummy: MoveHandler = None,
) -> FolderSyncer:
    if not os.path.exists(source_dir):
        raise FileNotFoundError(f"Source path '{source_dir}' does not exist.")

    handler = FolderSyncer(source_dir, output_dir, include, exclude)

    if initial_sync_flag:
        handler.perform_initial_sync()

    return handler


def initial_sync(source_dir: str, output_dir: str) -> None:
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            src_path: str = os.path.join(root, file)
            relative_path: str = os.path.relpath(src_path, source_dir)
            dst_path: str = os.path.join(output_dir, relative_path)

            if not os.path.exists(os.path.dirname(dst_path)):
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)

            try:
                shutil.copy2(src_path, dst_path)
                print(f"Synced '{src_path}' to '{dst_path}'.")
            except Exception as e:
                print(f"Error occurred while syncing file: {e}")
