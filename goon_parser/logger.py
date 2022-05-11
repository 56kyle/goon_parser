
import logging

log = logging.getLogger("Basic Logger")
log.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
log.addHandler(stream_handler)

file_handler = logging.FileHandler("error.log")
file_handler.setLevel(logging.ERROR)
log.addHandler(file_handler)
