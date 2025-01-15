import requests
import os
import geopandas as gpd


class GeoJSONFileStuff:
    def __init__(self, input_file, target_crs):
        self.input_file = input_file
        self.target_crs = target_crs

    def reproject(self):
        gdf = gpd.read_file(self.input_file)
        if gdf.crs != self.target_crs:
            print(f"CRS is different, reprojecting from {gdf.crs} to {self.target_crs}...")
            gdf = gdf.to_crs(self.target_crs)
            gdf.to_file(self.input_file, driver='GeoJSON')
        else:
            print(f"CRS is already {self.target_crs}, no reprojecting needed.")


class searchCity:
    def __init__(self, input_file):
        self.input_file = input_file

    def search_by_municipality(self, municipality_name):
        gdf = gpd.read_file(self.input_file)
        municipality = gdf[gdf['MUNICIPALITY'] == municipality_name]
        if not municipality.empty:
            print(f"Found boundary for {municipality_name}")
            return municipality
        else:
            print(f"No boundary found for {municipality_name}")
            return None


class tileDownloader:
    def __init__(self, url, output_folder='tiles'):
        self.url = url
        self.output_folder = output_folder

    def download(self, bbox, size, output_filename):
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
        full_url = f"{self.url}?{param_str}"

        print(f"Full URL: {full_url}")

        response = requests.get(full_url)

        if response.status_code == 200:
            if not os.path.exists(self.output_folder):
                os.makedirs(self.output_folder)

            output_path = os.path.join(self.output_folder, output_filename)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"Image saved as {output_path}")
        else:
            print(f"Failed to download image. Status code: {response.status_code}")


class create_tiles:
    def __init__(self, geojson_file, target_crs, bbox, size, output_filename):
        self.geojson_file = geojson_file
        self.target_crs = target_crs
        self.bbox = bbox
        self.size = size
        self.output_filename = output_filename

        self.geojson_processor = GeoJSONFileStuff(self.geojson_file, self.target_crs)
        self.municipality_searcher = searchCity(self.geojson_file)
        self.raster_downloader = tileDownloader(
            url="https://gis.cookcountyil.gov/imagery/rest/services/CookOrtho2024/ImageServer/exportImage"
        )

    def process(self, municipality_name):
        self.geojson_processor.reproject()
        self.raster_downloader.download(self.bbox, self.size, self.output_filename)

        boundary = self.municipality_searcher.search_by_municipality(municipality_name)
        if boundary is not None:
            print(boundary)


# Usage
bbox = '994999.9999770783%2C1740000.000119239%2C1212499.9999770783%2C2007500.000119239'
size = '1024%2C1024'
output_filename = 'chicago_raster.png'
target_crs = 'EPSG:6454'
municipality_name = 'Chicago'
input_geojson = 'Municipality.geojson'

municipality_processor = create_tiles(input_geojson, target_crs, bbox, size, output_filename)
municipality_processor.process(municipality_name)
