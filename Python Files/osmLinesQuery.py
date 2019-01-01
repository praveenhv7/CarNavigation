allIntersectingNodes = '''
                        select osm_id1,osm_id2,ST_AsText(ST_Transform(matchedpoint,4326)),(select ST_AsText(ST_Transform(way,4326)) from planet_osm_line where osm_id = insln.osm_id1) as wayOsmId1,(select ST_AsText(ST_Transform(way,4326)) from planet_osm_line where osm_id = insln.osm_id2) as wayOsmId2
                        from planet_osm_intersecting_lines insln;
                        '''




intersectionSQL = """
                    select * from (
                    select l1.osm_id1,l1.osm_id2,
                    ST_AsText(ST_Transform(l1.matchedpoint,4326)) AS "IntersectionPoint",   
                    ST_Distance(ST_Transform(l1.matchedPoint,3857),ST_Transform(ST_PointFromText(CONCAT('POINT(',%s,')'),4326),3857)) "Distace_To_Intersection",
                    degrees(st_azimuth(ST_PointFromText(CONCAT('POINT(',%s,')'),4326),ST_Transform(l1.matchedpoint,4326))) "Azimuth"
                    from planet_osm_intersecting_lines l1 ) as ins
                    where "Azimuth" >= %s
                    AND "Azimuth" <= %s
                    ORDER BY "Distace_To_Intersection" ASC LIMIT 8;
                      """

osmLineQuery = "select line.osm_id,line.highway,line.name,ST_AsText(ST_Transform(line.way, 4326)) " \
               "from planet_osm_line line where line.osm_id = %s;"

osmNextIntersection = """
                      select insTab.* from (
                            select osm_id1,osm_id2,ST_AsText(ST_Transform(matchedpoint,4326)),
                            degrees(st_azimuth(st_PointFromText(CONCAT('POINT(',%s,')'),4326),st_transform(l1.matchedpoint,4326)))
                            from planet_osm_intersecting_lines l1 
                            where osm_id1 = %s 
                            and osm_id2 != %s 
                            UNION
                            select osm_id2,osm_id1,ST_AsText(ST_Transform(matchedpoint,4326)),
                            degrees(st_azimuth(st_PointFromText(CONCAT('POINT(',%s,')'),4326),st_transform(l1.matchedpoint,4326)))
                            from planet_osm_intersecting_lines l1 
                            where osm_id1 != %s 
                            and osm_id2 = %s 
                            ) as insTab
                      """

markBothEndOfRoadsAsIntersection = """
                                select distinct osm_id,ST_AsText(ST_Transform(StartPoint,4326)),
											  ST_AsText(ST_Transform(endpoint,4326)) from (
                                    select  line.osm_id,iline.osm_id1,iline.osm_id2,
                                            ST_Transform(ST_StartPoint(line.way),4326) StartPoint,
                                            ST_Transform(ST_EndPoint(line.way),4326) EndPoint,
                                            ST_Equals(ST_Transform(ST_StartPoint(line.way),4326) , ST_Transform(iline.matchedpoint,4326)) as StartPointCovered,
                                            ST_Equals(ST_Transform(ST_EndPoint(line.way),4326) , ST_Transform(iline.matchedpoint,4326)) as EndPointCovered
                                            from planet_osm_line line, planet_osm_intersecting_lines iline  
                                            where line.osm_id in (iline.osm_id1,iline.osm_id2) ) tab
                                            WHERE startpointcovered = false
                                            AND endpointcovered = false
                                """

markStartOfRoadAsIntersection = """
                                select distinct osm_id,ST_AsText(ST_Transform(StartPoint,4326))
                                 from (
                                select  line.osm_id,iline.osm_id1,iline.osm_id2,
                                        ST_Transform(ST_StartPoint(line.way),4326) StartPoint,
                                        ST_Transform(ST_EndPoint(line.way),4326) EndPoint,
                                        ST_Equals(ST_Transform(ST_StartPoint(line.way),4326) , ST_Transform(iline.matchedpoint,4326)) as StartPointCovered,
                                        ST_Equals(ST_Transform(ST_EndPoint(line.way),4326) , ST_Transform(iline.matchedpoint,4326)) as EndPointCovered
                                        from planet_osm_line line, planet_osm_intersecting_lines iline  
                                        where line.osm_id in (iline.osm_id1,iline.osm_id2) ) tab
                                        WHERE startpointcovered = false
                                        AND endpointcovered = true
                            """

markEndOfRoadAsIntersection = """
                                select distinct osm_id,ST_AsText(ST_Transform(EndPoint,4326)) from (
                                    select  line.osm_id,iline.osm_id1,iline.osm_id2,
                                            ST_Transform(ST_StartPoint(line.way),4326) StartPoint,
                                            ST_Transform(ST_EndPoint(line.way),4326) EndPoint,
                                            ST_Equals(ST_Transform(ST_StartPoint(line.way),4326) , ST_Transform(iline.matchedpoint,4326)) as StartPointCovered,
                                            ST_Equals(ST_Transform(ST_EndPoint(line.way),4326) , ST_Transform(iline.matchedpoint,4326)) as EndPointCovered
                                            from planet_osm_line line, planet_osm_intersecting_lines iline  
                                            where line.osm_id in (iline.osm_id1,iline.osm_id2) ) tab
                                            WHERE startpointcovered = true
                                            AND endpointcovered = false;	
                            """

allOSMIdQuery = "select osm_id from planet_osm_line;"