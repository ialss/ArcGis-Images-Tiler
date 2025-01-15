import requests
import os
import geopandas as gpd

input_geojson = 'Municipality.geojson'

def reproject_geojson(input_file, target_crs):
    gdf = gpd.read_file(input_file)
    
    if gdf.crs != target_crs:
        print(f"CRS is different, reprojecting from {gdf.crs} to {target_crs}...")
        gdf = gdf.to_crs(target_crs)
        gdf.to_file(input_file, driver='GeoJSON')
        print(f"Reprojected GeoJSON saved as {input_file}")
    else:
        print(f"CRS is already {target_crs}, no reprojecting needed.")


def search_by_municipality(input_file, municipality_name):
    gdf = gpd.read_file(input_file)
    
    municipality = gdf[gdf['MUNICIPALITY'] == municipality_name]
    
    if not municipality.empty:
        print(f"Found boundary for {municipality_name}")
        return municipality
    else:
        print(f"No boundary found for {municipality_name}")
        return None


def download_raster(bbox, size, output_filename):
    url = "https://gis.cookcountyil.gov/imagery/rest/services/CookOrtho2024/ImageServer/exportImage"
    
    params = {
        'bbox': bbox,
        'bboxSR': '',
        'size': size,
        'imageSR': '',
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
    
    param_str = '&'.join([f"{key}={value}" for key, value in params.items()])
    full_url = f"{url}?{param_str}"
    
    print(f"Full URL: {full_url}")
    
    response = requests.get(full_url)
    
    if response.status_code == 200:
        if not os.path.exists('tiles'):
            os.makedirs('tiles')
        
        output_path = os.path.join('tiles', output_filename)
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"Image saved as {output_path}")
    else:
        print(f"Failed to download image. Status code: {response.status_code}")

bbox = '994999.9999770783%2C1740000.000119239%2C1212499.9999770783%2C2007500.000119239'
size = '1024%2C1024'
output_filename = 'chicago_raster.png'
target_crs = 'EPSG:6454'
municipality_name = 'Chicago'


reproject_geojson(input_geojson, target_crs)
download_raster(bbox, size, output_filename)

boundary = search_by_municipality(input_geojson, municipality_name)

if boundary is not None:
    print(boundary)

