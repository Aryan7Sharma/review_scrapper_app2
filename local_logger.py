import logging
def logss():
    logging.basicConfig(filename="logging.txt", level=logging.INFO, format='%(filename)s: %(levelname)s: %(message)s: %(asctime)s')
    logs = logging.getLogger()
    return logs