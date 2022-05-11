import os


def mkdir(path: str) -> None:
    """
    Create a folder if it does not exist.
    """
    if not os.path.exists(path):
        os.makedirs(path)

