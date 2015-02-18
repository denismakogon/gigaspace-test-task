__author__ = 'denis_makogon'

import sys
import proboscis

from oslo_config import cfg

from gigaspace.cmd import common
from gigaspace.common import cfg as config
from gigaspace.tests.functional import test_workflow

CONF = cfg.CONF


class Tester(object):

    def functional(self):
        sys.argv = []
        sys.argv.append('--groups=functional')
        proboscis.register(groups=['functional'],
                           depends_on_groups=[test_workflow.GROUP_WORKFLOW])
        proboscis.TestProgram(groups=['functional']).run_and_exit()

CATS = {
    'run': Tester
}

category_opt = cfg.SubCommandOpt('category',
                                 title='Command categories',
                                 help='Available categories',
                                 handler=common.add_command_parsers(CATS))


def main():
    """Parse options and call the appropriate class/method."""
    common._main(CONF, config, category_opt, sys.argv)

if __name__ == "__main__":
    main()
