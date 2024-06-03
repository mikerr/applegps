from wloc import *
import gmplot
import json

maclocs = QueryBSSID("12:34:56:78:90:12", more_results=True)

# add markers to map
print (maclocs)
lat,lon = ( next(iter(maclocs.values()))  ) # get first location

gmap = gmplot.GoogleMapPlotter( lat, lon , 17, apikey="your-key-here")

for mac,loc in maclocs.items():
        lat,lon = loc
        gmap.marker(lat,lon,title = mac)

print (len(maclocs), "items")
gmap.draw('map.html')

json.dump( maclocs, open( "wifis.json", 'w' ) )
