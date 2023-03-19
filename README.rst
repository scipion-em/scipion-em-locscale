===============
Locscale plugin
===============

This plugin provides a wrapper around `LocScale <https://gitlab.tudelft.nl/aj-lab/locscale>`_ program for local sharpening of cryo-EM density maps.

.. image:: https://img.shields.io/pypi/v/scipion-em-locscale.svg
        :target: https://pypi.python.org/pypi/scipion-em-locscale
        :alt: PyPI release

.. image:: https://img.shields.io/pypi/l/scipion-em-locscale.svg
        :target: https://pypi.python.org/pypi/scipion-em-locscale
        :alt: License

.. image:: https://img.shields.io/pypi/pyversions/scipion-em-locscale.svg
        :target: https://pypi.python.org/pypi/scipion-em-locscale
        :alt: Supported Python versions

.. image:: https://img.shields.io/sonar/quality_gate/scipion-em_scipion-em-locscale?server=https%3A%2F%2Fsonarcloud.io
        :target: https://sonarcloud.io/dashboard?id=scipion-em_scipion-em-locscale
        :alt: SonarCloud quality gate

.. image:: https://img.shields.io/pypi/dm/scipion-em-locscale
        :target: https://pypi.python.org/pypi/scipion-em-locscale
        :alt: Downloads


Installation
------------

You will need to use 3.0+ version of Scipion to be able to run these protocols. To install the plugin, you have two options:

a) Stable version

   .. code-block::

      scipion installp -p scipion-em-locscale

b) Developer's version

   * download repository

   .. code-block::

      git clone -b devel https://github.com/scipion-em/scipion-em-locscale.git

   * install

   .. code-block::

      scipion installp -p path/to/scipion-em-locscale --devel

LocScale software will be installed automatically with the plugin but you can also use an existing installation by providing *LOCSCALE_ENV_ACTIVATION* (see below).

**Important:** you need to have conda (miniconda3 or anaconda3) pre-installed to use this program.

Configuration variables
-----------------------
*CONDA_ACTIVATION_CMD*: If undefined, it will rely on conda command being in the
PATH (not recommended), which can lead to execution problems mixing scipion
python with conda ones. One example of this could can be seen below but
depending on your conda version and shell you will need something different:
CONDA_ACTIVATION_CMD = eval "$(/extra/miniconda3/bin/conda shell.bash hook)"

*LOCSCALE_ENV_ACTIVATION* (default = conda activate locscale-2.1):
Command to activate the LocScale environment.


Verifying
---------
To check the installation, simply run the following Scipion test:

``scipion test locscale.tests.test_protocol_locscale.TestProtLocscale``

Supported versions
------------------

2.1

Protocols
---------

* local sharpening


References
----------

1. A.J. Jakobi, M. Wilmanns and C. Sachse, Model-based local density sharpening of cryo-EM maps, eLife 6: e27131 (2017).
2. A.Bharadwaj and A.J. Jakobi, Electron scattering properties and their use in cryo-EM map sharpening, Faraday Discussions D2FD00078D (2022)
