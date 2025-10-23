SELECT 
    workout_type,
    ROUND(AVG(calories_burned / session_duration_hours), 2) AS avg_calories_per_hour,
    ROUND(AVG(max_bpm - resting_bpm), 2) AS avg_hr_range,
    ROUND(AVG((avg_bpm / max_bpm) * 100), 2) AS avg_intensity_pct,
    ROUND(AVG(calories_burned / avg_bpm), 2) AS avg_calories_per_bpm
FROM workout
WHERE session_duration_hours > 0   -- avoid division by zero
GROUP BY workout_type
ORDER BY avg_calories_per_hour DESC;

SELECT 
    w.workout_type,
    ROUND(AVG(w.calories_burned / w.session_duration_hours), 2) AS efficiency
FROM workout w
JOIN workout_to_user uw ON w.workout_id = uw.workout_id
WHERE uw.user_id = 60
  AND w.session_duration_hours > 0   -- avoid division by zero
GROUP BY w.workout_type
ORDER BY efficiency DESC;
