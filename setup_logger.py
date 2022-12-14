# setup_logger.py
#import logging

#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger('abc')

#logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)
#
#formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
#
#file_handler = logging.FileHandler('sample.log')
#file_handler.setLevel(logging.DEBUG)
#file_handler.setFormatter(formatter)
#
#stream_handler = logging.StreamHandler()
#stream_handler.setFormatter(formatter)
#
#logger.addHandler(file_handler)
#logger.addHandler(stream_handler)

import logging
import logging.config
logging.config.fileConfig('bot.logconf')
