<p align="center">
    <h1 align="center">
        <img src="resources/media/img_emoji_rss.png" width="50px"/>
        Colosseum
    </h1>
    <h2 align="center">
        <a href="https://arxiv.org/abs/2402.08191">
        A Benchmark for Evaluating Generalization for Robotic Manipulation
        </a>
    </h2>
</p>

[Wilbert Pumacay<sup>*</sup>][2], [Ishika Singh<sup>*</sup>][3], [Jiafei Duan<sup>*</sup>][4], [Ranjay Krishna][5], [Jesse Thomason][6], [Dieter Fox][7]

<p align="center">
    <img src="resources/media/gif_perturbation_factors.gif"/>
</p>

Colosseum is a robotic manipulation benchmark built on top of [PyRep][0], which
implements 20 out of the original 100 tasks from [RLBench][1], and extends it by
supporting 14 variation factors that randomize parts of the simulation.

## Documentation

- Overview: [Overview][8]
- Getting started: [Installation][9], [Quickstart][10]
- Data Generation: [Data Generation][11]
- RVT baseline: [RVT baseline repo][12]

## Citation

```bibtex
@inproceedings{pumacay2024colosseum,
  title     = {THE COLOSSEUM: A Benchmark for Evaluating Generalization for Robotic Manipulation},
  author    = {Pumacay, Wilbert and Singh, Ishika and Duan, Jiafei and Krishna, Ranjay and Thomason, Jesse and Fox, Dieter},
  booktitle = {Robotics: Science and Systems (RSS)},
  year      = {2024},
}
```


[0]: <https://github.com/stepjam/PyRep> (pyrep-gh-repo)
[1]: <https://github.com/stepjam/RLBench> (rlbench-gh-repo)
[2]: <https://wpumacay.github.io> (wilbert-site)
[3]: <https://ishikasingh.github.io> (ishika-site)
[4]: <https://duanjiafei.com> (jiafei-site)
[5]: <https://ranjaykrishna.com/index.html> (ranjay-site)
[6]: <https://jessethomason.com> (jesse-site)
[7]: <https://homes.cs.washington.edu/~fox> (dieter-site)
[8]: <https://robot-colosseum.readthedocs.io/en/latest/overview.html> (docs-site)
[9]: <https://robot-colosseum.readthedocs.io/en/latest/installation.html> (docs-installation)
[10]: <https://robot-colosseum.readthedocs.io/en/latest/quickstart.html> (docs-quickstart)
[11]: <https://robot-colosseum.readthedocs.io/en/latest/quickstart.html#collect-demonstrations> (docs-data-collection)
[12]: <https://github.com/robot-colosseum/rvt_colosseum> (rvt-colosseum-repo)
