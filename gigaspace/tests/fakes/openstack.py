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
        self._current_status = "BUILD"
        self.volumes = volumes
        info_vols = []
        for volume in self.volumes:
            info_vols.append({'id': volume.id})
            volume.set_attachment(id)
            volume.schedule_status("in-use", 1)
        self.old_host = None
        setattr(self, 'OS-EXT-AZ:availability_zone', 'nova')

        self._info = {'os:volumes': info_vols}
        self.bdm = block_device_mapping

    def delete(self):
        self.schedule_status = []
        self._current_status = "SHUTDOWN"


class FakeBlockDeviceMappingInfo(object):

    def __init__(self, id, device, _type, size, delete_on_terminate):
        self.volumeId = id
        self.device = device
        self.type = _type
        self.size = size
        self.delete_on_terminate = delete_on_terminate


FAKE_SERVERS_DB = {}


class Nova(object):

    def __init__(self):
        self.db = FAKE_SERVERS_DB
        self.volumes = Cinder()

    def create(self, name, image_id, flavor_ref, files=None, userdata=None,
               block_device_mapping=None, volume=None, security_groups=None,
               availability_zone=None, nics=None, config_drive=False, keyname=None):
        id = "FAKE_%s" % uuid.uuid4()
        volumes = self._get_volumes_from_bdm(block_device_mapping)
        for volume in volumes:
            volume._current_status = 'in-use'
        server = FakeServer(self, id, name, image_id, flavor_ref,
                            block_device_mapping, volumes)
        self.db[id] = server
        if name.endswith('SERVER_ERROR'):
            raise nova_exceptions.ClientException("Fake server create error.")

        if availability_zone == 'BAD_ZONE':
            raise nova_exceptions.ClientException("The requested availability "
                                                  "zone is not available.")

        if nics:
            if 'port-id' in nics[0] and nics[0]['port-id'] == "UNKNOWN":
                raise nova_exceptions.ClientException("The requested "
                                                      "port-id is not "
                                                      "available.")

        server._current_status = "ACTIVE"
        return server

    def _get_volumes_from_bdm(self, server):
        volumes = []
        if server.block_device_mapping is not None:
            # block_device_mapping is a dictionary, where the key is the
            # device name on the compute instance and the mapping info is a
            # set of fields in a string, separated by colons.
            # For each device, find the volume, and record the mapping info
            # to another fake object and attach it to the volume
            # so that the fake API can later retrieve this.
            for device in server.block_device_mapping:
                mapping = server.block_device_mapping[device]
                (id, _type, size, delete_on_terminate) = mapping.split(":")
                volume = self.volumes.get(id)
                volume.mapping = FakeBlockDeviceMappingInfo(
                    id, device, _type, size, delete_on_terminate)
                volumes.append(volume)
        return volumes

    def list(self):
        return [v for (k, v) in self.db.items() if self.can_see(v.id)]    def list(self):
        return [v for (k, v) in self.db.items() if self.can_see(v.id)]

class FakeVolume(object):

    def __init__(self, id, size, name, description, volume_type):
        self.attachments = []
        self.id = id
        self.size = size
        self.name = name
        self.description = description
        self._current_status = "BUILD"
        self.device = "vdb"
        self.volume_type = volume_type

    def __repr__(self):
        msg = ("FakeVolume(id=%s, size=%s, name=%s, "
               "description=%s, _current_status=%s)")
        params = (self.id, self.size, self.name,
                  self.description, self._current_status)
        return (msg % params)

    @property
    def availability_zone(self):
        return "fake-availability-zone"

    @property
    def created_at(self):
        return "2020-01-01-12:59:59"

    def get(self, key):
        return getattr(self, key)

    def set_attachment(self, server_id):
        """Fake method we've added to set attachments. Idempotent."""
        for attachment in self.attachments:
            if attachment['server_id'] == server_id:
                return  # Do nothing
        self.attachments.append({'server_id': server_id,
                                 'device': self.device})

    def delete_attachment(self, server_id):
        for attachment in self.attachments:
            if attachment['server_id'] == server_id:
                self.attachments.pop(
                    self.attachments.index(attachment))

    @property
    def status(self):
        return self._current_status


FAKE_VOLUMES_DB = {}


class Cinder(object):

    def __init__(self):
        self.db = FAKE_VOLUMES_DB

    def get(self, id):
        if id not in self.db.keys():
            raise cinder_exceptions.NotFound("Volume not found", 404)
        else:
            return self.db[id]

    def create(self, size, display_name=None,
               description=None, volume_type=None):
        id = "FAKE_VOL_%s" % uuid.uuid4()
        volume = FakeVolume(id, size, display_name,
                            description, volume_type)
        self.db[id] = volume
        volume._current_status = "available"

        return volume

    def list(self, detailed=True):
        return [self.db[key] for key in self.db]

    def delete_server_volume(self, server_id, volume_id):
        volume = self.get(volume_id)
        volume.device_path = None
        volume.delete_attachment(server_id)
        if volume._current_status != 'in-use':
            raise Exception("Invalid volume status: "
                            "expected 'in-use' but was '%s'" %
                            volume._current_status)

        volume._current_status = "available"

    def create_server_volume(self, server_id, volume_id, device_path):
        volume = self.get(volume_id)
        volume.device_path = device_path
        volume.set_attachment(server_id)
        if volume._current_status != "available":
            raise Exception("Invalid volume status: "
                            "expected 'available' but was '%s'" %
                            volume._current_status)

        volume._current_status = "in-use"


def fake_create_nova_client():
    class _fake_nova():
        def __init__(self):
            self.servers = Nova()

    return _fake_nova()


def fake_create_cinder_client():
    class _fake_cinder():
        def __init__(self):
            self.volumes = Cinder()

    return _fake_cinder()
