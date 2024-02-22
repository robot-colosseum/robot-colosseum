# Installation

`Colosseum` depends on both [`PyRep`][3] and [`RLBench`][4] to work correctly.
Please refer to their installation guides for more information. We repeat the
setup steps here for convenience. Notice that both `PyRep` and `RLBench` use
`CoppeliaSim` as simulator (former V-rep). Moreover, they use version `4.1`,
which is an old one, and targets old versions of Ubuntu.

> **Note**: Even though the version of CoppeliaSim targets and old version of
Ubuntu, we have tested it on different OS versions, and in most cases should
work just fine.

## 1.1 CoppeliaSim Setup

Download the appropriate version of CoppeliaSim for your system. Note that if
your system is not supported, then you could try using the latest CoppeliaSim
for Ubuntu20.04 and most likely will work just fine. Once downloaded, unzip its
contents in a place you prefer, we'll need the path to that place later.

| CoppeliaSim v4.1 URL |
| ---------------------|
|  [Ubuntu 16.04][0]   |
|  [Ubuntu 18.04][1]   |
|  [Ubuntu 20.04][2]   |

Once unzipped, export the following environment variables in your `.bashrc` file
as follows. Note that we're enclosing the exports into a function to call from
terminal, as having it directly in the `.bashrc` may cause issues when using
applications that rely on `Qt` (most ROS related stuff will break).

```bash
setup_pyrep() {
    export COPPELIASIM_ROOT=/path/to/CoppeliaSim_Edu_V4_1_0_Ubuntu20_04
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$COPPELIASIM_ROOT
    export QT_QPA_PLATFORM_PLUGIN_PATH=$COPPELIASIM_ROOT
}
```

Remember to **source** your `.bashrc` file to enable the changes, and call the
`setup_pyrep` function when you're ready to use CoppeliaSim and related tools.

## 1.2 Setup `PyRep`

Once you have source your `.bashrc` file, and called the `setup_pyrep` function,
you're ready to install `PyRep`. We recommend using a separate virtual environment
in which we'll install also `RLBench` and other packages. Also, in the following
lines we assume you have a separate folder called `WORKSPACE`, where you'll be
able to download and manage all relatedd packages.

```bash
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

```

[0]: <https://www.coppeliarobotics.com/files/V4_1_0/CoppeliaSim_Edu_V4_1_0_Ubuntu16_04.tar.xz> (coppeliasim-edu-ubuntu16)
[1]: <https://www.coppeliarobotics.com/files/V4_1_0/CoppeliaSim_Edu_V4_1_0_Ubuntu18_04.tar.xz> (coppeliasim-edu-ubuntu18)
[2]: <https://www.coppeliarobotics.com/files/V4_1_0/CoppeliaSim_Edu_V4_1_0_Ubuntu20_04.tar.xz> (coppeliasim-edu-ubuntu20)
[3]: <https://github.com/stepjam/pyrep> (pyrep-gh-repo)
[4]: <https://github.com/stepjam/rlbench> (rlbench-gh-repo)
