import os


class Scripts:
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))

    @property
    def linux_link_folders(self):
        """
        This script creates a symbolic link (symlink) between two paths.
        A symlink allows you to reference the target path from the symbolic path,
        effectively creating a shortcut or alias to the target directory or file.
        The script is typically used to simplify access to files or directories
        across different locations in the filesystem.
        """

        script_path = os.path.join(self.current_dir, "linux_link_folders.sh")

        with open(script_path, "r") as file:
            content = file.read()
        return content
