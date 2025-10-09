import os


def remove_dir(dir_path: str) -> None:
    if os.path.isdir(dir_path):
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            if os.path.isdir(item_path):
                remove_dir(item_path)
            else:
                os.remove(item_path)
        os.rmdir(dir_path)
