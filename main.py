# main.py

from src.frontend.front import Dashboard
from src.pipeline.logger import Logger
from src.pipeline.exception import CustomException

def main():
    logger = Logger()
    try:
        logger.info("Starting the application...")
        dashboard = Dashboard()
        dashboard.run()
        logger.info("Application running successfully.")
    except CustomException as e:
        logger.error(f"Custom application error occurred: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()
