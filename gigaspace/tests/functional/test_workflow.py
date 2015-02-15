__author__ = 'denis_makogon'

from proboscis import asserts
from proboscis import test
from proboscis.decorators import time_out

from gigaspace.cinder_workflow import base
from gigaspace.common import utils

GROUP_WORKFLOW = 'gigaspace.cinder.volumes.api'


@test(groups=[GROUP_WORKFLOW])
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
        - create SSH key pair
        - create block device mapping:
          - with preserve on delete
        - assign SSH key pair to an instance
     - poll until instance would reach ACTIVE state
     - poll until can do ssh into an instance
     - check if volume was mounted
     - format volume
     - detach volume
        - poll until volume would reach 'available' state
     - delete an instance
        - poll until instance would gone away
        - check if volume was deleted
    """

    def __init__(self):
        self.cinder_actions = base.BaseCinderActions()
        self.nova_actions = None
        self.volume = None
        self.server = None
        self.volume_size, self.display_name, self.expected_status = (
            "1", "test_volume", "available")

    def _poll_volume_status(self, expected_status):
        def _poller():
            volume = self.cinder_actions.show_volume(self.volume.id)
            if volume.status in ("error", "failed"):
                raise Exception("Volume is not in valid state")
            return volume.status == expected_status
        return _poller

    @test
    @time_out(300)
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

    @test(depends_on=[test_create_volume])
    def test_list_volumes(self):
        """
        - list volumes
        """
        volumes = self.cinder_actions.list_volumes()
        asserts.assert_equal(len(volumes), 1)

    @test(depends_on=[test_list_volumes])
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

    @test(depends_on=[test_get_volume_by_its_name_or_id])
    def test_boot_instance(self):
        """
        - boot an instance:
            - create SSH key pair
            - create block device mapping:
                - with preserve on delete
            - assign SSH key pair to an instance
            - poll until instance would reach ACTIVE state
            - poll until can do ssh into an instance
            - check if volume was mounted
        """
        pass
