__author__ = 'denis_makogon'

from gigaspace.common import remote

exceptions = remote.cinderclient.client.exceptions


class BaseCinderActions(remote.RemoteServices):

    def __init__(self):
        super(BaseCinderActions, self).__init__()

    def create_volume(self, size, name):
        try:
            return self.cinderclient.volumes.create(
                size, display_name=name)
        except exceptions.ClientException as e:
            print(str(e))

    def show_volume(self, id_or_name):
        try:
            return self.cinderclient.volumes.get(id_or_name)
        except exceptions.ClientException as e:
            print(str(e))

    def list_volumes(self):
        try:
            return self.cinderclient.volumes.list()
        except exceptions.ClientException as e:
            print(str(e))
