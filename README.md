virTUos Hybparc Medical Sewing Training (UI)
==============

UI for a hands on medical sewing training software for med students. Students sew on a pad and get a grade (green, orange, red) according to achieved quality.
This UI is being developed at [MITZ](https://tu-dresden.de/med/mf/mitz), with evaluation Software being imported from [RWTH Aachen](https://www.rwth-aachen.de/go/id/a/).

Also check out our hands-on [ECG training sofware](https://github.com/LeLoomi/hybparc_aruco)!

General requirements
--------------------
> Incomplete
- FFMPEG

Trivia
------
- Recommeded to use Pylance with type checking mode 'Standard'
- On MacOS and Windows PyQt6 supports Python 3.12. On Linux however, only Python 3.9 is currently<sup>Dec '24</sup> supported. You will have to downgrade your environment to Python 3.9 or you will be unable to install PyQt6.
- Issues may arise from which OpenCV package you install. On MacOS the standard opencv-python package works well. On Linux, not everything might be supported. In case of crashes we recommend opencv-contrib-python.
