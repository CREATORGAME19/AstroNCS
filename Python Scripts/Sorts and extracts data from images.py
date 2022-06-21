import os
import csv
from pathlib import Path
from exif import Image
from skyfield import almanac
from skyfield.api import load, wgs84, utc
from datetime import datetime, timedelta
directory = "D:\\Astro Pi images\\Images\\"
def add_csv_data(data_file, data):
    with open(data_file, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(data)

def latlng_conversion(latlng, ref):
    degrees = latlng[0]
    minutes = latlng[1] / 60.0 
    seconds = latlng[2]/ 3600.0

    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds

    return round(degrees + minutes + seconds, 5)

base_folder = Path(__file__).parent.resolve()
data_file = base_folder/"data.csv"
with open(data_file, 'w') as f:
    write = csv.writer(f)
    header = ("Counter","Date/time","Latitude","Longitude","Seen?")
    write.writerow(header)

counter = 0
for filename in os.listdir(directory):
    if filename.endswith(".jpg"):
      counter += 1
      imagepath = str(directory)+str(filename)
      image = Image(imagepath)
      time = image.datetime_original
      latitude_ref = image.gps_latitude_ref
      longtitude_ref = image.gps_longitude_ref
      latitude = image.gps_latitude
      longtitude = image.gps_longitude
      lat = latlng_conversion(latitude,latitude_ref)
      lng = latlng_conversion(longtitude,longtitude_ref)
      eph = load('de421.bsp')
      timescale = load.timescale()
      position = wgs84.latlon(lat,lng)
      f = almanac.sunrise_sunset(eph, position)
      timeobj = datetime.strptime(time, '%Y:%m:%d %H:%M:%S')
      timeobj = timescale.from_datetime(timeobj.replace(tzinfo=utc))
      if f(timeobj) == True:
          day = True
      else:
          day = False
      data = (counter,time,lat,lng,day)
      add_csv_data(data_file, data)
      new_path = str(directory)+str(counter)+".jpg"
      os.rename(imagepath,new_path)
      """
      for tag_id in exifdata:
        tag = TAGS.get(tag_id, tag_id)
        data = exifdata.get(tag_id)
        """
        

