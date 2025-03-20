Hi viewer! This is a simple progam I wrote that interacts with arcgis restful services.
Some services on arcgis make it difficult to customize data in the way that I wantted. 
In this case I need to grab tiled sattleite imagery hosted by different municaplities in the US,
but only by a given municapalties boundaries (like if I have imagery of Cook County in IL, I only want images of Chicago). 
This program is highly custimizable so that you can change what image servers you get data from, and what kinda of data you get like image size (which contributes to the number of tiles). 
Arcgis doesn't directly have a way to download tiled images so I had to write a program that piece by piece downloads imagery by navigating the boundaries of a municipality. 
