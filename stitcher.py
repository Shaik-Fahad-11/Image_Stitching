import cv2
import numpy as np
import imutils
import os

def stitch_images(image_paths, output_folder, filename="stitched_output.png"):
    """
    Stitches images provided in image_paths and saves to output_folder.
    Returns the path to the saved image or None if failed.
    """
    images = []
    for path in image_paths:
        img = cv2.imread(path)
        if img is not None:
            images.append(img)

    if len(images) < 2:
        return None, "Not enough images to stitch."

    # Create Stitcher
    imageStitcher = cv2.Stitcher_create()
    error, stitched_img = imageStitcher.stitch(images)

    if error != 0:
        return None, "Stitching failed. Likely not enough keypoints."

    # --- POST PROCESSING (Your Logic) ---
    # Add border
    stitched_img = cv2.copyMakeBorder(stitched_img, 10, 10, 10, 10, cv2.BORDER_CONSTANT, (0, 0, 0))

    # Grayscale & Threshold
    gray = cv2.cvtColor(stitched_img, cv2.COLOR_BGR2GRAY)
    thresh_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)[1]

    # Contours
    contours = cv2.findContours(thresh_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    if not contours:
        return None, "Post-processing failed."
        
    areaOI = max(contours, key=cv2.contourArea)

    mask = np.zeros(thresh_img.shape, dtype="uint8")
    x, y, w, h = cv2.boundingRect(areaOI)
    cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)

    minRectangle = mask.copy()
    sub = mask.copy()

    # Erosion loop
    while cv2.countNonZero(sub) > 0:
        minRectangle = cv2.erode(minRectangle, None)
        sub = cv2.subtract(minRectangle, thresh_img)

    contours = cv2.findContours(minRectangle.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    if not contours:
         # Fallback if erosion kills everything
        pass 
    else:
        areaOI = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(areaOI)
        stitched_img = stitched_img[y:y + h, x:x + w]

    # Save Output
    output_path = os.path.join(output_folder, filename)
    cv2.imwrite(output_path, stitched_img)

    return filename, None