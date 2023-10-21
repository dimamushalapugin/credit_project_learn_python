import os
import shutil
from webapp.risk.views import get_folder_names


def test_get_folder_names():
    temp_dir = 'temp_test_dir'
    full_temp_dir = os.path.abspath(temp_dir)
    os.makedirs(os.path.join(full_temp_dir, 'folder1'))
    os.makedirs(os.path.join(full_temp_dir, 'folder2'))

    try:
        folder_names = get_folder_names(full_temp_dir)
        assert folder_names == ['folder1', 'folder2']
    finally:
        shutil.rmtree(full_temp_dir)
