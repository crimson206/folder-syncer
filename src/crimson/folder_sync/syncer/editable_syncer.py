from watchdog.observers import Observer
from typing import Callable, Tuple
from crimson.folder_sync.sync_handlers.editable import EditableSyncHandler
from crimson.folder_sync.logger import get_logger
from crimson.folder_sync.syncer.base_syncer import (
    FolderSyncer,
    SourceDir,
    OutputDir,
    Exclude,
    Include,
)

logger = get_logger("EditableFolderSyncer")


class EditableFolderSyncer(FolderSyncer):
    """
    An extension of FolderSyncer that allows for content and path modification during sync.
    """

    def __init__(
        self,
        source_dir: SourceDir,
        output_dir: OutputDir,
        include: Include = [],
        exclude: Exclude = [],
        sync_final: Callable[[str, str], Tuple[str, str]] = None,
    ):
        super().__init__(source_dir, output_dir, include, exclude)
        self.sync_final = sync_final
        # Replace the event handler with EditableSyncHandler
        self.event_handler = EditableSyncHandler(
            source_dir, output_dir, include, exclude, sync_final
        )
        # Reschedule the observer with the new event handler
        self.observer = Observer()
        self.observer.schedule(self.event_handler, path=self.source_dir, recursive=True)
