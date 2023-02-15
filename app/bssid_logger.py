#!/usr/bin/env python3
import logging
import os
import time
import inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)

formatter = logging.Formatter('%(levelname)s: %(message)s')

PATH = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(
	filename='{}/XIQ_bssid_csv.log'.format(parent_dir),
	filemode='a',
	level=os.environ.get("LOGLEVEL", "INFO"),
	format= '{}: %(name)s - %(levelname)s - %(message)s'.format(time.strftime("%Y-%m-%d %H:%M"))
)

# create console handler for logger.
ch = logging.StreamHandler()
ch.setLevel(level=logging.INFO)
ch.setFormatter(formatter)

logger = logging.getLogger("BSSID_CSV").addHandler(ch)