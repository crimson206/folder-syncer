import os
from watchdog.observers import Observer
from crimson.folder_sync.sync_handlers.sync_handler import SyncHandler
from typing import List, Union, TypeVar, Annotated
import time
import threading
from ..logger import get_logger


logger = get_logger("FolderSyncer")

TypeHolder = TypeVar("TypeHolder")


Include = Annotated[
    Union[str, List[str]],
    "pattern(s) of paths to sync.",
    {
        "description": "{summary}\n For the search logic, it use [fnmatch](https://docs.python.org/3/library/fnmatch.html)",
    },
]

Exclude = Annotated[
    Union[str, List[str]],
    "pattern(s) of paths to exclude from the sync.",
    {
        "description": "{summary}\n For the search logic, it use [fnmatch](https://docs.python.org/3/library/fnmatch.html)",
    },
]

SourceDir = Annotated[str, "The source directory to sync."]

OutputDir = Annotated[str, "The files from `SourceDir` are moved here."]


class FolderSyncer:
    """
    It watches the source_dir, and move the files if changes are detected.
    """

    def __init__(
        self,
        source_dir: SourceDir,
        output_dir: OutputDir,
        include: Include = [],
        exclude: Exclude = [],
    ):
        self.logger = logger
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.include = include
        self.exclude = exclude
        self.event_handler = SyncHandler(source_dir, output_dir, include, exclude)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, path=self.source_dir, recursive=True)
        self.is_running = False
        self.thread = None

    def start(self):
        """ """
        if not self.is_running:
            self.observer.start()
            self.is_running = True
            self.thread = threading.Thread(target=self._run)
            self.thread.start()
            logger.info(f"Watching '{self.source_dir}' for changes...")

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
            logger.info("Stopped watching for changes.")

    def _run(self):
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def refresh_sync(self, clean_target=False):
        """
        force sync
        """
        logger.info("Performing Refresh sync...")
        self.event_handler.refresh_sync(clean_target=clean_target)
        logger.info("Refresh sync completed.")


def use_folder_syncer(
    source_dir: str,
    output_dir: str,
    include: Union[str, List[str]] = [],
    exclude: Union[str, List[str]] = [],
    initial_sync_flag: bool = False,
) -> FolderSyncer:
    if not os.path.exists(source_dir):
        raise FileNotFoundError(f"Source path '{source_dir}' does not exist.")

    handler = FolderSyncer(source_dir, output_dir, include, exclude)

    if initial_sync_flag:
        handler.refresh_sync()

    return handler
