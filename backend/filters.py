import cv2
import numpy as np

def anime(image):
    import cv2
    import numpy as np

    # 1. Resize for better processing
    img = cv2.resize(image, None, fx=1, fy=1)

    # 2. Smooth image (reduce noise)
    smooth = cv2.bilateralFilter(img, d=9, sigmaColor=200, sigmaSpace=200)

    # 3. Color Quantization using K-Means
    data = np.float32(smooth).reshape((-1, 3))
    K = 8  # fewer colors = more anime-like
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.001)
    _, labels, centers = cv2.kmeans(
        data, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
    )
    centers = np.uint8(centers)
    quantized = centers[labels.flatten()]
    quantized = quantized.reshape(img.shape)

    # 4. Edge detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 7)
    edges = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        blockSize=9,
        C=2
    )

    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    # 5. Combine edges with color
    cartoon = cv2.bitwise_and(quantized, edges)

    # 6. Final enhancement
    cartoon = cv2.detailEnhance(cartoon, sigma_s=10, sigma_r=0.15)

    return cv2.cvtColor(cartoon, cv2.COLOR_BGR2RGB)

def ghibli(image):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img = cv2.bilateralFilter(img, 15, 80, 80)
    return img

def sketch(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    inv = cv2.bitwise_not(gray)
    blur = cv2.GaussianBlur(inv, (21, 21), 0)
    sketch = cv2.divide(gray, 255 - blur, scale=256)
    return cv2.cvtColor(sketch, cv2.COLOR_GRAY2RGB)

def portrait(image):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img = cv2.detailEnhance(img, sigma_s=10, sigma_r=0.15)
    return img