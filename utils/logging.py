import logging
import os
from datetime import datetime
from typing import Optional

class Logger:
    """Logging utility for DataSync application."""
    
    def __init__(self, name: str, log_folder: str = "logs"):
        self.name = name
        self.log_folder = log_folder
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger with file and console handlers."""
        # Create logs directory if it doesn't exist
        os.makedirs(self.log_folder, exist_ok=True)
        
        # Create logger
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        
        # File handler
        log_filename = f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        log_filepath = os.path.join(self.log_folder, log_filename)
        file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str, exception: Optional[Exception] = None) -> None:
        """Log error message."""
        if exception:
            self.logger.error(f"{message}: {str(exception)}", exc_info=True)
        else:
            self.logger.error(message)
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)
    
    def success(self, message: str) -> None:
        """Log success message as info."""
        self.logger.info(f"SUCCESS: {message}")