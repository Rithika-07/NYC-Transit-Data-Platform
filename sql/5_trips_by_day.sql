SELECT 
  FORMAT_TIMESTAMP('%A', started_at) AS day_of_week,
  COUNT(*) AS trip_count
FROM `nyc-transit-data-platform.citibike_raw.citibike_trips`
GROUP BY day_of_week
ORDER BY trip_count DESC;