import logging

# Set up basic configuration for the logging system
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('debug.log'),
    ]
)

# Create a logger object that can be imported and used in other modules
logger = logging.getLogger('SimulationLogger')