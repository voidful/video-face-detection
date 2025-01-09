import re

id_reg = re.compile(r'(\d+)(?=\.\w+$)|\[(.*?)\](?!.*\[[^\[\]]*\])')

def extract_id(filename):
    match = re.search(id_reg, filename)
    if not match:
        raise ValueError('ID unfetchable')
    return match.group(1) if match.group(1) else match.group(2)