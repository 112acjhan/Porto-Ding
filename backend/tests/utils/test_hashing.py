import pytest
import hashlib
import os 
from app.utils.hashing import calculate_file_hash

def test_calculate_hash_success(tmp_path):
    # test data and file
    test_content = b"testing"
    test_file = tmp_path / "dummy.txt"
    test_file.write_bytes(test_content)

    # calculate expected Hash
    expected_hash = hashlib.sha256(test_content).hexdigest()

    # run function
    actual_hash = calculate_file_hash(str(test_file))

    # Assert
    assert actual_hash == expected_hash

def test_calculate_filehash_file_not_found():
    with pytest.raises(FileNotFoundError):  
        calculate_file_hash("non_existent_file.txt")