__author__ = 'dmakogon'

import argparse
import sys
import inspect

from gigaspace.common import cfg
from gigaspace.common import context
from gigaspace.common import remote
from gigaspace.common import utils

CONF = cfg.CONF


class GigaspaceToolCommands(object):

    def boot_volume(self, **kwargs):
        """
        Boots volume with given name and size
        """
        _context = context.RequestContext(**kwargs)
        cinderclient = remote.create_cinder_client(_context)

    def list_volumes(self, **kwargs):
        _context = context.RequestContext(**kwargs)
        cinderclient = remote.create_cinder_client(_context)
        volumes = cinderclient.volumes.list()
        for volume in volumes:
            utils.print_dict(volume.__dict__)

    def show_volume(self, name_or_id, **kwargs):
        pass

    def attach_volume(self, **kwargs):
        pass

    def delete_volume(self, id, **kwargs):
        pass

    def execute(self):
        exec_method = getattr(self, CONF.action.name)
        args = inspect.getargspec(exec_method)
        args.args.remove('self')
        kwargs = {}
        for arg in args.args:
            kwargs[arg] = getattr(CONF.action, arg)
        exec_method(**kwargs)


def main():

    parser = argparse.ArgumentParser(description='Process some integers.')
    # parser = parser.add_parser(
    #     'list_volumes', description='List Cinder volumes.')
    parser.add_argument("list_volumes")
    subparser = parser.add_subparsers()
    subparser.add_parser('--os-username')
    subparser.add_parser('--os-tenant-name')
    subparser.add_parser('--os-password')
    subparser.add_parser('--os-auth-url')
    subparser.add_parser('--os-auth-system')

    try:
        args = parser.parse_args()
        sys.exit(0)
    except TypeError as e:
        print("Possible wrong number of arguments supplied %s" % e)
        sys.exit(2)
    except Exception:
        print("Command failed, please check log for more info.")
        raise


if __name__ == "__main__":
    main()
