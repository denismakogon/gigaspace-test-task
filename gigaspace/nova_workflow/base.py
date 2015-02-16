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

    def _build_bdm(self, volume):
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
        return {'vdb': "%s:%s:%s:%s" % (volume.id, '', volume.size, 1)}

    def boot(self, name, flavor, image_id, volume_id):
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
            userdata = self.get_userdata()
            volume = self.cinderclient.volumes.get(volume_id)
            bdm = self._build_bdm(volume)
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
