# CarNavigation
Car Navigation using Compass and OSM data.
Install OSM2PGSQL this helps to extract XML data and store it in gis database.
Install Kartograph this uses the GIS database to create a SVG file more information on kartograph can be found here (http://kartograph.org/)
Once the installation is complete download the map from open street maps using export option.
Run SQL scripts to create objects, tables and functions in postgres.
Load the downloaded map using OSM2PGSQL.
Run createIntersectingLines to create intersections of roads.
Run find routeV2 by providing the stable readings of compass.
To improve accuraccy you can also run markroadends.py which creates intersection points for road ends.
PPT available in the REPO.
