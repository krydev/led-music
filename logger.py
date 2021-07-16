import logging

DEBUG = True

LOGGER = logging.getLogger(__name__)
if DEBUG:
	import sys

	LOGGER.setLevel(logging.DEBUG)
	h = logging.StreamHandler(sys.stdout)
	h.setLevel(logging.DEBUG)
	LOGGER.addHandler(h)