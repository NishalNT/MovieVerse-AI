import logging
import sys
from datetime import datetime
from typing import Any, Dict
import json

class MovieVerseLogger:
    """Custom logger for MovieVerse AI with different log levels and formatting"""
    
    def __init__(self, name: str = "movieverse"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Create console handler with formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # Create file handler for persistent logs
        file_handler = logging.FileHandler(f"movieverse_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str, data: Any = None):
        """Log debug message with optional data"""
        if data:
            self.logger.debug(f"{message} | Data: {self._format_data(data)}")
        else:
            self.logger.debug(message)
    
    def info(self, message: str, data: Any = None):
        """Log info message with optional data"""
        if data:
            self.logger.info(f"{message} | Data: {self._format_data(data)}")
        else:
            self.logger.info(message)
    
    def warning(self, message: str, data: Any = None):
        """Log warning message with optional data"""
        if data:
            self.logger.warning(f"{message} | Data: {self._format_data(data)}")
        else:
            self.logger.warning(message)
    
    def error(self, message: str, data: Any = None):
        """Log error message with optional data"""
        if data:
            self.logger.error(f"{message} | Data: {self._format_data(data)}")
        else:
            self.logger.error(message)
    
    def critical(self, message: str, data: Any = None):
        """Log critical message with optional data"""
        if data:
            self.logger.critical(f"{message} | Data: {self._format_data(data)}")
        else:
            self.logger.critical(message)
    
    def _format_data(self, data: Any) -> str:
        """Format data for logging"""
        try:
            if isinstance(data, (dict, list)):
                return json.dumps(data, default=str, indent=2)
            return str(data)
        except:
            return str(data)

# Create global logger instance
logger = MovieVerseLogger()