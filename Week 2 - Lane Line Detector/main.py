from pathlib import Path
import cv2
import numpy as np

def extract(image):
    h, w = image.shape[:2]
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    white = cv2.inRange(hsv, (0, 0, 170), (179, 75, 255))
    yellow = cv2.inRange(hsv, (15, 65, 100), (40, 255, 255))
    filtered = cv2.bitwise_and(image, image, mask=white | yellow)
    blur = cv2.GaussianBlur(cv2.cvtColor(filtered, cv2.COLOR_BGR2GRAY), (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    vertices = np.array([[(int(w * x), int(h * y)) for x, y in
                          [(0.08, 0.99), (0.43, 0.58), (0.57, 0.58), (0.95, 0.99)]]])
    mask = np.zeros_like(edges)
    cv2.fillPoly(mask, vertices, 255)
    roi = cv2.bitwise_and(edges, mask)
    overlay = image.copy()
    lines = cv2.HoughLinesP(roi, 1, np.pi / 180, 25,
                            minLineLength=max(20, w // 25), maxLineGap=45)
    if lines is not None:
        for x1, y1, x2, y2 in lines[:, 0]:
            if abs(x2 - x1) > 1 and abs((y2 - y1) / (x2 - x1)) > 0.35:
                cv2.line(overlay, (x1, y1), (x2, y2), (0, 255, 0), 5)
    return {'hsv': filtered, 'blur': blur, 'canny': edges, 'roi': roi,
            'lanes': cv2.addWeighted(image, 0.75, overlay, 0.7, 0)}

'''
if __name__ == '__main__':
    output = Path('outputs')
    output.mkdir(exist_ok=True)
    for path in Path('images').glob('*'):
        image = cv2.imread(str(path))
        if image is None:
            continue
        for stage, result in extract(image).items():
            cv2.imwrite(str(output / f'{path.stem}_{stage}.png'), result)
        print('Processed:', path)
'''

if __name__ == '__main__':
    from tkinter import Tk, filedialog

    root = Tk()
    root.withdraw()
    path = filedialog.askopenfilename(
        title="Select Road Image",
        filetypes=[("Images", "*.png *.jpg *.jpeg")]
    )
    root.destroy()

    if not path:
        exit()

    image = cv2.imread(path)

    if image is None:
        print("Invalid image")
        exit()

    output = Path("outputs")
    output.mkdir(exist_ok=True)

    results = extract(image)

    for stage, result in results.items():
        cv2.imwrite(str(output / f"{Path(path).stem}_{stage}.png"), result)

    cv2.imshow("Original Image", image)
    cv2.imshow("HSV Filtered", results["hsv"])
    cv2.imshow("Canny Edges", results["canny"])
    cv2.imshow("ROI", results["roi"])
    cv2.imshow("Detected Lane Lines", results["lanes"])

    print("Processed:", path)
    print("Results saved in outputs folder")

    cv2.waitKey(0)
    cv2.destroyAllWindows()