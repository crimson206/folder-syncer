import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time


class MoveHandler(FileSystemEventHandler):
    def __init__(self, source_path, base_source, base_destination):
        self.source_path = os.path.abspath(source_path)
        self.base_source = os.path.abspath(base_source)
        self.base_destination = os.path.abspath(base_destination)

    def on_modified(self, event):
        if not event.is_directory:
            self._move_file(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self._move_file(event.src_path)

    def _move_file(self, src_path):
        relative_path = os.path.relpath(src_path, self.base_source)

        destination_path = os.path.join(self.base_destination, relative_path)

        if not os.path.exists(os.path.dirname(destination_path)):
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        try:
            shutil.copy2(src_path, destination_path)
            print(f"Moved '{src_path}' to '{destination_path}'.")
        except Exception as e:
            print(f"Error occurred while moving file: {e}")


def start_watching(source_path, base_source, base_destination, polling_interval=1):

    absolute_source_path = os.path.abspath(source_path)

    if not os.path.exists(absolute_source_path):
        raise FileNotFoundError(f"Source path '{absolute_source_path}' does not exist.")

    event_handler = MoveHandler(source_path, base_source, base_destination)

    observer = Observer()
    observer.schedule(event_handler, path=absolute_source_path, recursive=True)
    observer.start()

    try:
        print(f"Watching '{absolute_source_path}' for changes...")
        while True:
            time.sleep(polling_interval)  # 파일 시스템 이벤트를 계속 감시하도록 1초마다 sleep
    except KeyboardInterrupt:
        print("KeyboardInterrupt detected, stopping observer...")
    finally:
        observer.stop()
        observer.join()
