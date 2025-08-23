import logging  
import logging.config  
  
DEFAULT_LOGGING_CONFIG = {  
    'version': 1,  
    'formatters': {  
        'standard': {  
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'  
        },  
    },  
    'handlers': {  
        'console': {  
            'class': 'logging.StreamHandler',  
            'formatter': 'standard',  
            'level': 'INFO',  
        },  
        'file_handler': {  
            'class': 'logging.handlers.RotatingFileHandler',  
            'formatter': 'standard',  
            'filename': 'file_processing.log',  
            'maxBytes': 10485760,  # 10MB  
            'backupCount': 5,  
            'level': 'DEBUG',  
        },  
    },  
    'loggers': {  
        'file_processing': {  
            'handlers': ['console', 'file_handler'],  
            'level': 'DEBUG',  
            'propagate': False  
        },  
    }  
}  
  
def setup_logging():  
    logging.config.dictConfig(DEFAULT_LOGGING_CONFIG)