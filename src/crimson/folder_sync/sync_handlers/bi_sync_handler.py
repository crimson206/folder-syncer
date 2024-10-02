import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from crimson.folder_sync.logger import get_logger
import filecmp
import time
from queue import Queue
from threading import Thread


class BiSyncHandler(FileSystemEventHandler):
    def __init__(self, dir1: str, dir2: str):
        self.dir1: str = os.path.abspath(dir1)
        self.dir2: str = os.path.abspath(dir2)
        self.logger = get_logger("BiSyncHandler")
        self.cwd = os.getcwd()
        self.queue1 = Queue()
        self.queue2 = Queue()
        self.ignore_paths = set()

    def start_sync(self):
        self._initial_sync()

        observer1 = Observer()
        observer2 = Observer()
        observer1.schedule(self, self.dir1, recursive=True)
        observer2.schedule(self, self.dir2, recursive=True)
        observer1.start()
        observer2.start()

        sync_thread1 = Thread(
            target=self._sync_worker, args=(self.queue1, self.dir1, self.dir2)
        )
        sync_thread2 = Thread(
            target=self._sync_worker, args=(self.queue2, self.dir2, self.dir1)
        )
        sync_thread1.start()
        sync_thread2.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer1.stop()
            observer2.stop()
            self.queue1.put(None)  # Signal to stop the thread
            self.queue2.put(None)
        observer1.join()
        observer2.join()
        sync_thread1.join()
        sync_thread2.join()

    def _initial_sync(self):
        self.logger.info("Performing initial sync...")
        self._sync_directories(self.dir1, self.dir2)
        self._sync_directories(self.dir2, self.dir1)
        self.logger.info("Initial sync completed.")

    def _sync_directories(self, src, dst):
        for root, _, files in os.walk(src):
            for file in files:
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, src)
                dst_path = os.path.join(dst, rel_path)

                if not os.path.exists(dst_path) or not filecmp.cmp(
                    src_path, dst_path, shallow=False
                ):
                    self._sync_file(src_path, dst_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._handle_file_event(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self._handle_file_event(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self._handle_file_event(event.src_path, delete=True)

    def _handle_file_event(self, src_path, delete=False):
        if src_path in self.ignore_paths:
            self.ignore_paths.remove(src_path)
            return

        if src_path.startswith(self.dir1):
            self.queue1.put((src_path, delete))
        else:
            self.queue2.put((src_path, delete))

    def _sync_worker(self, queue, src_dir, dst_dir):
        while True:
            item = queue.get()
            if item is None:
                break

            src_path, delete = item
            rel_path = os.path.relpath(src_path, src_dir)
            dst_path = os.path.join(dst_dir, rel_path)

            if delete:
                self._delete_file(dst_path)
            else:
                self._sync_file(src_path, dst_path)

            self.ignore_paths.add(dst_path)
            queue.task_done()

    def _sync_file(self, src_path, dst_path):
        try:
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy2(src_path, dst_path)
            rel_src_path = os.path.relpath(src_path, self.cwd)
            rel_dst_path = os.path.relpath(dst_path, self.cwd)
            self.logger.info(f"Synced './{rel_src_path}' to './{rel_dst_path}'.")
        except Exception as e:
            self.logger.error(f"Error occurred while syncing file: {e}")

    def _delete_file(self, path):
        try:
            if os.path.exists(path):
                os.remove(path)
                rel_path = os.path.relpath(path, self.cwd)
                self.logger.info(f"Deleted './{rel_path}'.")
        except Exception as e:
            self.logger.error(f"Error occurred while deleting file: {e}")


def is_file_different(src_path: str, dst_path: str) -> bool:
    if not os.path.exists(dst_path):
        return True
    return not filecmp.cmp(src_path, dst_path, shallow=False)
