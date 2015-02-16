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
     - boot an instance:
        - format volume using cloudinit
     - poll until instance would reach ACTIVE state
     - check volume and server attachments
     - delete an instance
        - poll until instance would gone away
        - check if volume was deleted
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

    @proboscis.test
    @decorators.time_out(300)
    def test_create_volume(self):
        """
        - create volume:
          - check while it will reach 'available status'
        """
        self.volume = self.cinder_actions.create_volume(
            self.volume_size, self.display_name)
        utils.poll_until(self._poll_volume_status(self.expected_status),
                         expected_result=True,
                         sleep_time=1)
        asserts.assert_equal(self.volume.size, int(self.volume_size))

        volume = self.cinder_actions.show_volume(self.volume.id)
        asserts.assert_equal(volume.status, self.expected_status)

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

    @decorators.time_out(300)
    @proboscis.test(depends_on=[test_get_volume_by_its_name_or_id])
    def test_boot_instance(self):
        """
        - boot an instance:
            - poll until instance would reach ACTIVE state
            - check attachments
        """
        try:
            self.server = self.nova_actions.boot(self.server_name,
                                                 self.flavor_id,
                                                 self.image_id,
                                                 self.volume.id)
            utils.poll_until(self._poll_until_server_is_active("ACTIVE"),
                             expected_result=True,
                             sleep_time=1)
            server = self.nova_actions.get(self.server.id)
            asserts.assert_equal(server.status, "ACTIVE")
        except Exception as e:
            print(str(e))
            raise proboscis.SkipTest("Failed to spawn an instance.")

    @proboscis.test(depends_on=[test_boot_instance])
    def test_server_and_volume_attachments(self):
        """
        - checks volume and server attachments
        """
        server = self.nova_actions.get(self.server.id)
        server_attachment = getattr(
            server, 'os-extended-volumes:volumes_attached').pop(0)
        volume_id = server_attachment['id']
        volume = self.cinder_actions.show_volume(self.volume.id)
        volume_attachment = volume.attachments.pop(0)
        server_id = volume_attachment['server_id']
        asserts.assert_equal(server.id, server_id)
        asserts.assert_equal(volume.id, volume_id)

    def _poll_until_server_is_gone(self):
        def _pollster():
            try:
                self.nova_actions.delete(self.server.id)
            except Exception:
                print("Instance is gone. Checking if volume still there.")
                return True

        return _pollster

    def _poll_until_volume_is_gone(self):
        def _pollster():
            try:
                self.cinder_actions.cinderclient.volumes.delete(
                    self.server.id)
            except Exception:
                print("Instance is gone. Checking if volume still there.")
                return True
        return _pollster

    @decorators.time_out(100)
    @proboscis.test(depends_on=[test_server_and_volume_attachments])
    def test_delete_instance(self):
        """
        - delete instance
        """
        utils.poll_until(self._poll_until_server_is_gone(),
                         expected_result=True,
                         sleep_time=1)
        utils.poll_until(self._poll_until_volume_is_gone(),
                         expected_result=True,
                         sleep_time=1)
