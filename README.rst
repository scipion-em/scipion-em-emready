==============
EMReady plugin
==============

`EMReady <http://huanglab.phys.hust.edu.cn/EMReady/>`_: Improvement of cryo-EM maps by simultaneous local and non-local deep learning.

.. image:: https://img.shields.io/pypi/v/scipion-em-emready.svg
        :target: https://pypi.python.org/pypi/scipion-em-emready
        :alt: PyPI release

.. image:: https://img.shields.io/pypi/l/scipion-em-emready.svg
        :target: https://pypi.python.org/pypi/scipion-em-emready
        :alt: License

.. image:: https://img.shields.io/pypi/pyversions/scipion-em-emready.svg
        :target: https://pypi.python.org/pypi/scipion-em-emready
        :alt: Supported Python versions

.. image:: https://img.shields.io/sonar/quality_gate/scipion-em_scipion-em-emready?server=https%3A%2F%2Fsonarcloud.io
        :target: https://sonarcloud.io/dashboard?id=scipion-em_scipion-em-emready
        :alt: SonarCloud quality gate

.. image:: https://img.shields.io/pypi/dm/scipion-em-emready
        :target: https://pypi.python.org/pypi/scipion-em-emready
        :alt: Downloads

Installation
-------------

You will need to use 3.0+ version of Scipion to be able to run these protocols. To install the plugin, you have two options:

a) Stable version

.. code-block::

     scipion installp -p scipion-em-emready

or through the **plugin manager** by launching Scipion and following **Configuration** >> **Plugins**

b) Developer's version

   * download repository

    .. code-block::

        git clone -b devel https://github.com/scipion-em/scipion-em-emready.git

   * install

    .. code-block::

       scipion installp -p /path/to/scipion-em-emready --devel

EMReady software will be installed automatically with the plugin but you can also use an existing installation by providing *EMREADY_ENV_ACTIVATION* and *EMREADY_HOME* (see below).

**Important:** you need to have conda (miniconda3 or anaconda3) pre-installed to use this program.

Configuration variables
-----------------------
*CONDA_ACTIVATION_CMD*: If undefined, it will rely on conda command being in the
PATH (not recommended), which can lead to execution problems mixing scipion
python with conda ones. One example of this could can be seen below but
depending on your conda version and shell you will need something different:
CONDA_ACTIVATION_CMD = eval "$(/extra/miniconda3/bin/conda shell.bash hook)"

*EMREADY_ENV_ACTIVATION* (default = conda activate emready-2.0):
Command to activate the EMReady environment.

*EMREADY_HOME* (default = software/em/emready-2.0):
Path with EMReady source code.

Verifying
---------
To check the installation, simply run the following Scipion test:

``scipion test emready.tests.test_protocol_sharpening.TestEMReadySharpening``

Supported versions
------------------

2.0

Protocols
----------

* sharpening

References
-----------

1. He J, Li T, Huang S-Y. Improvement of cryo-EM maps by simultaneous local and non-local deep learning. Nature Communications, 2023; 14:3217.
