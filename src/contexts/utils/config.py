from dotenv import load_dotenv
import os

def _get_root_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    split_folders = current_dir.split('/')[:-3]
    return '/'.join(split_folders)

load_dotenv()

root = _get_root_path()

#linux

#windows
