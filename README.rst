# gigaspace-test-task

===============
Learing process
===============

Background
----------

Most knowledge was earned during previous experience with OpenStack services::
    - Trove
    - Heat
    - Sahara
    - Cinder
    - Nova
    - Horizon


Nova API
--------

Learing by source code
https://gitgub.com/openstack/python-novaclient

Cinder API
----------

Learing by source code
https://github.com/openstack/python-cinderclient


Workflow
--------

Learning by source code
https://github.com/openstack-dev/devstack

OpenStack API consumption
-------------------------

http://www.ibm.com/developerworks/cloud/library/cl-openstack-pythonapis/

==============
Test execution
==============

NOTE. This code works with fake-mode OpenStack and with DevStack.

Fake-moe tests
--------------

NOTE. Fake mode tests would use etc/gigaspace/gigaspace.test.conf config file for execution.

Real-mode tests
---------------

NOTE. Fake mode tests would use etc/gigaspace/gigaspace.conf config file for execution.
      So, please consider to change credentials before launching real-mode tests.

Tests
-----

NOTE. Starting Ubuntu Trusty Tahr 14.04 LTS and CentOS 7 there's no python2.6 executable.

Once you clone this repo, you need to do next:

.. code-block:: bash

    $ virtualenv .venv
    $ source .venv/bin/active
    $ tox -evenv -- python setup.py install
    $ tox -epep8    # PEP8(flake8) checks
    $ tox -efake    # Fake-mode tests
    $ tox -ereal    # Real-mode tests
