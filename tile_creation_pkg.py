import os
import requests
import geopandas as gpd

class GeoJSONFile:
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

    def search_by_municipality(self, municipality_name):
        gdf = gpd.read_file(self.input_file)
        municipality = gdf[gdf['MUNICIPALITY'] == municipality_name]
        if not municipality.empty:
            print(f"Found boundary for {municipality_name}")
            return municipality
        else:
            print(f"No boundary found for {municipality_name}")
            return None

class Tiles:
    def __init__(self, geojson_processor, url, output_folder='tiles', bbox_size=1000):
        self.geojson_processor = geojson_processor
        self.url = url
        self.output_folder = output_folder
        self.bbox_size = bbox_size

    def get_bounding_boxes(self, boundary):
        minx, miny, maxx, maxy = boundary.bounds
        bboxes = []

        x_start = minx
        while x_start < maxx:
            y_start = miny
            while y_start < maxy:
                x_end = min(x_start + self.bbox_size, maxx)
                y_end = min(y_start + self.bbox_size, maxy)

                bboxes.append((x_start, y_start, x_end, y_end))
                y_start += self.bbox_size
            x_start += self.bbox_size
        return bboxes

    def download_tile(self, bbox, size, output_filename):
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
            'adjustAspectRatio': 'true',
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

    def download_tiles(self, municipality_name, size='1024%2C1024'):
        municipality = self.geojson_processor.search_by_municipality(municipality_name)

        if municipality is not None:
            municipality = municipality.to_crs(self.geojson_processor.target_crs)
            bboxes = self.get_bounding_boxes(municipality.geometry.iloc[0])

            print(f"The number of tiles to be downloaded: {len(bboxes)}")

            for i, bbox in enumerate(bboxes):
                output_filename = f"{municipality_name}_tile_{i}.png"
                bbox_str = '%2C'.join(map(str, bbox))
                self.download_tile(bbox=bbox_str, size=size, output_filename=output_filename)
        else:
            print(f"No boundary found for {municipality_name}")


#--------------------------------------------------------------------------------------------------------------------
#                   ('-. .-.   ('-.         .-') _               ('-.         .-') _    ('-. .-.           .-')       
#                   ( OO )  /  ( OO ).-.    ( OO ) )            _(  OO)       (  OO) )  ( OO )  /          ( OO ).    
#         .-----. ,--. ,--.  / . --. /,--./ ,--,'  ,----.    (,------.      /     '._ ,--. ,--.  ,-.-') (_)---\_)     
#        '  .--./ |  | |  |  | \-.  \ |   \ |  |\ '  .-./-')  |  .---'      |'--...__)|  | |  |  |  |OO)/    _ |  
#        |  |('-. |   .|  |.-'-'  |  ||    \|  | )|  |_( O- ) |  |          '--.  .--'|   .|  |  |  |  \\  :` `.  
#       /_) |OO  )|       | \| |_.'  ||  .     |/ |  | .--, \(|  '--.          |  |   |       |  |  |(_/ '..`''.) 
#       ||  |`-'| |  .-.  |  |  .-.  ||  |\    | (|  | '. (_/ |  .--'          |  |   |  .-.  | ,|  |_.'.-._)   \ 
#      (_'  '--'\ |  | |  |  |  | |  ||  | \   |  |  '--'  |  |  `---.         |  |   |  | |  |(_|  |   \       / 
#         `-----' `--' `--'  `--' `--'`--'  `--'   `------'   `------'         `--'   `--' `--'  `--'    `-----'    
#--------------------------------------------------------------------------------------------------------------------


