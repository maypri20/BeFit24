SELECT workout_type,
    ROUND(AVG(calories_burned / session_duration_hours), 2) AS avg_calories_per_hour,
    ROUND(AVG(max_bpm - resting_bpm), 2) AS avg_hr_range,
    ROUND(AVG((avg_bpm / max_bpm) * 100), 2) AS avg_intensity_pct,
    ROUND(AVG(calories_burned / avg_bpm), 2) AS avg_calories_per_bpm
FROM workout
WHERE session_duration_hours > 0 
GROUP BY workout_type
ORDER BY avg_calories_per_hour DESC;

SELECT w.workout_type,
    ROUND(AVG(w.calories_burned / w.session_duration_hours), 2) AS efficiency
FROM workout w
JOIN workout_to_user uw ON w.workout_id = uw.workout_id
WHERE uw.user_id = 60
  AND w.session_duration_hours > 0  
GROUP BY w.workout_type
ORDER BY efficiency DESC;

SELECT u.user_id, SUM(m.protein) AS total_protein,
    SUM(m.carbs) AS total_carbs,
    SUM(m.fats) AS total_fat,
    SUM(m.calories) AS total_calories
FROM meal m JOIN meal_to_user u ON m.meal_id = u.meal_id
GROUP BY u.user_id;

SELECT meal_type, SUM(protein) AS total_protein, SUM(carbs) AS total_carbs, SUM(fats) AS total_fat, SUM(calories) AS total_calories
FROM meal GROUP BY meal_type;

SELECT diet_type, SUM(protein) AS total_protein, SUM(carbs) AS total_carbs, SUM(fats) AS total_fat, SUM(calories) AS total_calories
FROM meal GROUP BY diet_type;

SELECT u.gender, w.workout_type, COUNT(*) AS workout_count from user u join workout_to_user wu ON u.user_id = wu.user_id
JOIN workout w ON w.workout_id = wu.user_id
GROUP BY u.gender, w.workout_type
ORDER BY u.gender, workout_count DESC;

SELECT gender, count(*) from user
group by gender;

SELECT u.gender, m.diet_type, COUNT(*) AS diet_type from user u join meal_to_user mu ON u.user_id = mu.user_id
JOIN meal m ON m.meal_id = mu.user_id
GROUP BY u.gender, m.diet_type
ORDER BY u.gender, diet_type DESC;

select weight_kg, COUNT(*) AS user_count from user
group by weight_kg
order by weight_kg;