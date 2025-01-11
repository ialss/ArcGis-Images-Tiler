import requests
import os
from urllib.parse import urlencode
import geopandas as gpd

from shapely.geometry import box

arcgis_url = "https://gis.cookcountyil.gov/imagery/rest/services/CookOrtho2024/ImageServer/exportImage?"
output_dir = "tiles"

tile_resolution = 1024
crs = 3435


os.makedirs(output_dir, exist_ok=True)


geojson_path = "Municipality.geojson"


gdf = gpd.read_file(geojson_path)


municipality = "Palatine"
filtered_gdf = gdf[gdf["MUNICIPALITY"] == municipality]

bbox = filtered_gdf.geometry.bounds.iloc[0]

minx, miny, maxx, maxy = bbox

bbox_geo = box(minx, miny, maxx, maxy)
gdf_geo = gpd.GeoDataFrame({'geometry': [bbox_geo]})


gdf_geo = gdf_geo.set_crs('EPSG:4326')


gdf_geo = gdf_geo.to_crs(f"EPSG:{crs}")


xmin, ymin, xmax, ymax = gdf_geo.geometry.bounds.iloc[0]


params = {
    'bbox': f"{xmin},{ymin},{xmax},{ymax}",
    'bboxSR': crs,
    'size': f"{tile_resolution},{tile_resolution}",
    'imageSR': crs,
    'format': 'png', # types: jpgpng | png | png8 | png24 | jpg | bmp | gif | tiff | png32 | bip | bsq | lerc
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

print(f"{arcgis_url}{urlencode(params, doseq=True)}")


response = requests.get(f"{arcgis_url}{urlencode(params, doseq=True)}")


if response.status_code == 200:
    filename = f"tile_1.png"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "wb") as f:
        f.write(response.content)
    print(f"Tile successfully downloaded and saved at: {filepath}")
else:
    print(f"Failed to download tile: {xmin},{ymin},{xmax},{ymax}")
    print(f"Error: {response.text}")

print("Tile download process complete!")
