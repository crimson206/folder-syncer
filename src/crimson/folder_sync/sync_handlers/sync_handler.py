import os
import shutil
from watchdog.events import FileSystemEventHandler
from typing import List, Union
from crimson.folder_sync.filter import filter_path
from crimson.folder_sync.logger import get_logger
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
            self._sync_file(event.src_path)

    def on_created(self, event) -> None:
        if not event.is_directory:
            self._sync_file(event.src_path)

    def on_deleted(self, event) -> None:
        if not event.is_directory:
            self._delete_file(event.src_path)

    def _sync_file(self, src_path: str) -> None:
        filtered_path = filter_path(src_path, self.include, self.exclude)
        if filtered_path is None:
            return

        destination_path = self._prepare_destination_path(src_path)

        if not os.path.exists(os.path.dirname(destination_path)):
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        if is_file_different(src_path, destination_path):
            self._copy_file(src_path, destination_path)

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
            except Exception as e:
                self.logger.error(f"Error occurred while deleting file: {e}")

    def clean_target_directory(self) -> None:
        self.logger.info("Cleaning target directory...")
        for root, _, files in os.walk(self.output_dir):
            for file in files:
                dst_path: str = os.path.join(root, file)
                relative_path: str = os.path.relpath(dst_path, self.output_dir)
                src_path: str = os.path.join(self.source_dir, relative_path)

                if not os.path.exists(src_path):
                    filtered_path = filter_path(dst_path, self.include, self.exclude)
                    if filtered_path is not None:
                        try:
                            os.remove(dst_path)
                            rel_dst_path = os.path.relpath(dst_path, self.cwd)
                            self.logger.info(
                                f"Removed file not in source: './{rel_dst_path}'"
                            )
                        except Exception as e:
                            self.logger.error(
                                f"Error occurred while removing file: {e}"
                            )

        # 빈 디렉토리 제거
        for root, dirs, _ in os.walk(self.output_dir, topdown=False):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                if not os.listdir(dir_path):
                    try:
                        os.rmdir(dir_path)
                        rel_dir_path = os.path.relpath(dir_path, self.cwd)
                        self.logger.info(f"Removed empty directory: './{rel_dir_path}'")
                    except Exception as e:
                        self.logger.error(
                            f"Error occurred while removing empty directory: {e}"
                        )

        self.logger.info("Target directory cleaning completed.")

    def refresh_sync(self, clean_target: bool = False) -> None:
        self.logger.info("Performing Refresh sync...")
        for root, _, files in os.walk(self.source_dir):
            for file in files:
                src_path: str = os.path.join(root, file)
                self._sync_file(src_path)

        if clean_target:
            self.clean_target_directory()

        self.logger.info("Refresh sync completed.")

    def _prepare_destination_path(self, src_path: str, makedir=True) -> str:
        relative_path: str = os.path.relpath(src_path, self.source_dir)
        destination_path: str = os.path.join(self.output_dir, relative_path)

        if makedir:
            if not os.path.exists(os.path.dirname(destination_path)):
                os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        return destination_path

    def _copy_file(self, src_path: str, destination_path: str) -> None:
        try:
            shutil.copy2(src_path, destination_path)
            rel_src_path = os.path.relpath(src_path, self.cwd)
            rel_dst_path = os.path.relpath(destination_path, self.cwd)
            self.logger.info(f"Synced './{rel_src_path}' to './{rel_dst_path}'.")
        except Exception as e:
            self.logger.error(f"Error occurred while syncing file: {e}")


def is_file_different(src_path: str, dst_path: str) -> bool:
    if not os.path.exists(dst_path):
        return True

    return not filecmp.cmp(src_path, dst_path, shallow=False)
