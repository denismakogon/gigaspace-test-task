__author__ = 'dmakogon'

from oslo.config import cfg

common_opts = [
    cfg.StrOpt('remote_nova_client',
               default='gigaspace.common.remote._nova_client',
               help='Client to send Nova calls to.'),
    cfg.StrOpt('remote_cinder_client',
               default='gigaspace.common.remote._cinder_client',
               help='Client to send Cinder calls to.'),
    cfg.StrOpt('os_username', default="demo"),
    cfg.StrOpt('os_password', default="demo"),
    cfg.StrOpt('os_tenant_name', default="demo"),
    cfg.StrOpt('os_auth_url', default="http://localhost:5000/v2.0/"),
    cfg.StrOpt('os_auth_system', default='keystone'),
]

CONF = cfg.CONF

CONF.register_opts(common_opts)


def parse_args(argv, default_config_files=None):
    cfg.CONF(args=argv[1:],
             project='gigaspace',
             version="default",
             default_config_files=default_config_files)
