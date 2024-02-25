Quickstart
==========

Once you're done setting up ``PyRep``, ``RLBench``, and ``Colosseum``, you can
start interacting with the benchmark via various scripts we provide. Note that
you have to activate your virtual environment, and call ``setup_pyrep`` when
starting from a new terminal. Also, make sure you have setup ``Colosseum`` in
developer mode by using ``pip install -e .`` with the ``-e`` option.

1. Visualize and use variations
--------------------------------
We'll start by showing how to visualize demonstrations for a task and how to
enable and tweak variations using config files.

1.1 Visualizing a task
++++++++++++++++++++++
Our first step will be to visualize one of the tasks from the benchmark. Let's
say we what to visualize some demonstrations of the expert policy for the task
``close_box``. We can make use of the ``visualize_task`` script to do so, as
follows:

.. code-block:: bash

   python -m colosseum.tools.visualize_task --config-name close_box

The script is also exposed as a console script in the ``setup.py`` file, so you
can also call it directly like this:

.. code-block:: bash

   visualize_task --config-name close_box

``CoppeliaSim`` should open up and start collecting some demonstrations from the
requested task.

.. figure:: /_static/gif_visualize_task_default.gif
   :width: 50%
   :align: center

   Visualizing the task ``close_box``.

1.2 Enabling variations
++++++++++++++++++++++++

Associated with each task there are 4 files, which we explain below for the
task ``close_box``:

.. figure:: /_static/img_task_related_files.png
   :width: 50%
   :align: center

   The four types of files associated with every task in ``Colosseum``


- ``close_box.ttm``: This is the ``CoppeliaSim`` model representing the task itself.
  It contains all the objects and waypoints required for the task to be executed.
  Note that for RLBench tasks, this is one of the files provided as part of the
  task itself. You usually don't have to change this file if you just want to use
  the task and take demonstrations from it.

- ``close_box.py``: This is the other resource used by RLBench to represent a
  given task. It contains the wiring of objects, sensors, and conditiions for
  the task to be successfull.

- ``close_box.yaml``: This file is related to ``Colosseum``, and it's used to
  configure variations for the associated task. We'll show the ``env`` section
  of the ``yaml`` file to discuss how we can enable and use these variations.

.. code-block:: yaml

   env:
     task_name: "close_box"
     seed: 42
     scene:
       factors:
         - variation: object_color
           name: manip_obj_color
           enabled: False
           targets: [box_base, box_lid]
           seed: ${env.seed}

         - variation: object_texture
           name: manip_obj_tex
           enabled: False
           targets: [box_base, box_lid]
           seed: ${env.seed}

         - variation: object_size
           name: manip_obj_size
           enabled: False
           targets: [box_base]
           scale_range: [0.75, 1.15]
           seed: ${env.seed}

         - variation: light_color
           enabled: False
           targets: [DefaultLightA, DefaultLightB, DefaultLightD]
           color_range: [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]]
           seed: ${env.seed}

         - variation: table_texture
           enabled: False
           seed: ${env.seed}

         - variation: table_color
           enabled: False
           color_range: [[0.25, 0.25, 0.25], [1.0, 1.0, 1.0]]
           seed: ${env.seed}

         - variation: background_texture
           enabled: False
           seed: ${env.seed}

         - variation: distractor_object
           enabled: False
           targets: [spawn_boundary0]
           num_objects: 2
           seed: ${env.seed}

         - variation: camera_pose
           enabled: False
           targets: [cam_front,
                    cam_over_shoulder_left,
                    cam_over_shoulder_right]
           euler_range: [[-0.05, -0.05, -0.05], [0.05, 0.05, 0.05]]
           position_range: [[-0.1, -0.1, -0.1], [0.1, 0.1, 0.1]]
           seed: ${env.seed}

Notice the list in ``yaml`` that we have, consisting of the various variations
that are defined for this task. Notice also that all are disabled, because of
``enabled: False``. Let's activate one of these and vary its parameters; for that
we'll choose the ``MO_Color`` corresponding to the following section in the yaml
file:

.. code-block:: yaml

   - variation: object_color
     name: manip_obj_color
     enabled: True
     targets: [box_base, box_lid]
     seed: ${env.seed}

We have enabled that variation, so if we visuaslize the task again we should see
the effect of this variation in action, as shown in the figure below:

.. figure:: /_static/gif_example_variation_enabled.gif
   :width: 40%
   :align: center

   Visualizing the task ``close_box`` with the variation ``MO_Color`` enabled.

For this variation we can notice that there are 5 arguments we have to provide
in the corresponding ``yaml`` file, as an element of a ``yaml`` list, which are:

- ``variation``: The type of variation to be used, in this case ``object_color``.
- ``name``: An optional argument to identify this variation from others.
- ``enabled``: Whether or not the variation is enabled by default.
- ``targets``: A list of shapes that this variation will handle. We have to check
  the ``.ttm`` file using the ``task_builder`` to look for the names of the objects
  we want our variations to handle.
- ``seed``: The seed to be used for the random number generator.

.. note:: These arguments are not the only ones. Each variation has a different
   set of arguments that allow to configure it according to our needs. We'll see
   more of these in the ``API Reference``.

Let's change the set of colors that we can sample from and select only red, green
and blue colors. For this, we can update that section of the ``yaml`` file to the
following. Also, let's make sure that both objects handled by the variation are
the same color:

.. code-block:: yaml

   - variation: object_color
     name: manip_obj_color
     enabled: True
     targets: [box_base, box_lid]
     seed: ${env.seed}
     color_names: [red, green, blue]
     color_same: True

The resulting demonstrations are shown below. Notice that for the red case the
motion planner failed at the task, and continued with another episode.

.. figure:: /_static/gif_example_variation_tweak.gif
   :width: 40%
   :align: center

   Visualizing the task ``close_box`` with the variation ``MO_Color`` enabled and
   with some modifications.
