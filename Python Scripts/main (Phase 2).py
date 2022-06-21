from pathlib import Path
from picamera import PiCamera
from orbit import ISS
from time import sleep
import time
from datetime import datetime, timedelta
from logzero import logger, logfile
import csv
from skyfield import almanac
from skyfield.api import load, wgs84
import os

def add_csv_data(data_file, data):
    with open(data_file, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(data)
def convert(angle):
    sign, degrees,minutes, seconds = angle.signed_dms()
    exif_angle = f'{degrees:.0f}/1,{minutes:.0f}/1,{seconds*10:.0f}/10'
    return sign <0, exif_angle

def capture(camera,image):
    location = ISS.coordinates()
    south, exif_latitude = convert(location.latitude)
    west,exif_longitude = convert(location.longitude)
    camera.exif_tags['GPS.GPSLatitude'] = exif_latitude
    camera.exif_tags['GPS.GPSLatitudeRef'] = "S" if south else "N"
    camera.exif_tags['GPS.GPSLongitude'] = exif_longitude
    camera.exif_tags['GPS.GPSLongitudeRef'] = "W" if west else "E"
    
    camera.capture(image)
    
base_folder = Path(__file__).parent.resolve()
logfile(base_folder/"events.log")
camera = PiCamera()
try:
    camera.resolution = (4056,3040)
except:
    camera.resolution = (2592,1994)
data_file = base_folder/"data.csv"
with open(data_file,'w') as f:
    write = csv.writer(f)
    header = ("Counter","Date/time","Latitude","Longitude","Day")
    write.writerow(header)
image_path = base_folder/"images"
try:
    os.mkdir(image_path)
except:
    pass
counter = 1
eph = load('de421.bsp')
timescale = load.timescale()
start_time = datetime.now()
current_time = datetime.now()
while(current_time < start_time + timedelta(minutes=178)):
    try:
        location = ISS.coordinates()
        position = wgs84.latlon(location.latitude.degrees,location.longitude.degrees)
        f1 = almanac.sunrise_sunset(eph,position)
        t = timescale.now()
        data = (counter,datetime.now(),location.latitude.degrees,location.longitude.degrees,f1(t))
        add_csv_data(data_file,data)
        if f1(t) == True:
            image_file = f"{base_folder}/images/photo_{counter:03d}.jpg"
            capture(camera, image_file)
            logger.info(f"iteration {counter}")
        counter += 1
        sleep(14.99)
        current_time = datetime.now()

    except Exception as e:
        logger.error(f'{e.__class__.__name__}: {e}')
