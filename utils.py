import hashlib


def extract_id(filename):
    # use hash function to create unique id of filename
    return hashlib.md5(filename.encode()).hexdigest()[:10]
