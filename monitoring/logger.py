"""
Centralized Logging System
Handles logging for all agents and APIs
"""

import logging
from pathlib import Path


# Create logs directory
Path("logs").mkdir(
    exist_ok=True
)

# Configure logging
logging.basicConfig(

    filename="logs/system.log",

    level=logging.INFO,

    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    )
)


class SystemLogger:

    @staticmethod
    def info(message):

        logging.info(message)

        print(f"[INFO] {message}")

    @staticmethod
    def warning(message):

        logging.warning(message)

        print(f"[WARNING] {message}")

    @staticmethod
    def error(message):

        logging.error(message)

        print(f"[ERROR] {message}")