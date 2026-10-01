import cv2
import numpy as np


MAX_DOCUMENT_SIDE = 1600


def resize_for_speed(image, max_side=MAX_DOCUMENT_SIDE):
    height, width = image.shape[:2]
    longest = max(height, width)
    if longest <= max_side:
        return image
    scale = max_side / longest
    return cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)


def order_points(points):
    points = np.array(points, dtype=np.float32)
    result = np.zeros((4, 2), dtype=np.float32)
    total = points.sum(axis=1)
    difference = np.diff(points, axis=1).reshape(-1)
    result[0] = points[np.argmin(total)]
    result[2] = points[np.argmax(total)]
    result[1] = points[np.argmin(difference)]
    result[3] = points[np.argmax(difference)]
    return result


def perspective_transform(image, points):
    rect = order_points(points)
    tl, tr, br, bl = rect
    width = int(max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl)))
    height = int(max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl)))
    destination = np.array(
        [
            [0, 0],
            [width - 1, 0],
            [width - 1, height - 1],
            [0, height - 1],
        ],
        dtype=np.float32,
    )
    matrix = cv2.getPerspectiveTransform(rect, destination)
    return cv2.warpPerspective(image, matrix, (width, height))


def detect_document(image):
    working = resize_for_speed(image, 800)
    scale_y = image.shape[0] / working.shape[0]
    scale_x = image.shape[1] / working.shape[1]

    gray = cv2.cvtColor(working, cv2.COLOR_BGR2GRAY) if working.ndim == 3 else working
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    image_area = working.shape[0] * working.shape[1]
    candidates = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < image_area * 0.30:
            continue
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        if len(approx) == 4:
            points = approx.reshape(4, 2).astype(np.float32)
            points[:, 0] *= scale_x
            points[:, 1] *= scale_y
            candidates.append((area, points))

    if not candidates:
        return None
    candidates.sort(reverse=True, key=lambda item: item[0])
    return candidates[0][1]


def correct_document(image):
    image = resize_for_speed(image)
    points = detect_document(image)
    if points is None:
        return image
    return perspective_transform(image, points)
