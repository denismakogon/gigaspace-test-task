__author__ = 'denis_makogon'

from gigaspace.common import remote

exceptions = remote.cinderclient.client.exceptions


class BaseCinderActions(remote.RemoteServices):
    """
    Base Cinder actions class
    """
    def __init__(self):
        super(BaseCinderActions, self).__init__()

    def create_volume(self, size, name):
        """
        Create volume by given size and display name
        :param size: volume size
        :type size basestring
        :param name: volume display name
        :type name: basestring
        :return volume info
        :rtype: dict
        """
        try:
            volume = self.cinderclient.volumes.create(
                int(size), name=name)
            return volume
        except exceptions.ClientException as e:
            raise

    def show_volume(self, id_or_name):
        """
        Returns volume info by given ID or name
        :param id_or_name: volume ID or name
        :type id_or_name: basestring
        :return volume info
        :rtype: dict
        """
        try:
            volume = self.cinderclient.volumes.get(id_or_name)
            return volume
        except exceptions.ClientException as e:
            raise

    def list_volumes(self):
        """
        Lists volumes
        :return: list of volumes
        :type list of volumes: list
        """
        try:
            return self.cinderclient.volumes.list()
        except exceptions.ClientException as e:
            raise
