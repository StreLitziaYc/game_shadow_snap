import os


def get_unique_filepath(directory, filename_base, extension):
    """生成不重复的文件名"""
    filename = f"{filename_base}{extension}"
    filepath = os.path.join(directory, filename)
    counter = 1
    while os.path.exists(filepath):
        filename = f"{filename_base}_{counter}{extension}"
        filepath = os.path.join(directory, filename)
        counter += 1
    return filepath, filename
