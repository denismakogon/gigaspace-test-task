__author__ = 'denis_makogon'

import eventlet


class Nova(object):
    pass


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

    def schedule_status(self, new_status, time_from_now):
        """Makes a new status take effect at the given time."""
        def set_status():
            self._current_status = new_status
        eventlet.spawn_after(time_from_now, set_status)

    def set_attachment(self, server_id):
        """Fake method we've added to set attachments. Idempotent."""
        for attachment in self.attachments:
            if attachment['server_id'] == server_id:
                return  # Do nothing
        self.attachments.append({'server_id': server_id,
                                 'device': self.device})

    @property
    def status(self):
        return self._current_status


FAKE_VOLUMES_DB = {}


class Cinder(object):

    def __init__(self):
        self.db = FAKE_VOLUMES_DB

    def get(self, id):
        return self.db[id]

    def create(self, size, display_name=None, description=None, volume_type=None):
        import uuid
        id = "FAKE_VOL_%s" % uuid.uuid4()
        volume = FakeVolume(id, size, display_name,
                            description, volume_type)
        self.db[id] = volume
        volume.schedule_status("available", 2)
        return volume

    def list(self, detailed=True):
        return [self.db[key] for key in self.db]

    def extend(self, volume_id, new_size):
        volume = self.get(volume_id)

        if volume._current_status != 'available':
            raise Exception("Invalid volume status: "
                            "expected 'in-use' but was '%s'" %
                            volume._current_status)

        def finish_resize():
            volume.size = new_size
        eventlet.spawn_after(1.0, finish_resize)

    def delete_server_volume(self, server_id, volume_id):
        volume = self.get(volume_id)

        if volume._current_status != 'in-use':
            raise Exception("Invalid volume status: "
                            "expected 'in-use' but was '%s'" %
                            volume._current_status)

        def finish_detach():
            volume._current_status = "available"
        eventlet.spawn_after(1.0, finish_detach)

    def create_server_volume(self, server_id, volume_id, device_path):
        volume = self.get(volume_id)

        if volume._current_status != "available":
            raise Exception("Invalid volume status: "
                            "expected 'available' but was '%s'" %
                            volume._current_status)

        def finish_attach():
            volume._current_status = "in-use"
        eventlet.spawn_after(1.0, finish_attach)


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
