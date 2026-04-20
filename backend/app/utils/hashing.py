import hashlib

# generate SHA-256 for files
def calucalte_file_hash(file_path):
    # init SHA-256 object
    sha256_hash = hashlib.sha256()

    # 'rb' (read binary) mode to open file
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    # return hexdigit string (fingerprint)
    return sha256_hash.hexdigest()

