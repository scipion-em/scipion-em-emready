=================
EMReady plugin
=================

EMReady: Improvement of cryo-EM maps by simultaneous local and non-local deep learning.

**Installing the plugin**
=========================

In order to install the plugin follow these instructions:

**Install the plugin**

.. code-block::

     scipion installp -p scipion-em-emready

or through the **plugin manager** by launching Scipion and following **Configuration** >> **Plugins**


**To install in development mode**

- Clone or download the plugin repository

.. code-block::

          git clone https://github.com/scipion-em/scipion-em-emready.git

- Install the plugin in developer mode.

.. code-block::

  scipion installp -p local/path/to/scipion-em-emready --devel

===============
Buildbot status
===============

Status devel version:

.. image:: http://scipion-test.cnb.csic.es:9980/badges/emready_devel.svg

Status production version:

.. image:: http://scipion-test.cnb.csic.es:9980/badges/emready_prod.svg

