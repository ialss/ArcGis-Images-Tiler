import requests
import os
from urllib.parse import urlencode

arcgis_url = "https://gis.cookcountyil.gov/imagery/rest/services/CookOrtho2024/ImageServer/exportImage?" 
output_dir = "tiles" 

x_min = 994999.9999770783
y_min = 1740000.000119239
x_max = 1212499.9999770783
y_max = 2007500.000119239
tile_resolution = 1024  
crs = 3435  

os.makedirs(output_dir, exist_ok=True)

geojson_path = "Municipality.geojson"

# Correctly format bbox without parentheses
bbox = f"{x_min},{y_min},{x_max},{y_max}"
print(bbox)

params = {
    'bbox': bbox,
    'bboxSR': '',
    'size': '1000,1000',
    'imageSR': '',
    'time': '',
    'format': 'png',
    'pixelType': 'U8',
    'noData': '',
    'noDataInterpretation': 'esriNoDataMatchAny',
    'interpolation': 'RSP_BilinearInterpolation',
    'compression': '',
    'compressionQuality': '',
    'bandIds': '',
    'sliceId': '',
    'mosaicRule': '',
    'renderingRule': '',
    'adjustAspectRatio': 'true',
    'validateExtent': 'false',
    'lercVersion': '1',
    'compressionTolerance': '',
    'f': 'image'
}

# Print the full URL (to debug)
print(f"{arcgis_url}{urlencode(params, doseq=True)}")

# Make the GET request
response = requests.get(f"{arcgis_url}{urlencode(params, doseq=True)}")

if response.status_code == 200:
    filename = f"tile_1.png"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "wb") as f:
        f.write(response.content)
    print(f"Tile successfully downloaded and saved at: {filepath}")
else:
    print(f"Failed to download tile: {bbox}")
    print(f"Error: {response.text}")

print("Tile download process complete!")
