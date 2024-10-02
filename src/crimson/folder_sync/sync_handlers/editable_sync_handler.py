from typing import Tuple, Callable, Union, List
from crimson.filter_beta.filter.filter_source import fnmatch_filter_source
from crimson.filter_beta.filter import fnmatch_filter
from crimson.folder_sync.sync_handlers.sync_handler import (
    SyncHandler,
    filter_path,
)
import os


class SyncFinal(Callable[[str, str], Tuple[str, str]]):
    """
    A function to modify content and path.

    Take a look of the  example function, `SyncFinal.sync_final`
    """

    def sync_final(content: str, path: str) -> Tuple[str, str]:
        content = "# modified content\n" + content
        path_split = path.split(".")
        path_split[-2] = path_split[-2] + "_modified"
        return content, ".".join(path_split)


class EditableSyncHandler(SyncHandler):
    def __init__(
        self,
        source_dir: str,
        output_dir: str,
        include: Union[str, List[str]],
        exclude: Union[str, List[str]],
        sync_final: SyncFinal,
    ):
        super().__init__(source_dir, output_dir, include, exclude)
        self.sync_final = sync_final

    def _sync_file(self, src_path: str) -> None:
        filtered_path = filter_path(src_path, self.include, self.exclude)
        if filtered_path is None:
            return

        destination_path = self._prepare_destination_path(src_path, makedir=False)

        with open(src_path, "r", encoding="utf-8") as file:
            content = file.read()

        modified_content, modified_path = self.sync_final(content, destination_path)

        if not os.path.exists(os.path.dirname(modified_path)):
            os.makedirs(os.path.dirname(modified_path), exist_ok=True)

        previous_content = (
            open(modified_path, "r").read() if os.path.exists(modified_path) else ""
        )

        if modified_content != previous_content:
            self._copy_file(src_path, modified_path, modified_content)

    def _copy_file(self, src_path: str, destination_path: str, content: str) -> None:
        try:
            open(destination_path, "w").write(content)
            rel_src_path = os.path.relpath(src_path, self.cwd)
            rel_dst_path = os.path.relpath(destination_path, self.cwd)
            self.logger.info(f"Synced './{rel_src_path}' to './{rel_dst_path}'.")
        except Exception as e:
            self.logger.error(f"Error occurred while syncing file: {e}")

    def refresh_sync(self, clean_target: bool = False) -> None:
        self.logger.info("Performing Refresh sync...")
        for root, _, files in os.walk(self.source_dir):
            for file in files:
                src_path: str = os.path.join(root, file)
                self._sync_file(src_path)
        if clean_target:
            clean_output_dir(self.source_dir, self.output_dir, self.sync_final, self.include, self.exclude)
        self.logger.info("Refresh sync completed.")


def get_source_paths(source_dir: str, include: List[str], exclude: List[str]):
    source_paths = []
    for root, _, files in os.walk(source_dir):
        for file in files:
            src_path: str = os.path.join(root, file)
            source_paths.append(src_path)

    return fnmatch_filter(source_paths, include, exclude)


def clean_output_dir(source_dir, output_dir, sync_final, include, exclude):
    filtered_source_paths = fnmatch_filter_source(source_dir, include, exclude)
    output_paths = fnmatch_filter_source(output_dir)

    modified_paths = []

    for source_path in filtered_source_paths:
        content = "dummy_content"
        _, modified_path = sync_final(content, source_path)

        modified_paths.append(modified_path)

    for output_path in output_paths:
        if output_path not in modified_paths:
            os.remove(os.path.join(output_dir, output_path))
