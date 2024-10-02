from typing import Tuple, Callable, Union, List
from crimson.folder_sync.sync_handlers.sync_handler import (
    SyncHandler,
    filter_path,
    is_file_different,
)
import shutil
import os


class EditableSyncHandler(SyncHandler):
    def __init__(
        self,
        source_dir: str,
        output_dir: str,
        include: Union[str, List[str]],
        exclude: Union[str, List[str]],
        sync_final: Callable[[str, str], Tuple[str, str]],
    ):
        super().__init__(source_dir, output_dir, include, exclude)
        self.sync_final = sync_final

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
                with open(src_path, "r", encoding="utf-8") as file:
                    content = file.read()

                # Apply the sync_final function to modify content and path
                modified_content, modified_path = self.sync_final(
                    content, destination_path
                )

                # If the path was modified, update the destination
                if modified_path != destination_path:
                    destination_path = modified_path
                    if not os.path.exists(os.path.dirname(destination_path)):
                        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

                # Write the modified content to the destination
                with open(destination_path, "w", encoding="utf-8") as file:
                    file.write(modified_content)

                # Copy metadata (permissions, times, etc.)
                shutil.copystat(src_path, destination_path)

                rel_src_path = os.path.relpath(src_path, self.cwd)
                rel_dst_path = os.path.relpath(destination_path, self.cwd)
                self.logger.info(
                    f"Synced './{rel_src_path}' to './{rel_dst_path}' with modifications."
                )
            except Exception as e:
                self.logger.error(f"Error occurred while syncing file: {e}")
