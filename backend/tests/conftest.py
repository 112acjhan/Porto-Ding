import sys
from pathlib import Path


backend_root_directory = Path(__file__).resolve().parents[1]
backend_root_directory_as_text = str(backend_root_directory)

if backend_root_directory_as_text not in sys.path:
    sys.path.insert(0, backend_root_directory_as_text)
