__author__ = 'denis_makogon'

import os
from gigaspace.common import cfg


def initialize_test_config(config_file):

    cfg.CONF(args=[],
             project='gigaspace',
             default_config_files=[config_file])


def main():
    config_file = os.path.realpath('etc/gigspace/gigaspace.test.conf')
    initialize_test_config([config_file])
