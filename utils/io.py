import os
import sys


def asset_resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS  # type: ignore
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, "src", "assets", relative_path)

