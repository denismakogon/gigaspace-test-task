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

=======================
Workflow implementation
=======================

This code is represented by a test suit that represents described workflow::

 - create volume

    - check while it will reach 'available status'
 - list volumes
 - get volume

    - by id
    - by name

Attachment workflow was implemented in two different manners::

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
    $ tox # Will run all tests: flake8, fake-mode, real-mode
    $ tox -evenv -- python setup.py install
    $ tox -epep8    # PEP8(flake8) checks
    $ tox -efake    # Fake-mode tests
    $ tox -ereal    # Real-mode tests


=================
CLI usage section
=================

This installed project provides an ability to use two types of CLI tools::

    - gigaspace-tool - allows to access next API:

        instances
            - attach_volume
            - boot_with_volume
            - boot_without_volume
            - delete
            - detach_volume

        volumes
            - create
            - list
            - show

    - gigaspace-tool-tester - allows to access next API for testing:

        run
            - functional


Please note that --config-file option is required for both tools. Please take a look at syntax:

.. code-block:: bash

    $ gigaspace-tool-tester --config-file=etc/gigaspace/gigaspace.test.conf {category} command --{options}
    $ gigaspace-tool --config-file=etc/gigaspace/gigaspace.conf {category} command --{options}


