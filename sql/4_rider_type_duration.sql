SELECT 
  member_casual,
  ROUND(AVG(TIMESTAMP_DIFF(ended_at, started_at, SECOND)) / 60, 2) AS avg_minutes
FROM `nyc-transit-data-platform.citibike_raw.citibike_trips`
GROUP BY member_casual;
