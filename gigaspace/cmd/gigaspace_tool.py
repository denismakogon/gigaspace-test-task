__author__ = "denis_makogon"

import sys

from oslo_config import cfg

from gigaspace.cmd import common
from gigaspace.common import cfg as config
from gigaspace.common import utils
from gigaspace.cinder_workflow import (
    base as cinder_workflow)
from gigaspace.nova_workflow import (
    base as nova_workflow)

CONF = cfg.CONF


class Volumes(object):

    def list(self, *args, **kwargs):
        """
        CLI representation of 'list volumes'
        :param args:
        :param kwargs:
        :return: CLI representation of 'list of volumes'
        :rtype: None
        """
        attrs = ['id', 'size', 'name', 'status', 'bootable', 'attachments']
        cinder = cinder_workflow.BaseCinderActions()
        volumes = cinder.list_volumes()
        utils.print_list(volumes, attrs)

    @common.args("--size", dest="size",
                 help='Volume size')
    @common.args("--display-name", dest="name",
                 help='Volume name')
    def create(self, size, name):
        """
        CLI representation of 'create volume'
        :param size: volume size
        :type size: basestring
        :param name: volume display name
        :type name: basestring
        :return: CLI representation of 'create volume;
        :rtype: None
        """
        cinder = cinder_workflow.BaseCinderActions()
        volume = cinder.create_volume(size, name)._info
        del volume['links']
        utils.print_dict(volume)

    @common.args("--id-or-name", dest='id_or_name',
                 help='Volume ID or name')
    def show(self, id_or_name):
        """
        CLI representation of 'show volume'
        :param id_or_name: volume ID or name
        :type id_or_name: basestring
        :return: CLI representation of 'show volume'
        :rtype: None
        """
        cinder = cinder_workflow.BaseCinderActions()
        volume = cinder.show_volume(id_or_name)._info
        del volume['links']
        utils.print_dict(volume)


class Instances(object):

    def _boot(self, name, flavor, image_id, volume_id=None):
        """
        CLI representation of 'boot instance'
        :param name: instance name
        :type name: basestring
        :param flavor: flavor
        :type flavor: basestring
        :param image_id: Glance image id
        :type image_id: basestring
        :return server
        :rtype: dict
        """
        nova = nova_workflow.BaseNovaActions()
        server = nova.boot(
            name, flavor, image_id, volume_id)._info
        del server['links']
        return server

    @common.args('--name', dest='name',
                 help='Instance name')
    @common.args('--flavor', dest='flavor',
                 help='Flavor id')
    @common.args('--image-id', dest='image_id',
                 help='Glance image ID')
    @common.args('--volume-id', dest='volume_id',
                 help='Volume ID')
    def boot_with_volume(self, name, flavor, image_id, volume_id):
        """
        CLI representation of 'boot instance'
        :param name: instance name
        :type name: basestring
        :param flavor: flavor
        :type flavor: basestring
        :param image_id: Glance image id
        :type image_id: basestring
        :return: CLI representation of 'boot instance'
        :rtype: None
        """
        server = self._boot(name, flavor, image_id,
                            volume_id=volume_id)
        utils.print_dict(server)

    @common.args('--name', dest='name',
                 help='Instance name')
    @common.args('--flavor', dest='flavor',
                 help='Flavor id')
    @common.args('--image-id', dest='image_id',
                 help='Glance image ID')
    def boot_without_volume(self, name, flavor, image_id):
        """
        CLI representation of 'boot instance'
        :param name: instance name
        :type name: basestring
        :param flavor: flavor
        :type flavor: basestring
        :param image_id: Glance image id
        :type image_id: basestring
        :return: CLI representation of 'boot instance'
        :rtype: None
        """
        server = self._boot(name, flavor, image_id)
        utils.print_dict(server)

    @common.args('--server-id', dest="server_id")
    def delete(self, server_id):
        nova = nova_workflow.BaseNovaActions()
        nova.delete(server_id)
        print(str("Server accepted for deletion."))

    @common.args('--volume-id', dest="volume_id")
    @common.args('--server-id', dest="server_id")
    def attach_volume(self, volume_id, server_id):
        nova = nova_workflow.BaseNovaActions()
        nova.create_server_volume(volume_id, server_id)
        print("Server requires:"
              "\n - restart to discover new block storage"
              "\n - manual volume formatting")

    @common.args('--volume-id', dest="volume_id")
    @common.args('--server-id', dest="server_id")
    def detach_volume(self, volume_id, server_id):
        nova = nova_workflow.BaseNovaActions()
        nova.delete_server_volume(server_id, volume_id)


CATS = {
    'volumes': Volumes,
    'instances': Instances
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
