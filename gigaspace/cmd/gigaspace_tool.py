__author__ = "denis_makogon"

import sys

from oslo_config import cfg

from gigaspace.cmd import common
from gigaspace.common import cfg as config
from gigaspace.common import utils
from gigaspace.cinder_workflow import (
    base as cinder_workflow)

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
        attrs = ['id', 'description', 'size']
        cinder = cinder_workflow.BaseCinderActions()
        volumes = cinder.list_volumes()
        utils.print_list(volumes, attrs)

    @common.args("--size", dest="size")
    @common.args("--display-name", dest="name")
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
        utils.print_dict(cinder.create_volume(size, name).__dict__)

    @common.args("--id-or-name", dest='id_or_name')
    def show(self, id_or_name):
        """
        CLI representation of 'show volume'
        :param id_or_name: volume ID or name
        :type id_or_name: basestring
        :return: CLI representation of 'show volume'
        :rtype: None
        """
        cinder = cinder_workflow.BaseCinderActions()
        volume = cinder.show_volume(id_or_name)
        utils.print_dict(volume.__dict__)


class Instances(object):

    @common.args('--volume-id', dest='volume_id')
    @common.args('--instance-id', dest='instance_id')
    @common.args('--device_path', dest='device_path', default='/dev/vdb')
    def attach_volume(self, volume_id, instance_id, device_path):
        """
        CLI representation of 'attach volume'
        :param volume_id: volume ID
        :type volume_id: basestring
        :param instance_id: instance ID
        :type instance_id: basestring
        :param device_path: root FS device path
        :return: CLI representation of 'attach volume'
        :rtype: None
        """
        print("good")

    @common.args('--name', dest='name')
    @common.args('--flavor', dest='flavor')
    @common.args('--image_id', dest='image_id')
    @common.args('--block-mapping-device', dest='block_device_mapping')
    def boot(self, name, flavor, image_id, block_device_mapping):
        """
        CLI representation of 'boot instance'
        :param name: instance name
        :type name: basestring
        :param flavor: flavor
        :type flavor: basestring
        :param image_id: Glance image id
        :type image_id: basestring
        :param block_device_mapping: block mapping device
        :type block_device_mapping: basestring
        :return: CLI representation of 'boot instance'
        :rtype: None
        """
        print("good")


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
