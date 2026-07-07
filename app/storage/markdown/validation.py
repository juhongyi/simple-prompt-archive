from ..errors import StorageError


def validate_markdown_paths(data_dir, export_plan):
    validate_data_directory(data_dir)

    for item in export_plan:
        if item.directory.exists() and not item.directory.is_dir():
            raise StorageError("필요한 폴더 위치에 파일이 있습니다.")
        if item.path.exists() and not item.path.is_file():
            raise StorageError("필요한 파일 위치에 폴더가 있습니다.")


def validate_data_directory(data_dir):
    if data_dir.exists() and not data_dir.is_dir():
        raise StorageError("data 위치에 파일이 있어 내보낼 수 없습니다.")
