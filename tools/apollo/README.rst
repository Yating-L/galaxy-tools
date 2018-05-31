Galaxy-apollo
=============

Galaxy tools to interface with Apollo. The webapollo.py file is also
`separately
available <https://github.com/galaxy-genome-annotation/python-apollo>`__
as a pip-installable package.

Create or Update Organism
-------------------------
Adds an organism to the Apollo database. The tool takes the output of a
JBrowse run as that contains all of the necessary information for which
tracks are appropriate for a given analysis.

Apollo User Manager
-------------------

This Galaxy tool is used to manage Apollo users.The currently supported operation including:

  - Create a new user
  - Delete a user
  - Create a group
  - Delete a group
  - Add a user to a group
  - Remove a user from a group

The tool can do these operations on one user/group at a time. It can also do the operations on multiple users/groups at a time by uploading a text file, which including users/groups information.

The text file can be either CSV (comma-delimited) or Tabular (tab-delimited). It should have a header line, including names for each column. Example text files:

Text file for creating multiple users/groups:

.. csv-table::
   :header: "useremail", "firstname", "lastname", "role"
   :widths: 20, 10, 10, 10

   "test1@demo.com", "test1", "demo", "user"
   "test2@demo.com", "test2", "demo", "user"
   "test3@demo.com", "test3", "demo", "user"

Text file for deleting multiple users:

.. csv-table::
    :header: "useremail"
    :widths: 20

    "test1@demo.com"
    "test2@demo.com"
    "test3@demo.com"


Text file for creating multiple user groups:

.. csv-table::
    :header: "group"
    :widths: 20

    "annotation_group_1"
    "annotation_group_2"
    "annotation_group_3"


Text file for deleting multiple user groups:

.. csv-table::
    :header: "group"
    :widths: 20

    "annotation_group_1"
    "annotation_group_2"
    "annotation_group_3"


Text file for adding / removing multiple users from a group:

.. csv-table::
   :header: "useremail", "group"
   :widths: 20, 20

   "test1@demo.com", "annotation_group1"
   "test2@demo.com", "annotation_group1"
   "test3@demo.com", "annotation_group1"

Delete an Apollo record
-----------------------

Deletes organism from Apollo and export every single one of the annotations on the organism.

Dependencies
------------

You will need to install some python modules in the Galaxy virtualenv for these
tools to be fully functional:

.. code:: bash

    . /path/to/galaxy/.venv/bin/activate
    pip install future biopython bcbio-gff
    deactivate

Environment
-----------

The following environment variables must be set:

+--------------------------------+-----------------------------------------------------------+
| ENV                            | Use                                                       |
+================================+===========================================================+
| ``$GALAXY_WEBAPOLLO_URL``      | The URL at which Apollo is accessible, internal to Galaxy |
|                                | and where the tools run. Must be absolute, with FQDN and  |
|                                | protocol.                                                 |
+--------------------------------+-----------------------------------------------------------+
| ``$GALAXY_WEBAPOLLO_USER``     | The admin user which Galaxy should use to talk to Apollo. |
|                                |                                                           |
+--------------------------------+-----------------------------------------------------------+
| ``$GALAXY_WEBAPOLLO_PASSWORD`` | The password for the admin user.                          |
|                                |                                                           |
|                                |                                                           |
+--------------------------------+-----------------------------------------------------------+
| ``$GALAXY_WEBAPOLLO_EXT_URL``  | May be relative or absolute.                              |
|                                | The external URL at which Apollo is accessible to end     |
|                                | users.                                                    |
+--------------------------------+-----------------------------------------------------------+
| ``$GALAXY_SHARED_DIR``         | Directory shared between Galaxy and Apollo, used to       |
|                                | exchange JBrowse instances.                               |
+--------------------------------+-----------------------------------------------------------+

License
-------

All python scripts, wrappers, and the webapollo.py are licensed under
MIT license.
