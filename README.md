# CarNavigation
Car Navigation using Compass and OSM data.
1. Requires Kartograph along with gis database on postgres more information on kartograph can be found here (http://kartograph.org/)
2. Once the installation is complete download the map from open street maps using export option.
3. Run SQL scripts to create objects, tables and functions in postgres.
4. Load the downloaded map using osm2pgsql.
5. Run createIntersectingLines to create intersections of roads.
6. Run find routeV2 by provind the stable readings of compass.
