# CarNavigation
Car Navigation using Compass and OSM data.
1. Install OSM2PGSQL this helps to extract XML data and store it in gis database.
2. Install Kartograph this uses the GIS database to create a SVG file more information on kartograph can be found here         (http://kartograph.org/)
3. Once the installation is complete download the map from open street maps using export option.
4. Run SQL scripts to create objects, tables and functions in postgres.
5. Load the downloaded map using OSM2PGSQL.
6. Run createIntersectingLines to create intersections of roads.
7. Run find routeV2 by providing the stable readings of compass.
8. To improve accuraccy you can also run markroadends.py which creates intersection points for road ends.
PPT available in the REPO.
