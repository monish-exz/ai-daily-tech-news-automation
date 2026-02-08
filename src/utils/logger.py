import logging
import os


# This function configures logging for the project
def setup_logger():
    # Create logs folder if it does not exist
    os.makedirs("logs", exist_ok=True)

    # Setup log file format and level
    logging.basicConfig(
        filename="logs/execution.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
