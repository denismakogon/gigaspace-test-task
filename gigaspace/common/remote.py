__author__ = 'dmakogon'


from gigaspace.common import cfg
from cinderclient.v2 import client as CinderClient
from novaclient.v1_1.client import Client as NovaClient
from oslo.utils.importutils import import_class

CONF = cfg.CONF


def nova_client(context):
    # Required options:
    # --os-username
    # --os-tenant-name
    # --os-auth-system
    # --os-password
    # --os-auth-url
    client = NovaClient(context.os_username, context.os_password, context.os_tenant_name)
    return client


def cinder_client(context):
    # Required options:
    # --os-username
    # --os-tenant-name
    # --os-auth-system
    # --os-password
    # --os-auth-url
    client = CinderClient.Client(context.os_username, context.os_password, context.os_tenant_name)
    return client

create_nova_client = import_class(CONF.remote_nova_client)
create_cinder_client = import_class(CONF.remote_cinder_client)
