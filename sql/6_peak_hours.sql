SELECT 
  EXTRACT(HOUR FROM started_at) AS hour,
  COUNT(*) AS trip_count
FROM `nyc-transit-data-platform.citibike_raw.citibike_trips`
GROUP BY hour
ORDER BY hour;