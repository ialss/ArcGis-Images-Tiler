import requests
import os
from urllib.parse import urlencode
import geopandas as gpd
from shapely.geometry import box
import rasterio
import numpy as np
from rasterio.mask import mask


arcgis_url = "https://gis.cookcountyil.gov/imagery/rest/services/CookOrtho2024/ImageServer/exportImage?"
tiles_fdr = "tiles"

tile_resolution = 1024
crs = 3435

num_tiles = 2


os.makedirs(tiles_fdr, exist_ok=True)


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

tile_width = (xmax - xmin) / num_tiles
tile_height = (ymax - ymin) / num_tiles

if filtered_gdf.crs.to_epsg() != crs:
    filtered_gdf = filtered_gdf.to_crs(f"EPSG:{crs}")


tiles = []
for i in range(num_tiles):
    for j in range(num_tiles):
        tile_xmin = xmin + i * tile_width
        tile_xmax = tile_xmin + tile_width
        tile_ymin = ymin + j * tile_height
        tile_ymax = tile_ymin + tile_height


        tile_bbox = box(tile_xmin, tile_ymin, tile_xmax, tile_ymax)

        clipped_tile = tile_bbox.intersection(filtered_gdf.geometry.union_all())
        if not clipped_tile.is_empty:
            tiles.append(clipped_tile)



for idx, tile in enumerate(tiles):
    tileXmin, tileYmin, tileXmax, tileYmax = tile.bounds
    params = {
    'bbox': f"{tileXmin},{tileYmin},{tileXmax},{tileYmax}",
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
        filepath = os.path.join(tiles_fdr, f"tile_{idx+1}.png")
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"Tile successfully downloaded and saved at: {filepath}")
    else:
        print(f"Failed to download tile: {idx+1}")
        print(f"Error: {response.text}")


print("Tile download process complete!")
