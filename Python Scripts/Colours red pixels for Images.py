import cv2
import numpy as np
from fastiecm import fastiecm
import os
from pathlib import Path
import csv
directory = "D:\\Astro Pi images\\Images\\"
data_file = "D:\\Astro Pi images\\NDVIdata.csv"

def contrast_stretch(im):
    in_min = np.percentile(im, 5)
    in_max = np.percentile(im, 95)

    out_min = 0.0
    out_max = 255.0

    out = im - in_min
    out *= ((out_min - out_max) / (in_min - in_max))
    out += in_min

    return out

def calc_ndvi(image):
    b, g, r = cv2.split(image)
    bottom = (r.astype(float) + b.astype(float))
    bottom[bottom==0] = 0.01
    ndvi = (b.astype(float) - r) / bottom
    return ndvi

def display(image, image_name):
    image = np.array(image, dtype=float)/float(255)
    shape = image.shape
    height = int(shape[0] / 2)
    width = int(shape[1] / 2)
    image = cv2.resize(image, (width, height))
    cv2.namedWindow(image_name)
    cv2.imshow(image_name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

with open(data_file, 'r') as f:
    read = csv.reader(f)
    line_count = 0
    for row in read:
        if (line_count != 0) and ((line_count % 2)==0):
            image_id = row[0]
            pixels = int(row[3])
            if row[4] == "TRUE":
                if pixels >= 1000000:
                    average = float(row[1])
                    max = float(row[2])
                    if (max > 0.5):
                        print(image_id)
                        selected = cv2.imread('Images\\'+str(image_id)+'.jpg')
                        new = selected
                        contrasted = contrast_stretch(selected)
                        ndvi = calc_ndvi(contrasted)
                        counter = 0
                        # Ratio of circular disk = (12.7/13.2 * 3040 and 12.7/17.4 * 4056) 9.9/17.4 * 4056 and 6.35/13.2 * 3040
                        for y in range(3040):
                            for x in range(4056):
                                if (((x-((9.9/17.4) * 4056))**2)+(((y-((6.35/13.2) * 3040))**2)) <= ((5.8/13.2) * 3040)**2): # Checks if pixel is within range
                                    b = selected[y,x,0]
                                    g = selected[y,x,1]
                                    r = selected[y,x,2]
                                    if ((b < 140) or (g < 140)) or (r < 140): #Does not include Cloud cover
                                        if ((b > 100) or (g > 100)) or (r > 100): # Does not include Water cover
                                            if (ndvi[y,x] >= -0.9) and (ndvi[y,x] <=0.3):
                                                new[y,x] = [0,0,255]
                                                counter += 1
                                else:
                                    new[y,x] = [0,0,0]
                        print("Done",counter)
                        cv2.imwrite('Raw Images for Reforestation\\'+str(image_id)+'.jpg', new)

        line_count += 1
"""
counter = 0
for filename in os.listdir(directory):
    if filename.endswith(".jpg"):
        counter += 1
        print("Loading",counter,"/",len(os.listdir(directory)))
        selected = cv2.imread('Images\\'+str(filename))
        contrasted = contrast_stretch(selected)
        ndvi = calc_ndvi(contrasted)
        total_sum = 0
        count = 0
        max = 0
        # Ratio of circular disk = (12.7/13.2 * 3040 and 12.7/17.4 * 4056) 9.9/17.4 * 4056 and 6.35/13.2 * 3040
        for y in range(3040):
            for x in range(4056):
                if (((x-((9.9/17.4) * 4056))**2)+(((y-((6.35/13.2) * 3040))**2)) <= ((6.35/13.2) * 3040)**2): # Checks if pixel is within range
                    b = selected[y,x,0]
                    g = selected[y,x,1]
                    r = selected[y,x,2]
                    if ((b < 220) or (g < 220)) or (r < 220): #Does not include Cloud cover
                        if ((b > 70) or (g > 70)) or (r > 70): # Does not include Water cover
                            total_sum = ndvi[y,x] + total_sum
                            if max < ndvi[y,x]:
                                max = ndvi[y,x]
                            count += 1
        if count != 0:
            data = (counter,(total_sum/count),max,count)
        else:
            data = (counter,"NaN","NaN",count)
        add_csv_data(data_file, data)
        print(counter,"Done")
"""
