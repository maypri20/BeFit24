CREATE DATABASE fitness;
USE fitness;

CREATE TABLE `user`(
    `user_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `age` BIGINT NOT NULL,
    `gender` VARCHAR(255) NOT NULL,
    `weight_kg` BIGINT NOT NULL,
    `height_m` FLOAT(53) NOT NULL,
    `bmi` FLOAT(53) NOT NULL,
    `fat_percentage` FLOAT(53) NOT NULL,
    `lean_mass_kg` FLOAT(53) NOT NULL
);
CREATE TABLE `workout`(
    `workout_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `max_bpm` FLOAT(53) NOT NULL,
    `avg_bpm` FLOAT(53) NOT NULL,
    `resting_bpm` FLOAT(53) NOT NULL,
    `session_duration_hours` FLOAT(53) NOT NULL,
    `calories_burned` FLOAT(53) NOT NULL,
    `workout_type` VARCHAR(255) NOT NULL,
    `cal_balance` FLOAT(53) NOT NULL
);
CREATE TABLE `meal`(
    `meal_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `carbs` FLOAT(53) NOT NULL,
    `protein` FLOAT(53) NOT NULL,
    `fats` FLOAT(53) NOT NULL,
    `calories` FLOAT(53) NOT NULL,
    `meal_type` VARCHAR(255) NOT NULL,
    `diet_type` VARCHAR(255) NOT NULL,
    `pct_carbs` FLOAT(53) NOT NULL,
    `protein_per_kg` FLOAT(53) NOT NULL,
    `water_intake_liters` BIGINT NOT NULL
);
CREATE TABLE `meal_to_user`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
     user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
     meal_id INT REFERENCES meals(meal_id) ON DELETE CASCADE
);
CREATE TABLE `workout_to_user`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    workout_id INT REFERENCES workouts(workout_id) ON DELETE CASCADE
);

ALTER TABLE user 
ADD COLUMN height_cm INT;

UPDATE user
SET height_cm = ROUND(height_m * 100);

UPDATE user
SET height_cm = ROUND(height_m * 100)
WHERE user_id > 0;

SELECT user_id, height_m, height_cm
FROM user
LIMIT 10;

ALTER TABLE user DROP COLUMN height_m;


