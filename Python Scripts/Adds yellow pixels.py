import os
os.environ["OPENCV_IO_MAX_IMAGE_PIXELS"] = pow(2,40).__str__()
import cv2
import numpy as np
from pathlib import Path
import csv
import math
import requests

#directory = "D:\\Astro Pi images\\Filtered Reforestation Images\\"
data_file = "D:\\Astro Pi images\\data.csv"

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
def add_csv_data(data_file1, data):
    with open(data_file1, 'a') as f2:
        writer = csv.writer(f2)
        writer.writerow(data)
base_folder = Path(__file__).parent.resolve()
data_file1 = base_folder/"Forestation_data.csv"

with open(data_file1, 'w') as f2:
    write = csv.writer(f2)
    header = ("Counter","Pixels")
    write.writerow(header)

with open(data_file, 'r') as f:
    read = csv.reader(f)
    line_count = 0
    for row in read:
        if (line_count != 0) and ((line_count % 2)==0):
            image_id = row[0]
            lat = float(row[2])
            long = float(row[3])
            continue1 = True
            selected = cv2.imread('Filtered Reforestation Images\\'+str(image_id)+'.png')
            if not(selected is None):
                new = selected
                midy = 0
                midx = 0
                for y in range(len(selected)):
                    for x in range(len(selected[1])):
                        b = selected[y,x,0]
                        g = selected[y,x,1]
                        r = selected[y,x,2]
                        if ((r == 34) and (b == 76)) and (g == 177):
                            midy = y
                            midx = x
                """
                midy = round(len(selected)/2)-58
                midx = round(len(selected[0])/2)+280
                """
                if (midx != 0) and (midy != 0):
                    # Ratio of circular disk = (12.7/13.2 * 3040 and 12.7/17.4 * 4056) 9.9/17.4 * 4056 and 6.35/13.2 * 3040
                    counter = 0
                    mapdatainfo = ""
                    for y in range(len(selected)):
                        for x in range(len(selected[1])):
                            b = selected[y,x,0]
                            g = selected[y,x,1]
                            r = selected[y,x,2]
                            if ((r >= 130) and (b <= 50)) and (g <= 50): # Checks if pixel is red
                                xdistance = (x-midx)
                                ydistance = (y-midy)
                                if image_id == "16":
                                    print(x,y)
                                if not((xdistance == 0) and (ydistance == 0)):
                                    final_distance = math.sqrt(((xdistance*0.10793)**2) + ((ydistance*0.10794)**2))
                                    if xdistance > 0:
                                        if ydistance < 0:
                                            bearing = math.atan(xdistance/(ydistance*-1))
                                        elif ydistance >= 0:
                                            bearing = ((math.pi)/2)+math.atan(ydistance/xdistance)

                                    elif xdistance < 0:
                                        if ydistance <= 0:
                                            bearing = (((math.pi)*3)/2)+math.atan((ydistance)/xdistance)
                                        elif ydistance > 0:
                                            bearing = (math.pi)+math.atan((xdistance*-1)/ydistance)

                                    else:
                                        if ydistance < 0:
                                            bearing = 0
                                        elif ydistance > 0:
                                            bearing = (math.pi)
                                    #bearing = bearing-math.pi
                                    R = 6378.1 #Radius of the Earth
                                    
                                    #Converts to coordinates using bearings between points and distance
                                    
                                    lat1 = math.radians(lat) #Current lat point converted to radians
                                    lon1 = math.radians(long) #Current long point converted to radians

                                    lat2 = math.asin( math.sin(lat1)*math.cos(final_distance/R) +
                                         math.cos(lat1)*math.sin(final_distance/R)*math.cos(bearing))

                                    lon2 = lon1 + math.atan2(math.sin(bearing)*math.sin(final_distance/R)*math.cos(lat1),
                                                 math.cos(final_distance/R)-math.sin(lat1)*math.sin(lat2))

                                    lat2 = math.degrees(lat2)
                                    lon2 = math.degrees(lon2)
                                else:
                                    lat2 = lat
                                    lon2 = long
                                roundedlat = str(math.ceil(lat2/20)*20)
                                roundedlon = str(math.floor(lon2/20)*20)
                                if roundedlat == "0":
                                    roundedlat = "N00"
                                elif roundedlat[0] != "-":
                                    roundedlat = "N"+roundedlat
                                else:
                                    roundedlat = "S"+roundedlat[1:]
                                if roundedlon == "0":
                                    roundedlon = "E000"
                                elif (roundedlon[0] != "-"):
                                    if len(roundedlon) != 3:
                                        roundedlon = "0E"+roundedlon
                                    else:
                                        roundedlon = "E"+roundedlon
                                else:
                                    if len(roundedlon) != 4:
                                        roundedlon = "W0"+roundedlon[1:]
                                    else:
                                        roundedlon = "W"+roundedlon[1:]
                                        
                                #Downloads the necessary layer data from the internet
                                
                                if mapdatainfo != (str(roundedlat)+"_"+str(roundedlon)):
                                    mapdata = cv2.imread('Forestation Mapping Data\\'+str(roundedlat)+"_"+str(roundedlon)+'.tif')
                                    mapdatainfo = str(roundedlat)+"_"+str(roundedlon)
                                    if mapdata is None:
                                        url = "https://s3-eu-west-1.amazonaws.com/vito.landcover.global/v3.0.1/2019/"+str(roundedlon)+str(roundedlat)+"/"+str(roundedlon)+str(roundedlat)+"_PROBAV_LC100_global_v3.0.1_2019-nrt_Discrete-Classification-map_EPSG-4326.tif"
                                        r = requests.get(url, allow_redirects=True)
                                        open('Forestation Mapping Data\\'+str(roundedlat)+"_"+str(roundedlon)+'.tif', 'wb').write(r.content)
                                        mapdata = cv2.imread('Forestation Mapping Data\\'+str(roundedlat)+"_"+str(roundedlon)+'.tif')
                                if lat2 < 0:
                                    changeinlat = ((int(roundedlat[1:])*-1)-lat2)
                                else:
                                    changeinlat = (int(roundedlat[1:])-lat2)
                                if lon2 < 0:
                                    changeinlon = lon2+(int(roundedlon[1:]))
                                else:
                                    changeinlon = lon2-int(roundedlon[1:])
                                
                                total_latpixels = len(mapdata)
                                total_lonpixels = len(mapdata[0])
                                y1 = math.ceil((changeinlat/20)*total_latpixels)-1
                                x1 = math.ceil((changeinlon/20)*total_lonpixels)-1
                                if ((mapdata[y1,x1,0] == 30) and (mapdata[y1,x1,1] == 30)) and (mapdata[y1,x1,2] == 30):
                                    new[y,x] = [0,251,255]
                                    counter += 1


                                
                    print("Done",counter)
                    data = (image_id,counter)
                    add_csv_data(data_file1, data)
                    cv2.imwrite('Final Images\\'+str(image_id)+'.jpg', new)

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
