__author__ = 'denis_makogon'

from proboscis import test


GROUP_VOLUMES = 'gigaspace.cinder.volumes.api'

@test(group=[GROUP_VOLUMES])
class TestCinderVolumesWorkflow(object):
    pass
