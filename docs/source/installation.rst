Installation
============

1. Setup locally
-----------------

``Colosseum`` depends on both `PyRep`_ and `RLBench`_ to work correctly.
Please refer to their installation guides for more information. We repeat the
setup steps here for convenience. Notice that both PyRep and RLBench use
CoppeliaSim as simulator (former V-rep). Moreover, they use version ``4.1``,
which is an old one, and targets old versions of Ubuntu.

.. note:: Even though the version of CoppeliaSim targets an old version of
   Ubuntu, we have tested it on different OS versions and different OSs, and
   in most cases should work just fine.


1.1. CoppeliaSim Setup
++++++++++++++++++++++
Download the appropriate version of CoppeliaSim for your system (note that even
though we don't list the latest version of Ubuntu, this still should work just
fine).

+----------------------+
| CoppeliaSim v4.1 URL |
+======================+
| `Ubuntu 16.04 Link`_ |
+----------------------+
| `Ubuntu 18.04 Link`_ |
+----------------------+
| `Ubuntu 20.04 Link`_ |
+----------------------+

Export the following environment variables in your ``.bashrc`` as follows. Note
that we're enclosing it into a function to call from our terminal, as having it
directly in the ``.bashrc`` file might cause issues with other programs that use
``Qt`` and similar libraries as CoppeliaSim.

.. code-block:: bash

   setup_pyrep(){
      export COPPELIASIM_ROOT=/path/to/CoppeliaSim_Edu_V4_1_0_Ubuntu20_04
      export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$COPPELIASIM_ROOT
      export QT_QPA_PLATFORM_PLUGIN_PATH=$COPPELIASIM_ROOT
   }

Remember to ``source`` and call the ``setup_pyrep`` function when you're about
to use CoppeliaSim and related packages.

1.2. Setup PyRep
++++++++++++++++++

Once you have source your ``.bashrc`` file, and called the ``setup_pyrep``
function, you're ready to install PyRep. We recommend using a separate virtual
environment in which we'll install also ``RLBench`` and other packages. Also, in
the following lines we assume you have a separate folder called ``WORKSPACE``,
where you'll be able to download and manage all relatedd packages.

.. code-block:: bash

   $ cd $WORKSPACE
   # Create a virtual environment
   $ virtualenv venv
   $ . venv/bin/activate
   # Clone the PyRep repository and install the package
   (venv) $ git clone https://github.com/stepjam/PyRep.git pyrep && cd pyrep
   (venv) $ pip install -r requirements.txt
   (venv) $ pip install .
   # Go back to our workspace, and test that PyRep is working correctly
   (venv) $ cd $WORKSPACE
   (venv) $ setup_pyrep # Call this function you added to your .bashrc
   (venv) $ python pyrep/examples/example_youbot_navigation.py

After the setup is complete, you should see the following simulation by using
one of the provided samples in PyRep (``pyrep/examples/example_youbot_navigation.py``)

.. image:: /_static/gif_example_pyrep_working.gif
   :width: 100%
   :align: center


1.3. Setup RLBench
++++++++++++++++++++

Once you have ``PyRep`` installed, we can proceed to install ``RLBench``

.. note:: If you have the `PerAct`_ fork of ``RLBench``, you can still use our repo,
   as we have compatibility with both version.

.. code-block:: bash

   $ cd $WORKSPACE
   $ . venv/bin/activate
   (venv) $ git clone https://github.com/stepjam/RLBench.git rlbench && cd rlbench
   (venv) $ pip install -r requirements.txt
   (venv) $ pip install .
   (venv) $ cd $WORKSPACE
   (venv) $ setup_pyrep # Call this function you added to your .bashrc
   (venv) $ python rlbench/examples/imitation_learning.py

After the setup is complete, you should see the following simulation by using
one of the provided samples in RLBench (``rlbench/examples/imitation_learning.py``)

.. image:: /_static/gif_example_rlbench_working.gif
   :width: 100%
   :align: center


1.4. Setup our Repo
+++++++++++++++++++++

Finally, we can download our repo and configure it. Just follow the following
steps and you should be good to go:

.. code-block:: bash

   $ cd $WORKSPACE
   $ . venv/bin/activate
   (venv) $ git clone https://github.com/robot-colosseum/robot-colosseum.git && cd robot-colosseum
   (venv) $ pip install -r requirements.txt
   (venv) $ pip install -e . # Install in developer mode

.. warning:: The current setup we have in our repo only allows to change the
   config files and update them if using developer mode, so for the moment
   please stick to developer mode until we have a fix for the assets managment

Once you're done with the installation, you can check that everything is working
by using the example visualizer:

.. code-block:: bash

   (venv) $ cd $WORKSPACE/robot-colosseum
   (venv) $ python -m colosseum.tools.visualize_task --config-name hockey

.. image:: /_static/gif_example_own_repo_working.gif
   :width: 100%
   :align: center


2. Setup using Docker
------------------------

We provide a set of ``Dockerfiles`` that can be used to build images that have
everything ready for collecting demos.

* ``Dockerfile_mesa``: Used for collecting demonstrations in headless mode, but
  without hardware acceleration. PyRep will default to use software rendering
  for this case. Build an image out of this file as follows:

.. code-block:: bash

   $ cd $WORKSPACE/robot-colosseum
   $ docker build -t colosseum:mesa -f Dockerfile_mesa .


Spawn a container using this image for data collection as follows:

.. code-block:: bash

   $ docker run -e DISPLAY -v $HOME/.Xauthority:/home/randuser/.Xauthority \
     --net=host -it --rm colosseum:mesa bash


Once the container is running, refer to the quickstart section for info on how
to collect data and visualize tasks.

* ``Dockerfile_nvidia``: Used for collecting demonstrations in headless mode,
  but with hardware acceleration. To allow to build using GPU support, you need
  to have the `NVIDIA Container Toolkit`_ PyRep will default to use hardware rendering
  for this case. Build an image out of this file as follows:

.. code-block:: bash

   $ cd $WORKSPACE/robot-colosseum
   $ docker build -t colosseum:nvidia -f Dockerfile_nvidia .

Spawn a container using this image for data collection as follows:

.. code-block:: bash

   docker run --runtime=nvidia --gpus all -e DISPLAY -it --rm \
     -v $HOME/.Xauthority:/home/randuser/.Xauthority \
     -v /tmp/.X11-unix:/tmp/.X11-unix --net=host colosseum:nvidia bash


.. _PyRep: https://github.com/stepjam/PyRep
.. _RLBench: https://github.com/stepjam/RLBench
.. _RLBench fork: https://github.com/MohitShridhar/RLBench/tree/peract
.. _Ubuntu 16.04 Link: https://downloads.coppeliarobotics.com/V4_1_0/CoppeliaSim_Edu_V4_1_0_Ubuntu16_04.tar.xz
.. _Ubuntu 18.04 Link: https://downloads.coppeliarobotics.com/V4_1_0/CoppeliaSim_Edu_V4_1_0_Ubuntu18_04.tar.xz
.. _Ubuntu 20.04 Link: https://downloads.coppeliarobotics.com/V4_1_0/CoppeliaSim_Edu_V4_1_0_Ubuntu20_04.tar.xz
.. _PerAct: https://github.com/peract/peract
.. _NVIDIA Container Toolkit: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
