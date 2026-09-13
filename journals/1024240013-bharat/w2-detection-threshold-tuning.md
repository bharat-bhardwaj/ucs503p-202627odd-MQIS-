# Week 2 : Defect Detection Producing False Positives

## Error
No runtime error — but manual review of "good" (non-defective) images
showed several were being incorrectly flagged as REJECTED.

## Relevant Context
`detector.py`'s `find_defect_region()` function compares each captured
image against a reference "good" image using:
```python
diff = cv2.absdiff(gray_img, gray_ref)
diff = cv2.GaussianBlur(diff, (7, 7), 0)
_, thresh = cv2.threshold(diff, 45, 255, cv2.THRESH_BINARY)
```
followed by morphological close/open operations and contour extraction,
keeping only contours with area > 500.

## Key Observation
Minor lighting variation between the reference image and otherwise
identical "good" samples was producing small diff regions that still
exceeded the 500px area threshold, causing false rejections. The
Gaussian blur kernel size and threshold value were too sensitive for
the natural pixel-level variance in the dataset.

## Solution
Increased the minimum contour area threshold and slightly widened the
blur kernel to suppress low-level noise before thresholding:
```python
diff = cv2.GaussianBlur(diff, (9, 9), 0)
_, thresh = cv2.threshold(diff, 55, 255, cv2.THRESH_BINARY)
...
if cv2.contourArea(largest) > 800:
    return cv2.boundingRect(largest)
```
Re-tested against the full "good" sample set — false positive rate
dropped significantly while true defects were still correctly localized.

**Because:** reference-based image differencing is inherently sensitive
to lighting/noise; the threshold and minimum-area cutoff need to be
tuned empirically against real "good" samples, not guessed once and
left fixed.