class settings: 
    def __init__(self, municipality_name = "Palatine", bbox_size = 5280, settings_file = "settings", input_geojson = "Municipality.geojson", target_crs = "EPSG:6455", url="https://gis.cookcountyil.gov/imagery/rest/services/CookOrtho2024/ImageServer/exportImage"):
        self.municipality_name = municipality_name
        self.bbox_size = bbox_size
        self.settings_file = settings_file
        self.input_geojson = input_geojson
        self.target_crs = target_crs
        self.url = url


    def runProgram(self):
        self.readSettings()
        try:
            settingsHuh = int(input("Enter 1 or 0 for settings: "))
            if settingsHuh == 1:
                self.startSettings()
        except ValueError:
            print("Invalid input. Please enter 1 or 0.")
            return
        print(f"{self.municipality_name}\n" )
        print(f"{self.bbox_size}\n" )
        print(f"{self.settings_file}\n" )
        print(f"{self.input_geojson}\n" )
        print(f"{self.target_crs}\n" )
        print(f"{self.url}\n" )    
        
        
        geojson_processor = GeoJSONFile(self.input_geojson, self.target_crs)
        tiles_manager = Tiles(
        geojson_processor=geojson_processor,
        url=self.url,
        bbox_size=self.bbox_size)
        
        geojson_processor.reproject()
        tiles_manager.download_tiles(self.municipality_name)
        

    def startSettings(self):
        doneHuh = False

        while not doneHuh:
            print("What setting to change?")
            print("1. Municipality")
            print("2. BBox size")
            print("3. Settings file")
            print("4. GeoJSON file")
            print("5. CRS")
            print("6. URL")
            print("7. Exit settings")

            try:
                chosenSetting = int(input("Enter the number of the setting to change: "))
            except ValueError:
                print("Invalid input. Please enter a number from 1 to 6.")
                continue

            if chosenSetting == 1:
                municipality_input = input("Enter the name of the city: ").title()
                self.municipality_name = municipality_input
            elif chosenSetting == 2:
                print("You chose to change BBox size.")
                try:
                    self.bbox_size = int(input("Enter the size for the bbox: "))
                except ValueError:
                    print("Invalid input. Please enter a number")
                    continue
            elif chosenSetting == 3:
                self.settings_file= input("Enter the new file name")
            elif chosenSetting == 4:
                print("You chose to change GeoJSON file.")
                self.input_geojson = input("Enter the new file name")
            elif chosenSetting == 5:
                self.target_crs = "EPSG:6455" + input("Enter the new CRS: ") 
            elif chosenSetting == 6:
                self.target_crs = input("Enter the new URL: ") 
            elif chosenSetting == 7:
                doneHuh = True
            else:
                print("Invalid choice. Please enter a number from 1 to 7.")
        else:
            doneHuh = True
        self.updateSettings()

    def updateSettings(self):
        with open(self.settings_file, "w") as f:
            f.write(f"Municipality: {self.municipality_name}\n")
            f.write(f"BBox Size: {self.bbox_size}\n")
            f.write(f"Settings File: {self.settings_file}\n")
            f.write(f"GeoJSON File: {self.input_geojson}\n")
            f.write(f"CRS: {self.target_crs}\n")
            f.write(f"URL: {self.url}\n")
            
            print("Saved")

        
    def readSettings(self):
        try:
            with open(self.settings_file, "r") as f:
                for line in f:
                    key, value = line.strip().split(": ", 1)  

                    if key == "Municipality":
                        self.municipality_name = value
                    elif key == "BBox Size":
                        self.bbox_size = int(value)  
                    elif key == "Settings File":
                        self.settings_file = value
                    elif key == "GeoJSON File":
                        self.input_geojson = value
                    elif key == "CRS":
                        self.target_crs = value  
                    elif key =="URL":
                        self.url = value



        except FileNotFoundError:
            print(f"Settings file '{self.settings_file}' not found. Using default settings.")
        except ValueError:
            print(f"Error reading settings file '{self.settings_file}'. Some values may be incorrect.")

            

settings().runProgram()



""" 

geojson_processor = GeoJSONFile(input_geojson, target_crs)
tiles_manager = Tiles(
    geojson_processor=geojson_processor,
    url="https://gis.cookcountyil.gov/imagery/rest/services/CookOrtho2024/ImageServer/exportImage",
    bbox_size=bbox_size
)


geojson_processor.reproject()
tiles_manager.download_tiles(municipality_name) """