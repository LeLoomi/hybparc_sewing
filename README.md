virTUos Hybparc Medical Sewing Training (UI)
==============

UI for a hands on medical sewing training software for med students. Students sew on a pad and get a grade (green, orange, red) according to achieved quality.
This UI is being developed at [MITZ](https://tu-dresden.de/med/mf/mitz), with evaluation Software being imported from [RWTH Aachen](https://www.rwth-aachen.de/go/id/a/).

General requirements
--------------------

> TBD

Linux specific adjustments
--------------------------

> currently copy-pasted from our [ECG-Project](https://github.com/leloomi/hybparc_aruco)

<u>Video capture id:</u><br>
Windows and MacOS use id 0 for the first camera, 1 for the second and so on. On Linux a USB camera has multiple `dev/videoX` interfaces, e.g. `video0` to `video3` for the first and `video4` to `video7` for the second camera. We recommend using the lowest interface per camera, i.e. 0 and 4. Using the Win/Mac 0 and 1 indices will result in an attempt to grab from the same camera, crashing the software.

<u>Video capture resolution and format:</u><br>
On Linux OpenCV (/the V4L2 driver) defaults to something, which is likely the lowest resolution and a wrong/limiting capture format. This can be fixed by setting the cv capture properties by hand, e.g. if our camera supports 3840x2160 via MJPG, the following should be applied to <u>all</u> your VideoCapture objects:
```` Python
stream.set(cv.CV_CAP_PROP_FOURCC, cv.VideoWriter.fourcc('M', 'J', 'P', 'G'))
        stream.set(cv.CV_CAP_PROP_FRAME_WIDTH, 3840)
        stream.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 2160)
````
To check available capture indices/devices run `v4l2-ctl --list-devices`
To check available formats, resolutions run `v4l2-ctl -d /dev/videoX --list-formats-ext`

<u>OpenCV and Python version:</u><br>
On MacOS and Windows PyQt6 supports Python 3.12. On Linux however, only Python 3.9 is currently<sup>Dec '24</sup> supported. You will have to downgrade your environment to Python 3.9 or you will be unable to install PyQt6.
<br>Additionally, potential issues may arise from which OpenCV package you install. On MacOS the standard opencv-python package works well. On Linux not everything might be supported. In case of crashes we recommend opencv-contrib-python.
