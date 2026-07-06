from pathlib import Path


def project_root():
    return Path(__file__).resolve().parents[2]


def data_directory(root=None):
    return Path(root if root is not None else project_root()) / "data"


def json_file_path(root=None):
    return data_directory(root) / "prompts.json"
