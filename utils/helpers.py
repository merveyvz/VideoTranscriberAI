import os
from app.config import TEMP_DIR


def save_uploaded_file(uploaded_file):
    with open(os.path.join(TEMP_DIR, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())
    return os.path.join(TEMP_DIR, uploaded_file.name)
