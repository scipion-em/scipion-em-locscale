===============
Locscale plugin
===============

This plugin provides a wrapper around `LocScale <https://git.embl.de/jakobi/LocScale>`_ program for local sharpening of cryo-EM density maps.

Installation
------------

You will need to use 3.0+ version of Scipion to be able to run these protocols. To install the plugin, you have two options:

a) Stable version

   .. code-block::

      scipion installp -p scipion-em-locscale

b) Developer's version

   * download repository

   .. code-block::

      git clone https://github.com/scipion-em/scipion-em-locscale.git

   * install

   .. code-block::

      scipion installp -p path_to_scipion-em-locscale --devel

LocScale sources will be downloaded automatically with the plugin,
but you can also link an existing installation.
Default installation path assumed is ``software/em/locscale-0.1``,
if you want to change it, set *LOCSCALE_HOME* in ``scipion.conf``
file to the folder where the LocScale is installed.
LocScale uses EMAN2 libraries, so you need to provide existing EMAN2
installation path by setting *EMAN2_HOME* variable
(default eman-2.99) in the config file.

Note: **mpi4py** will be installed in the Eman's python

.. warning:: File locscale-0.1/source/locscale_mpi.py needs a patch (see locscale_mpi.py.patch) to be able to work with new versions of EMAN.

To check the installation, simply run the following Scipion tests:

.. code-block::

   scipion test locscale.tests.test_protocol_locscale.TestProtLocscale

A complete list of tests can also be seen by executing ``scipion test --show --grep locscale``

Supported versions
------------------

0.1

Protocols
---------

* local sharpening


References
----------

1. Jakobi A. et al., eLife, 2017
