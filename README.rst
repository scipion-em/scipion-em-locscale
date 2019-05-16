===============
LOCSCALE PLUGIN
===============

This sub-package contains data and protocol classes to use Locscale within the Scipion framework.  The package implements a general procedure for local sharpening of cryo-EM density maps based on prior knowledge of an atomic reference structure. The procedure optimizes contrast of cryo-EM densities by amplitude scaling against the radially averaged local falloff estimated from a windowed reference model.


=====
Setup
=====

- **Install this plugin:**

.. code-block::

    scipion installp -p scipion-em-locscale

OR

  - through the plugin manager GUI by launching Scipion and following **Configuration** >> **Plugins**

Alternatively, in devel mode:

.. code-block::

    scipion installp -p local/path/to/scipion-em-locscale --devel
