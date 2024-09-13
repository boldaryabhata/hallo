from datetime import datetime
import sys

def log_debug(msg):
    sys.stderr.write(f"{datetime.now()}  DEBUG  {msg}")
    sys.stderr.flush()

def log_info(msg):
    sys.stderr.write(f"{datetime.now()}  INFO   {msg}")
    sys.stderr.flush()

def log_warn(msg):
    sys.stderr.write(f"{datetime.now()}  WARN   {msg}")
    sys.stderr.flush()

def log_error(msg):
    sys.stderr.write(f"{datetime.now()}  ERROR  {msg}")
    sys.stderr.flush()