__author__ = "denis_makogon"

import six
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
        attrs = ['id', 'description', 'size']
        cinder = cinder_workflow.BaseCinderActions()
        volumes = cinder.list_volumes()
        utils.print_list(volumes, attrs)

    @common.args("--size", dest="size")
    @common.args("--display-name", dest="name")
    def create(self, size, name):
        cinder = cinder_workflow.BaseCinderActions()
        utils.print_dict(cinder.create_volume(size, name).__dict__)

    @common.args("--id-or-name", dest='id_or_name')
    def show(self, id_or_name):
        cinder = cinder_workflow.BaseCinderActions()
        volume = cinder.show_volume(id_or_name)
        utils.print_dict(volume.__dict__)


class Instances(object):

    @common.args('--volume-id', dest='volume_id')
    @common.args('--instance-id', dest='instance_id')
    @common.args('--device_path', dest='device_path', default='/dev/vdb')
    def attach_volume(self, volume_id, instance_id, device_path):
        print("good")

    @common.args('--name', dest='name')
    @common.args('--flavor', dest='flavor')
    @common.args('--image_id', dest='image_id')
    @common.args('--block-mapping-device', dest='block_device_mapping')
    def boot(self, name, flavor, image_id, block_device_mapping):
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
    CONF.register_cli_opt(category_opt)
    config.parse_args(sys.argv)
    fn = CONF.category.action_fn
    fn_args = [arg.decode('utf-8') for arg in CONF.category.action_args]
    fn_kwargs = {}
    for k in CONF.category.action_kwargs:
        v = getattr(CONF.category, 'action_kwarg_' + k)
        if v is None:
            continue
        if isinstance(v, six.string_types):
            v = v.decode('utf-8')
        fn_kwargs[k] = v

    try:
        ret = fn(*fn_args, **fn_kwargs)
        return ret
    except Exception as e:
        print(str(e))

if __name__ == "__main__":
    main()
