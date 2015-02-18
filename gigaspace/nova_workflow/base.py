__author__ = 'dmakogon'

from gigaspace.common import templating
from gigaspace.common import remote

nova_exceptions = remote.novaclient.client.exceptions
cinder_exceptions = remote.cinderclient.client.exceptions


class BaseNovaActions(remote.RemoteServices, templating.UserdataTemplate):
    """
    Base Cinder actions class
    """
    def __init__(self):
        super(BaseNovaActions, self).__init__()

    def _build_bdm(self, volume_id):
        """
        Block device mapping is used to attach volume
        during instance bootstrap.
        :param volume volume object
        :type volume: cinderclient.v2.volumes.Volume
        :return block device mapping V1
        :rtype: dict
        """
        # <id>:[<type>]:[<size(GB)>]:[<delete_on_terminate>]
        # setting the delete_on_terminate instance to true=1
        if volume_id:
            volume = self.cinderclient.volumes.get(volume_id)
            return {'vdb': "%s:%s:%s:%s" % (volume.id, '', volume.size, 1)}

    def boot(self, name, flavor, image_id, volume_id=None):
        """
        Boots an instance by given description
        :param name: instance name
        :type name: basestring
        :param flavor: instance flavor
        :type flavor: basestring
        :param image_id: image id to boot instance from
        :type image_id: basestring
        :param volume_id: volume id
        :type volume_id: basestring
        :return server: server description
        :rtype: novaclient.v1_1.servers.Server
        """
        try:
            bdm = self._build_bdm(volume_id)
            userdata = self.get_userdata() if bdm else None
            server = self.novaclient.servers.create(
                name, image_id, flavor,
                userdata=userdata,
                block_device_mapping=bdm)
            return server
        except (Exception, nova_exceptions.ClientException,
                cinder_exceptions.ClientException):
            raise

    def delete(self, id):
        try:
            self.novaclient.servers.delete(id)
        except nova_exceptions.ClientException:
            raise

    def get(self, id):
        """
        Retrives server if it exists
        :param id: server ID
        :type id: basestring
        :return server
        :rtype: novaclient.v1_1.servers.Server
        """
        try:
            return self.novaclient.servers.get(id)
        except nova_exceptions.NotFound:
            raise

    def create_server_volume(self, volume_id, server_id):
        """
        Attaches volume into server.
        :param volume_id: volume ID
        :type volume_id: basestring
        :param server_id: server ID
        :type server_id: basestring
        :return: None
        :rtype: None
        """
        try:
            self.novaclient.volumes.create_server_volume(
                server_id, volume_id, '/dev/vdb')
        except nova_exceptions.ClientException:
            raise

    def delete_server_volume(self, server_id, attachment_id):
        """
        Detaches volume from server
        :param server_id: server ID
        :param attachment_id: volume ID
        :return: None
        :rtype: None
        """
        try:
            self.novaclient.volumes.delete_server_volume(
                server_id, attachment_id)
        except nova_exceptions.ClientException:
            raise
