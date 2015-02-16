__author__ = 'dmakogon'


from gigaspace.common import cfg
from cinderclient.v2 import client as cinderclient
from novaclient.v1_1 import client as novaclient
from oslo.utils import importutils

CONF = cfg.CONF


class RemoteServices(object):

    _novaclient = None
    _cinderclient = None

    @property
    def novaclient(self):
        """
        Nova ReST client initializer
        :return: authenticated novaclient
        :rtype: novaclient.Client
        """
        if not self._novaclient:
            _create_nova_client = importutils.import_class(
                CONF.remote_nova_client)
            self._novaclient = _create_nova_client()
        return self._novaclient

    @property
    def cinderclient(self):
        """
        Cinder ReST client initializer
        :return: authenticated novaclient
        :rtype: novaclient.Client
        """
        if not self._cinderclient:
            _create_cinder_client = importutils.import_class(
                CONF.remote_cinder_client)
            self._cinderclient = _create_cinder_client()
        return self._cinderclient


def _nova_client():
    """
    Instantiates Nova ReST client
    :return: authenticated novaclient
    :rtype: novaclient.Client
    """
    CONF.reload_config_files()
    _client = novaclient.Client(CONF.os_username,
                                CONF.os_password,
                                CONF.os_tenant_name,
                                auth_url=CONF.os_auth_url,
                                timeout=40)
    _client.authenticate()
    return _client


def _cinder_client():
    """
    Instantiates Cinder ReST client
    :return: authenticated cinderclient
    :rtype: cinderclient.Client
    """
    CONF.reload_config_files()
    _client = cinderclient.Client(CONF.os_username,
                                  CONF.os_password,
                                  project_id=CONF.os_tenant_name,
                                  auth_url=CONF.os_auth_url,
                                  timeout=40)
    _client.authenticate()
    return _client
