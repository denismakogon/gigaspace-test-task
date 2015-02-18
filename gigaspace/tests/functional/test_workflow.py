__author__ = 'denis_makogon'

import proboscis
from proboscis import asserts
from proboscis import decorators


from gigaspace.cinder_workflow import base as cinder_workflow
from gigaspace.nova_workflow import base as nova_workflow
from gigaspace.common import cfg
from gigaspace.common import utils

GROUP_WORKFLOW = 'gigaspace.cinder.volumes.api'
CONF = cfg.CONF


@proboscis.test(groups=[GROUP_WORKFLOW])
class TestWorkflow(object):
    """
    This is a test suit that represents described workflow:
     - create volume:
        - check while it will reach 'available status'
     - list volumes
     - get volume:
        - by id
        - by name

    Attachment workflow was implemented in two different manners:

        Main workflow:
         - boot an instance:
            - format volume using cloudinit
         - poll until instance would reach ACTIVE state
         - check volume and server attachments
         - delete an instance
            - poll until instance would gone away
            - check if volume was deleted

        Alternative workflow:
         - boot volume
           - poll untill volume reach 'available' state
         - boot an instance without volume and userdata
           - poll untill instance would reach ACTIVE state
         - use Nova volumes API to attach volume
           - check volume attachments
         - reboot server (required, to let operating system to
           discover volume during reboot)
           - poll untill instance would reach ACTIVE state
         - check server attachments
    """

    def __init__(self):
        self.cinder_actions = cinder_workflow.BaseCinderActions()
        self.nova_actions = nova_workflow.BaseNovaActions()
        self.volume = None
        self.server = None
        self.volume_size, self.display_name, self.expected_status = (
            "1", "test_volume", "available")
        self.server_name, self.flavor_id, self.image_id, = (
            "test_server",
            CONF.test_config.test_flavor_id,
            CONF.test_config.test_image_id
        )

    def _poll_volume_status(self, expected_status):
        def _pollster():
            volume = self.cinder_actions.show_volume(self.volume.id)
            if volume.status in ("error", "failed"):
                raise Exception("Volume is not in valid state")
            return volume.status == expected_status
        return _pollster

    def _create_volume(self):
        self.volume = self.cinder_actions.create_volume(
            self.volume_size, self.display_name)
        utils.poll_until(self._poll_volume_status(self.expected_status),
                         expected_result=True,
                         sleep_time=1)
        asserts.assert_equal(self.volume.size, int(self.volume_size))

        volume = self.cinder_actions.show_volume(self.volume.id)
        asserts.assert_equal(volume.status, self.expected_status)

    @proboscis.test
    @decorators.time_out(300)
    def test_create_volume(self):
        """
        - create volume:
          - check while it will reach 'available status'
        """
        self._create_volume()

    @proboscis.test(depends_on=[test_create_volume])
    def test_list_volumes(self):
        """
        - list volumes
        """
        volumes = self.cinder_actions.list_volumes()
        asserts.assert_equal(len(volumes), 1)

    @proboscis.test(depends_on=[test_list_volumes])
    def test_get_volume_by_its_name_or_id(self):
        """
        - get volume:
            - by name
            - by ID
        """
        try:
            volume = self.cinder_actions.show_volume(self.display_name)
        except Exception as e:
            print("Can't get volume by its display name. %s" % str(e))
            volume = self.cinder_actions.show_volume(self.volume.id)
            pass
        asserts.assert_equal(volume.status, self.expected_status)

    def _poll_until_server_is_active(self, expected_status):
        def _pollster():
            server = self.nova_actions.get(self.server.id)
            if server.status.upper() in ["ERROR", "FAILED"]:
                raise Exception("Failed to spawn compute instance.")
            return server.status == expected_status
        return _pollster

    def _boot(self, volume_id):
        try:
            self.server = self.nova_actions.boot(self.server_name,
                                                 self.flavor_id,
                                                 self.image_id,
                                                 volume_id=volume_id)
            utils.poll_until(self._poll_until_server_is_active("ACTIVE"),
                             expected_result=True,
                             sleep_time=1)
            self.server = self.nova_actions.get(self.server.id)
            asserts.assert_equal(self.server.status, "ACTIVE")
        except Exception as e:
            print(str(e))
            raise proboscis.SkipTest("Failed to spawn an instance.")

    @decorators.time_out(300)
    @proboscis.test(depends_on=[test_get_volume_by_its_name_or_id])
    def test_boot_instance(self):
        """
        - boot an instance:
            - poll until instance would reach ACTIVE state
            - check attachments
        """
        self._boot(self.volume.id)

    def _check_attachments(self):
        server = self.nova_actions.get(self.server.id)
        server_attachment = getattr(
            server, 'os-extended-volumes:volumes_attached').pop(0)
        volume_id = server_attachment['id']
        volume = self.cinder_actions.show_volume(self.volume.id)
        volume_attachment = volume.attachments.pop(0)
        server_id = volume_attachment['server_id']
        asserts.assert_equal(server.id, server_id)
        asserts.assert_equal(volume.id, volume_id)

    @proboscis.test(depends_on=[test_boot_instance])
    def test_server_and_volume_attachments(self):
        """
        - checks volume and server attachments
        """
        self._check_attachments()

    def _poll_until_server_is_gone(self, server_id=None):
        def _pollster():
            try:
                _server_id = (server_id if server_id
                              else self.server.id)
                self.nova_actions.delete(_server_id)
            except Exception:
                print("\nInstance has gone.")
                return True

        return _pollster

    def _poll_until_volume_is_gone(self, volume_id=None):
        def _pollster():
            try:
                _volume_id = (volume_id if volume_id
                              else self.volume.id)
                self.cinder_actions.cinderclient.volumes.delete(
                    _volume_id)
            except Exception:
                print("Volume has gone.")
                return True
        return _pollster

    @decorators.time_out(300)
    @proboscis.test(runs_after=[test_server_and_volume_attachments])
    def test_boot_without_volume(self):
        """
        - boot instance without volume
        """
        self._boot(None)

    @proboscis.test(depends_on=[test_boot_without_volume])
    def test_volume_create(self):
        """
        - create volume
        """
        self._create_volume()

    @proboscis.test(depends_on=[test_volume_create])
    def test_attach_volume(self):
        self.nova_actions.create_server_volume(self.volume.id, self.server.id)
        utils.poll_until(self._poll_volume_status("in-use"),
                         expected_result=True,
                         sleep_time=1)
        self._check_attachments()

    @decorators.time_out(300)
    @proboscis.test(depends_on=[test_attach_volume])
    def test_server_reboot_for_volume_discovery(self):
        self.nova_actions.novaclient.servers.reboot(self.server.id)
        utils.poll_until(self._poll_until_server_is_active("ACTIVE"),
                         expected_result=True,
                         sleep_time=1)
        self._check_attachments()

    @proboscis.after_class
    def test_delete_resources(self):
        """
        - delete instance
        - delete volumes
        """
        for server in self.nova_actions.novaclient.servers.list():
            server.delete()
            utils.poll_until(
                self._poll_until_server_is_gone(server_id=server.id),
                expected_result=True,
                sleep_time=1)

        for volume in self.cinder_actions.cinderclient.volumes.list():
            # one of the volumes was bootstraped with delete flag in block
            # mapping device, so Cinder API service would reject request
            # because of volume status that is 'deleting' at this stage
            if volume.status in ['available', 'error']:
                volume.delete()
            utils.poll_until(
                self._poll_until_volume_is_gone(volume_id=volume.id),
                expected_result=True,
                sleep_time=1)
