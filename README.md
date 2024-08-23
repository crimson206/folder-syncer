# Crimson Folder Sync

**Crimson Folder Sync** is a Python package designed to help you synchronize directories and automate certain system tasks with scripts.

## Installation

Install the package using pip:

```bash
pip install crimson-folder-sync
```

## Usage

### Directory Synchronization

To use the directory synchronization feature, import `MoveHandler` and `start_watching` from the package:

```python
from crimson.folder_sync.syncer import MoveHandler, start_watching

# Example usage
source_path = "/path/to/source"
base_source = "/path/to/base_source"
base_destination = "/path/to/base_destination"

start_watching(source_path, base_source, base_destination)
```

- **`MoveHandler`**: Handles file creation and modification events, copying the files from the source to the destination directory.
- **`start_watching`**: Watches the specified directory for changes and triggers the `MoveHandler` to copy files to the destination.

### Scripts

The package also includes utility scripts that can be accessed through the `Scripts` class.

```python
from crimson.folder_sync.load_script import Scripts

scripts = Scripts()

# Access the content of the linux_link_folders.sh script
print(scripts.linux_link_folders)
```

- **`linux_link_folders.sh`**: This script creates a symbolic link between two paths, allowing you to easily reference the target path from the symbolic path.

This package is designed to be a simple and effective tool for directory synchronization and basic system automation tasks.
