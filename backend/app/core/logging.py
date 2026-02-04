import logging
import logging.config
import json
import warnings
from datetime import datetime
from pythonjsonlogger import jsonlogger
from app.core.config import DEBUG, ENVIRONMENT

# Suppress passlib/bcrypt compatibility warning
warnings.filterwarnings("ignore", message=".*bcrypt version.*")
logging.getLogger('passlib.handlers.bcrypt').setLevel(logging.ERROR)

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['environment'] = ENVIRONMENT
        log_record['level'] = record.levelname
        log_record['logger'] = record.name

def setup_logging():
    if DEBUG:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(logger)s %(message)s')
        log_handler = logging.StreamHandler()
        log_handler.setFormatter(formatter)
        
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(log_handler)
        
        logging.getLogger('redis').setLevel(logging.WARNING)

auth_logger = logging.getLogger('app.auth')
task_logger = logging.getLogger('app.tasks')
db_logger = logging.getLogger('app.database')
cache_logger = logging.getLogger('app.cache')
request_logger = logging.getLogger('app.request')
