__author__ = 'denis_makogon'

import uuid

from cinderclient import client as novaclient
from novaclient import client as cinderclient

cinder_exceptions = cinderclient.exceptions
nova_exceptions = novaclient.exceptions


class FakeServer(object):

    def __init__(self, id, name, image_id, flavor_ref,
                 block_device_mapping, volumes):
        self.id = id
        self.name = name
        self.image_id = image_id
        self.flavor_ref = flavor_ref
        self.old_flavor_ref = None
        self._current_status = "BUILDING"
        self.volumes = volumes
        self.bdm = block_device_mapping
        info_vols = []
        for volume in self.volumes:
            info_vols.append({'id': volume.id})
            volume.set_attachment(id)
        setattr(self,
                'os-extended-volumes:volumes_attached',
                info_vols)

    def delete(self):
        for volume in self.volumes:
            volume._current_status = 'deleting'
            volume.delete_attachment(self.id)
            Cinder().delete(volume.id)
        self._current_status = "SHUTDOWN"

    @property
    def status(self):
        return self._current_status


class FakeBlockDeviceMappingInfo(object):

    def __init__(self, id, device, _type, size, delete_on_terminate):
        self.volume_id = id
        self.device = device
        self.type = _type
        self.size = size
        self.delete_on_terminate = delete_on_terminate


FAKE_SERVERS_DB = {}


class Nova(object):

    def __init__(self):
        self.db = FAKE_SERVERS_DB
        self.volumes = Cinder()

    def reboot(self, server_id, **kwargs):
        import time
        server = self.get(server_id)
        server._current_status = "REBOOT"
        time.sleep(5)
        server._current_status = "ACTIVE"

    def create(self, name, image_id, flavor_ref, userdata=None,
               block_device_mapping=None):
        id = "FAKE_%s" % uuid.uuid4()
        volumes = self._get_volumes_from_bdm(block_device_mapping)
        for volume in volumes:
            volume._current_status = 'in-use'
        server = FakeServer(id, name, image_id, flavor_ref,
                            block_device_mapping, volumes)
        self.db[id] = server

        server._current_status = "ACTIVE"
        return server

    def _get_volumes_from_bdm(self, block_device_mapping):
        volumes = []
        if block_device_mapping is not None:
            for device in block_device_mapping:
                mapping = block_device_mapping[device]
                (id, _type, size, delete_on_terminate) = mapping.split(":")
                volume = self.volumes.get(id)
                volume.mapping = FakeBlockDeviceMappingInfo(
                    id, device, _type, size, delete_on_terminate)
                volumes.append(volume)
        return volumes

    def get(self, id):
        if id not in self.db.keys():
            raise nova_exceptions.NotFound(404)
        else:
            return self.db[id]

    def list(self):
        return [v for (k, v) in self.db.items()]

    def delete(self, id):
        if id not in self.db.keys():
            raise nova_exceptions.NotFound("HTTP 404. Not Found.")
        else:
            del self.db[id]


class FakeVolume(object):

    def __init__(self, id, size, name):
        self.attachments = []
        self.id = id
        self.size = size
        self.name = name
        self._current_status = "building"
        self.device = "vdb"

    def __repr__(self):
        msg = ("FakeVolume(id=%s, size=%s, name=%s, "
               "_current_status=%s)")
        params = (self.id, self.size, self.name,
                  self._current_status)
        return (msg % params)

    @property
    def created_at(self):
        return "2020-01-01-12:59:59"

    def get(self, key):
        return getattr(self, key)

    def set_attachment(self, server_id):
        for attachment in self.attachments:
            if attachment['server_id'] == server_id:
                return  # Do nothing
        self.attachments.append({'server_id': server_id,
                                 'device': self.device,
                                 'id': self.id,
                                 'volume_id': self.id})

    def delete_attachment(self, server_id):
        for attachment in self.attachments:
            if attachment['server_id'] == server_id:
                self.attachments.pop(
                    self.attachments.index(attachment))

    @property
    def status(self):
        return self._current_status

    def delete(self):
        Cinder().delete(self.id)

FAKE_VOLUMES_DB = {}


class Cinder(object):

    def __init__(self):
        self.db = FAKE_VOLUMES_DB

    def get(self, id):
        if id not in self.db.keys():
            raise cinder_exceptions.NotFound(
                404, message="Volume not found.")
        else:
            return self.db[id]

    def create(self, size, name=None, **kwargs):
        id = "FAKE_VOL_%s" % uuid.uuid4()
        volume = FakeVolume(id, size, name)
        self.db[id] = volume
        volume._current_status = "available"

        return volume

    def list(self):
        return [self.db[key] for key in self.db]

    def delete(self, id):
        if id not in self.db.keys():
            raise Exception
        else:
            del self.db[id]

    def create_server_volume(self, server_id, volume_id, device):
        server = Nova().get(server_id)
        volume = self.get(volume_id)
        volumes = getattr(server, 'os-extended-volumes:volumes_attached')
        volumes.append({'id': volume.id})
        setattr(server,
                'os-extended-volumes:volumes_attached',
                volumes)
        volume.device = device
        volume.set_attachment(server_id)
        if volume._current_status != "available":
            raise Exception("Invalid volume status: "
                            "expected 'available' but was '%s'" %
                            volume._current_status)
        volume._current_status = "in-use"

    def delete_server_volume(self, server_id, volume_id):
        server = Nova().get(server_id)
        volumes = getattr(
            server,
            'os-extended-volumes:volumes_attached')
        volumes.pop(volumes.index({'id': volume_id}))
        setattr(server,
                'os-extended-volumes:volumes_attached',
                volumes)
        volume = self.get(volume_id)
        volume.delete_attachment(server_id)
        if volume._current_status != 'in-use':
            raise Exception("Invalid volume status: "
                            "expected 'in-use' but was '%s'" %
                            volume._current_status)
        volume._current_status = "available"


def fake_create_nova_client():
    class _fake_nova():
        def __init__(self):
            self.servers = Nova()
            self.volumes = Cinder()
    return _fake_nova()


def fake_create_cinder_client():
    class _fake_cinder():
        def __init__(self):
            self.volumes = Cinder()
    return _fake_cinder()
