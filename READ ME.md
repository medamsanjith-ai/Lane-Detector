# Lane Detection using OpenCV

A Python script for detecting straight lane markings in road images. It uses HSV color filtering, Canny edge detection, a region of interest mask, and the Probabilistic Hough Line Transform to identify likely lane segments.

The script accepts one image at a time through a file picker. It displays the detection results in OpenCV windows and saves images from each processing stage to an `outputs` folder.

## Requirements

- Python 3
- OpenCV (`opencv-python`)
- NumPy
- Tkinter for the file picker (usually included with Python, but some Linux installations require a separate package)
- A desktop environment capable of opening Tkinter and OpenCV windows

Install the Python packages:

```bash
python -m pip install opencv-python numpy
```

## Running the script

Save the code as `lane_extractor.py`, then run:

```bash
python lane_extractor.py
```

A file picker opens. Select a road image in PNG or JPEG format. The script processes the selected image, saves the results in `outputs/`, and opens windows showing the original image, filtered image, edges, region of interest, and highlighted line segments.

Press a key while an OpenCV window is focused to close the result windows.

## Project structure

```text
.
├── lane_extractor.py
└── outputs/                 # Created on the first successful run
```

For an image called `road.jpg`, the output files are:

```text
outputs/
├── road_hsv.png
├── road_blur.png
├── road_canny.png
├── road_roi.png
└── road_lanes.png
```

The `hsv` filename refers to the color-filtered BGR image, not the raw HSV image.

## How detection works

### Color filtering

The input image is converted from BGR to HSV. Two threshold masks select pixels that fall within the configured white and yellow ranges:

```python
white = cv2.inRange(hsv, (0, 0, 170), (179, 75, 255))
yellow = cv2.inRange(hsv, (15, 65, 100), (40, 255, 255))
```

The masks are combined, then applied to the original image. Pixels outside both ranges are set to black.

### Edge detection

The filtered image is converted to grayscale and smoothed with a 5 by 5 Gaussian kernel. Canny edge detection then finds edges using thresholds of 50 and 150.

### Region of interest

A trapezoidal mask limits detection to the lower part of the image. Its corners use these coordinates relative to image width and height:

```python
(0.08, 0.99)
(0.43, 0.58)
(0.57, 0.58)
(0.95, 0.99)
```

This region is fixed relative to the image size. It may need adjustment for different camera angles or framing.

### Line detection

`cv2.HoughLinesP()` finds straight line segments within the masked edge image. The configured settings are:

| Setting | Value |
| --- | --- |
| Distance resolution | 1 pixel |
| Angle resolution | 1 degree |
| Vote threshold | 25 |
| Minimum line length | `max(20, width // 25)` |
| Maximum line gap | 45 pixels |

Segments with a horizontal endpoint difference of 1 pixel or less are ignored. The remaining segments must have an absolute slope greater than 0.35. Accepted segments are drawn in green on a copy of the input image, which is then blended with the original.

## Using the extraction function

The image-processing logic is available separately from the file picker:

```python
import cv2
from lane_extractor import extract

image = cv2.imread("road.jpg")
if image is None:
    raise ValueError("Could not read road.jpg")

results = extract(image)
cv2.imwrite("detected_lanes.png", results["lanes"])
```

`extract()` returns a dictionary with these keys:

| Key | Description |
| --- | --- |
| `hsv` | Color-filtered BGR image |
| `blur` | Blurred grayscale image |
| `canny` | Canny edge image |
| `roi` | Edge image after the trapezoidal mask |
| `lanes` | Image with accepted segments drawn in green |

## Limitations

This script detects straight line segments, not complete lane boundaries. It does not estimate lane curvature, identify which markings belong to the current driving lane, or track lanes across video frames.

Detection depends on the fixed color thresholds and region of interest. Shadows, worn markings, unusual camera angles, or objects with similar colors may lead to missed or incorrect segments. Nearly vertical segments are also excluded by the slope filter.

The `cv2.addWeighted()` call uses weights of 0.75 and 0.7, so bright background pixels may appear brighter in the final output. The current script is intended for local image processing and requires a graphical desktop session.

## Batch processing code

The source file also contains an inactive batch-processing section inside a triple-quoted string. That section iterates through files in an `images` folder and saves the processing results. It is not executed by the current script, which uses a Tkinter file picker instead.
