SELECT 
  start_station_name, 
  COUNT(*) AS trip_count
FROM `nyc-transit-data-platform.citibike_raw.citibike_trips`
GROUP BY start_station_name
ORDER BY trip_count DESC
LIMIT 10;