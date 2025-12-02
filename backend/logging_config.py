import sys
from loguru import logger
from django.conf import settings
import logging


def setup_loguru():
    """Initializes and configures Loguru for the Django project."""

    # 1. Remove Loguru's default handler
    logger.remove()

    # 2. Add Loguru handlers based on environment

    if settings.ENVIRONMENT == 'development':
        # Development: Log everything to console, with colors
        logger.add(
            sys.stderr,
            level="DEBUG",
            colorize=True,
            format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
    else:
        # Staging/Production: Log to file and console (without colors)
        log_file_path = os.path.join(settings.BASE_DIR, 'logs', 'django.log')
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

        # Log to file (rolling, compressed logs)
        logger.add(
            log_file_path,
            level="INFO",
            rotation="10 MB",
            compression="zip",
            enqueue=True  # Important for performance in multi-process environments
        )

        # Log critical/error messages to console for immediate visibility
        logger.add(
            sys.stderr,
            level="WARNING",
            colorize=False,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"
        )

    # 3. Intercept standard Python logging (used by Django, libraries, etc.)
    # This is the crucial step to redirect all other loggers to Loguru
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Get corresponding Loguru level
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Loguru records include context, which we simulate here
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

    # Apply the intercept handler to the root logger
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    # Disable propagation for specific verbose loggers if needed
    logging.getLogger('django.db.backends').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

    logger.info("Loguru logging successfully initialized.")
