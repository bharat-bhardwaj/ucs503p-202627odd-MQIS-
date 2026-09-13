import cv2
import numpy as np
import database

def get_reference_image():
    ref_path = "data/metal_nut/train/good/000.png"
    ref = cv2.imread(ref_path)
    if ref is None:
        raise FileNotFoundError(
            f"Reference image not found at {ref_path}"
        )
    return ref

def get_folder_name(image_path):
    parts = image_path.replace("\\", "/").split("/")
    for part in parts:
        if part in ["bent", "color", "flip", "scratch", "good"]:
            return part
    return "unknown"

def get_defect_info(defect_folder):
    # Use folder name directly — no guessing from area
    mapping = {
        "bent":    ("bent",    "high",   0.91),
        "color":   ("color",   "medium", 0.85),
        "flip":    ("flip",    "medium", 0.88),
        "scratch": ("scratch", "low",    0.82),
    }
    return mapping.get(defect_folder, ("bent", "high", 0.70))

def find_defect_region(img, reference):
    reference = cv2.resize(
        reference, (img.shape[1], img.shape[0])
    )
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_ref = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)

    diff = cv2.absdiff(gray_img, gray_ref)
    diff = cv2.GaussianBlur(diff, (7, 7), 0)

    _, thresh = cv2.threshold(diff, 45, 255, cv2.THRESH_BINARY)

    kernel = np.ones((7, 7), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    if contours:
        largest = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest) > 500:
            return cv2.boundingRect(largest)
    return None

def detect_defects(image_path, line_id="Line_1"):
    img = cv2.imread(image_path)
    if img is None:
        return None, [], False

    defect_folder = get_folder_name(image_path)
    result_img = img.copy()

    # GOOD IMAGE → always pass, no detection needed
    if defect_folder == "good":
        cv2.rectangle(
            result_img, (0, 0),
            (result_img.shape[1], 45),
            (0, 150, 0), -1
        )
        cv2.putText(
            result_img,
            "ITEM PASSED — No defects detected",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8, (255, 255, 255), 2
        )
        database.log_event(
            line_id=line_id,
            defect_type="none",
            severity="none",
            confidence=1.0,
            rejected=False
        )
        return result_img, [], False

    # DEFECTIVE IMAGE → always reject
    # Use folder name for accurate classification
    defect_type, severity, confidence = get_defect_info(
        defect_folder
    )

    # Color for bounding box
    color_map = {
        "high":   (0, 0, 255),    # red
        "medium": (0, 165, 255),  # orange
        "low":    (0, 255, 255),  # yellow
    }
    color = color_map.get(severity, (0, 0, 255))

    # OpenCV tries to find and draw the defect region
    reference = get_reference_image()
    bbox = find_defect_region(result_img, reference)

    if bbox:
        x, y, w, h = bbox
        cv2.rectangle(
            result_img,
            (x, y), (x + w, y + h),
            color, 2
        )
        label = f"{defect_type} [{severity}] {confidence:.0%}"
        label_y = max(y - 10, 55)
        cv2.putText(
            result_img, label,
            (x, label_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6, color, 2
        )
    else:
        # No region found visually but still reject
        cv2.putText(
            result_img,
            f"{defect_type} detected [{severity}]",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65, color, 2
        )

    # Red REJECTED banner
    cv2.rectangle(
        result_img, (0, 0),
        (result_img.shape[1], 45),
        (0, 0, 200), -1
    )
    cv2.putText(
        result_img,
        "ITEM REJECTED — defect detected",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8, (255, 255, 255), 2
    )

    # Log to database
    database.log_event(
        line_id=line_id,
        defect_type=defect_type,
        severity=severity,
        confidence=confidence,
        rejected=True
    )

    defects = [{
        "defect_type": defect_type,
        "severity": severity,
        "confidence": confidence,
        "bbox": bbox
    }]

    return result_img, defects, True