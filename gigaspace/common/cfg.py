__author__ = 'dmakogon'

from oslo.config import cfg

common_opts = [
    cfg.StrOpt('cinder_url', help='URL without the tenant segment.'),
    cfg.StrOpt('cinder_service_type', default='volumev2',
               help='Service type to use when searching catalog.'),
    cfg.StrOpt('nova_compute_url', help='URL without the tenant segment.'),
    cfg.StrOpt('nova_compute_service_type', default='compute',
               help='Service type to use when searching catalog.'),
    cfg.StrOpt('nova_compute_endpoint_type', default='publicURL',
               help='Service endpoint type to use when searching catalog.'),
    cfg.StrOpt('cinder_endpoint_type', default='publicURL',
               help='Service endpoint type to use when searching catalog.'),
    cfg.StrOpt('remote_nova_client',
               default='gigaspace.common.remote.nova_client',
               help='Client to send Nova calls to.'),
    cfg.StrOpt('remote_cinder_client',
               default='gigaspace.common.remote.cinder_client',
               help='Client to send Cinder calls to.'),
    cfg.StrOpt('auth_url', default='http://0.0.0.0:5000/v2.0',
               help='Authentication URL.'),
]

CONF = cfg.CONF

CONF.register_opts(common_opts)


def parse_args(default_config_files=None):
    cfg.CONF(project='gigaspace',
             version="initial",
             default_config_files=default_config_files)
