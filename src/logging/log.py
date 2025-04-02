from threading import Lock
import uuid
import os

file_lock = Lock()

def __log_set_write__(path, id, message):
    print(f"Adding Log {id}: {message}")
    file_lock.acquire()
    try:
        log_entries = {}
        if os.path.exists(path):
            with open(path, "r") as log_file:
                for line in log_file:
                    key, value = line.strip().split(": ", 1)
                    log_entries[key] = value
        if id is None:
            id = f"Err {str(uuid.uuid4())[0:6]}"
        log_entries[id] = f"{message}"

        with open(path, "w") as log_file:
            for key, value in log_entries.items():
                log_file.write(f"{key}: {value}\n")
    finally:
        file_lock.release()