Overview
========

.. figure:: /_static/gif_perturbation_factors.gif
   :width: 100%
   :align: center

   Perturbations applied to various tasks from the benchmark.

Introduction
------------

**Colosseum** is a benchmark that test the generalization capabilities of robot
manipulation policies. It does so in a similar approach to :cite:t:`Xie2023decomposing`
and :cite:t:`Zhu2023learning` by varying environmental factors that can affect
generalization of robot manipulation policies. Our simulated benchmark builds
on top of `RLBench <https://github.com/stepjam/RLBench>`_ (:cite:t:`James2019rlbench`)
by defining 12 perturbation factors that the user can control and collect
demonstrations for training and testing policies under these variations.

Below we list the perturbation factors and give a brief description. Note that
we make use of the following categorization:

- ``Manipulation Object`` (MO) perturbation : MO is a task-relevant object that is
  directly manipulated or interacted with by the robot.

- ``Receiver Object`` (RO) perturbation: RO is a task-relevant object that is not
  directly interacted with by the robot.

- ``Background`` perturbation: Factors that do not relate to task-relevant objects,
  but are background characteristics of the scene.

+-----------------------+--------------------------------------------------------+
| Factor of Variation   | Description                                            |
+=======================+========================================================+
| *MO color*            | Modifies the color of the MO                           |
+-----------------------+--------------------------------------------------------+
| *RO color*            | Modifies the color of the RO (if applicable)           |
+-----------------------+--------------------------------------------------------+
| *MO texture*          | Modifies the texture applied to the MO                 |
+-----------------------+--------------------------------------------------------+
| *RO texture*          | Modifies the texture applied to the RO (if applicable) |
+-----------------------+--------------------------------------------------------+
| *MO size*             | Scales the MO by a given factor                        |
+-----------------------+--------------------------------------------------------+
| *RO size*             | Scales the RO (if applicable) by a given factor        |
+-----------------------+--------------------------------------------------------+
| *Light color*         | Modifies the color of the lights setup in the scene.   |
+-----------------------+--------------------------------------------------------+
| *Table color*         | Modifies the color of the tabletop of the robot setup  |
+-----------------------+--------------------------------------------------------+
| *Table texture*       | Modifies the texture applied to the tabletop of the    |
|                       | robot setup.                                           |
+-----------------------+--------------------------------------------------------+
| *Distractor object*   | Spawns a random object in the workspace of the robot.  |
+-----------------------+--------------------------------------------------------+
| *Background texture*  | Modifies the textures applied to the walls of the      |
|                       | scene.                                                 |
+-----------------------+--------------------------------------------------------+
| *Camera pose*         | Randomly perturbs the pose of a camera.                |
+-----------------------+--------------------------------------------------------+

Perturbations
-------------

1. MO Color
+++++++++++++++

.. figure:: /_static/gif_open_drawer_mo_color_none.gif
   :align: center
   :width: 50%

   Task ``Open Drawer`` with no variations

.. figure:: /_static/gif_open_drawer_mo_color_drawer.gif
   :align: center
   :width: 50%

   Task ``Open Drawer`` with object color variation applied to drawer

2. RO Color
+++++++++++++++

.. figure:: /_static/gif_basketball_ro_color_none.gif
   :align: center
   :width: 50%

   Task ``Basketball In Hoop`` with no variations

.. figure:: /_static/gif_basketball_ro_color_hoop.gif
   :align: center
   :width: 50%

   Task ``Basketball In Hoop`` with object color variation applied to hoop


3. MO Texture
+++++++++++++++++

.. figure:: /_static/gif_basketball_mo_texture_none.gif
   :align: center
   :width: 50%

   Task ``Basketball In Hoop`` with no variations

.. figure:: /_static/gif_basketball_mo_texture_ball.gif
   :align: center
   :width: 50%

   Task ``Basketball In Hoop`` with object texture variation applied to ball

4. RO Texture
+++++++++++++++++

.. figure:: /_static/gif_place_wine_ro_texture_none.gif
   :align: center
   :width: 50%

   Task ``Basketball In Hoop`` with no variations

.. figure:: /_static/gif_place_wine_ro_texture_rack.gif
   :align: center
   :width: 50%

   Task ``Basketball In Hoop`` with object texture variation applied to ball

5. MO Size
++++++++++++++

.. figure:: /_static/gif_close_box_mo_size_none.gif
   :align: center
   :width: 50%

   Task ``Close Box`` with no variations

.. figure:: /_static/gif_close_box_mo_size_box.gif
   :align: center
   :width: 50%

   Task ``Close Box`` with object size variation applied to the box

6. RO Size
++++++++++++++

.. figure:: /_static/gif_hockey_ro_size_none.gif
   :align: center
   :width: 50%

   Task ``Hokey`` with no variations

.. figure:: /_static/gif_hockey_ro_size_ball.gif
   :align: center
   :width: 50%

   Task ``Hockey`` with object size variation applied to the ball

7. Light Color
++++++++++++++

.. figure:: /_static/gif_reach_and_drag_light_color_none.gif
   :align: center
   :width: 50%

   Task ``Reach and Drag`` with no variations

.. figure:: /_static/gif_reach_and_drag_light_color_default.gif
   :align: center
   :width: 50%

   Task ``Reach and Drag`` with light color variation applied

8. Table Color
++++++++++++++

.. figure:: /_static/gif_hockey_table_color_none.gif
   :align: center
   :width: 50%

   Task ``Hockey`` with no variations

.. figure:: /_static/gif_hockey_table_color_default.gif
   :align: center
   :width: 50%

   Task ``Hockey`` with table color variation applied to the tabletop


9. Table Texture
++++++++++++++++

.. figure:: /_static/gif_meat_and_grill_table_texture_none.gif
   :align: center
   :width: 50%

   Task ``Meat On Grill`` with no variations

.. figure:: /_static/gif_meat_and_grill_table_texture_default.gif
   :align: center
   :width: 50%

   Task ``Meat On Grill`` with table texture variation applied to the tabletop


10. Distractor Object
+++++++++++++++++++++++

.. figure:: /_static/gif_insert_peg_distractors_none.gif
   :align: center
   :width: 50%

   Task ``Insert onto square peg`` with no variations

.. figure:: /_static/gif_insert_peg_distractors_default.gif
   :align: center
   :width: 50%

   Task ``Insert onto square peg`` with distractor object variation being applied

11. Background Texture
+++++++++++++++++++++++++

.. figure:: /_static/gif_basketball_background_texture_none.gif
   :align: center
   :width: 50%

   Task ``Basketball In Hoop`` with no variations

.. figure:: /_static/gif_basketball_background_texture_default.gif
   :align: center
   :width: 50%

   Task ``Basketball In Hoop`` with background texture variation being applied

12. Camera Pose
+++++++++++++++++++++

.. figure:: /_static/gif_setup_chess_camera_pose_none.gif
   :align: center
   :width: 50%

   Task ``Setup Chess`` with no variations

.. figure:: /_static/gif_setup_chess_camera_pose_default.gif
   :align: center
   :width: 50%

   Task ``Setup Chess`` with camera pose variation being applied

.. bibliography::
