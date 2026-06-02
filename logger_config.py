import logging
import os
import json

def setup_logging(log_file_path):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if not os.path.exists(config_path):
        # Create a default config.json if it doesn't exist
        default_config = {
            "chrome_debug_port": 9222,
            "chrome_user_data_dir": os.path.join(os.path.expanduser("~"), "onvio_chrome_profile"),
            "log_file": "onvio_automation.log"
        }
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=4)
    
    with open(config_path, 'r') as f:
        return json.load(f)

config = load_config()
logger = setup_logging(config['log_file'])
