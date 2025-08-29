
"""
PROTON
(C) 2022-2042, Kumar Madhukar
Department of Computer Science and Engineering, Indian Institute of Technology Delhi
"""


"""
Various utility functions
"""
import logging
import os
from os import path
import shutil
import sys
from datetime import datetime
from collections import namedtuple
from dataclasses import dataclass

from config import Config as c

def init_logging():
    """
    Initializes the root logger with required info logger
    """
    # Set the log format
    log_format = '\n[%(relativeCreated)s %(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - \n\t %(message)s'

    # Get root logger
    logger = logging.getLogger()
    logger.setLevel( level = logging.INFO )

    # Remove existing handlers (if any)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create log path if it doesnt exist
    if not os.path.exists( c.LOG_PATH ):
        os.mkdir( c.LOG_PATH )

    # Create a file handler for the log file
    log_filename = os.path.join(
        c.LOG_PATH,
        "log_{0}.log".format( 
            datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        )
    )
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)

    # Create a stream handler for stdout
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)  # Adjust the log level as needed
    stream_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(stream_handler)

    # Log the program start
    program_start_time = datetime.now()
    logger.info('Logging to %s', log_filename)

    # Log contents of config
    logger.info("Config has: {}".format( 
        [ (n, v) for n, v in c.__dict__.items() if '__' not in n ]
    ))


def clear_tmp():
    """ Helper to clear temp directory """
    l = logging.getLogger( __name__ )
    if os.path.exists( c.TMP_PATH ):
        l.debug("Temp dir {} exists, deleting".format( 
            c.TMP_PATH ))
        shutil.rmtree( c.TMP_PATH )
    os.mkdir( c.TMP_PATH )

@dataclass
class LoopData:
    """ Data for each loop. Entries not yet calculated may be None """
    full_code : str = None    # Code of the whole program
    loop_code : str = None    # Code of the extracted loop
    loop_id : str = None      # Id of extracted loop
    loop_type : str = None    # Type of loop, may be "WhileStmt", "ForStmt", "DoStmt" 
    beg_line : str = None     # Begining line
    end_line : str = None     # Ending line
    variant : str = None      # Variant, invariant, assigns to check for the loop
    invariant : str = None
    assigns : str = None


""" Represents status of operations """
Status = namedtuple( 'Status', [
    'success',          # Did operation succeed
    'failure_reason',   # Why did operation fail, None if it didn't fail
])

""" Represents Result of operations that may fail """
Result = namedtuple( 'Result', [
    'result',           # Result, None if operation failed
    'failure_reason',   # Why did operation fail, None if it didn't fail
])
