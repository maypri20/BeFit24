import streamlit as st
import pandas as pd
import numpy as np
import yaml
import gower

try:
    with open("../config.yaml", "r") as file:
        config = yaml.safe_load(file)
except:
    st.error("⚠️ Yaml configuration file not found!")

df = pd.read_csv(config['output_data']['file'])

def body_composition_dashboard(df):
    st.title("💪 FitTrack360 — Body Composition & Fitness Analyzer")

    st.write("Calculate your body composition and discover your closest fitness matches from the dataset for personalized insights.")

    # --- User Inputs ---
    col1, col2 = st.columns(2)
    with col1:
        gender = st.selectbox("Select Gender", ["Male", "Female"])
        age = st.slider("Age (years)", min_value=18, max_value=59, value=30, step=1)
        workout_type = st.selectbox("Workout Type", ["Cardio", "Strength", "Yoga", "Hiit"])
    with col2:
        height_m = st.slider("Height (m)", min_value=1.49, max_value=2.01, value=1.70, step=0.01)
        weight_kg = st.slider("Weight (kg)", min_value=39, max_value=130, value=70, step=1)
        diet_type = st.selectbox("Diet Type", ["Balanced", "Keto", "Low-Carb", "Paleo"])

    st.divider()

    # --- Gower Distance Similarity (Top 3 Neighbors) ---
    cols_for_match = [
        "gender", "age", "height_m", "weight_kg",
        "diet_type", "workout_type", "avg_bpm",
        "calories_burned", "water_intake_liters"
    ]

    # Drop missing columns if any are absent in df
    cols_for_match = [c for c in cols_for_match if c in df.columns]

    # Build input record
    input_data = pd.DataFrame([{
        "gender": gender.title(),
        "age": age,
        "height_m": height_m,
        "weight_kg": weight_kg,
        "diet_type": diet_type.title(),
        "workout_type": workout_type.title(),
        "avg_bpm": 140,
        "calories_burned": 400,
        "water_intake_liters": 2.5
    }])

    df_subset = df[cols_for_match].dropna().copy()

    gower_distances = gower.gower_matrix(df_subset, input_data)
    gower_flat = gower_distances.flatten()

    # --- Get Top 3 Most Similar Profiles ---
    top_k = 3
    topk_idx = np.argsort(gower_flat)[:top_k]
    matched_rows = df.iloc[topk_idx]
    matched_row = matched_rows.mean(numeric_only=True)  # numeric average for stability

    st.info(
        f"**Top {top_k} similar profiles found!** "
        f"Closest age: {matched_rows.iloc[0]['age']}, "
        f"Height: {matched_rows.iloc[0]['height_m']} m, "
        f"Weight: {matched_rows.iloc[0]['weight_kg']} kg"
    )

    # --- Derived Metrics (Core) ---
    bmi = weight_kg / (height_m ** 2)
    gender_factor = 1 if gender.lower() == "male" else 0
    body_fat_percentage = (1.20 * bmi) + (0.23 * age) - (10.8 * gender_factor) - 5.4
    fat_mass_kg = weight_kg * (body_fat_percentage / 100)
    lean_mass_kg = weight_kg - fat_mass_kg
    muscle_to_fat_ratio = round(lean_mass_kg / fat_mass_kg, 2) if fat_mass_kg > 0 else None

    # --- Derived Metrics (Advanced) ---
    calories = matched_row.get("calories", 0)
    calories_burned = matched_row.get("calories_burned", 0)
    proteins = matched_row.get("proteins", 0)
    carbs = matched_row.get("carbs", 0)
    fats = matched_row.get("fats", 0)
    session_duration_hours = matched_row.get("session_duration_hours", 1)
    water_intake_liters = matched_row.get("water_intake_liters", 2)
    max_bpm = matched_row.get("max_bpm", 180)
    avg_bpm = matched_row.get("avg_bpm", 140)
    resting_bpm = matched_row.get("resting_bpm", 70)

    total_calories = (carbs * 4) + (proteins * 4) + (fats * 9)
    pct_carbs = (carbs * 4 / total_calories) * 100 if total_calories > 0 else 0
    protein_per_kg = proteins / weight_kg if weight_kg > 0 else 0
    cal_balance = calories - calories_burned
    workout_efficiency = calories_burned / session_duration_hours if session_duration_hours > 0 else 0
    hr_reserve = max_bpm - resting_bpm
    cardio_load = (avg_bpm / max_bpm) * 100 if max_bpm > 0 else 0
    hydration_score = water_intake_liters / (weight_kg * 0.033)
    nutrition_quality = (0.4 * protein_per_kg) + (0.3 * (100 - abs(pct_carbs - 50)) / 100) + (0.3 * hydration_score)
    fitness_score = (0.3 * workout_efficiency / 500) + (0.3 * nutrition_quality) + (0.4 * (lean_mass_kg / weight_kg))
    fitness_score = round(fitness_score * 100, 1)

    # --- BMI Classification ---
    if bmi < 18.5:
        bmi_category = "Underweight"; bmi_reco = "Increase calorie intake and focus on nutrient-rich foods."; bmi_color = "orange"
    elif 18.5 <= bmi < 25:
        bmi_category = "Normal weight"; bmi_reco = "Maintain your current healthy habits."; bmi_color = "green"
    elif 25 <= bmi < 30:
        bmi_category = "Overweight"; bmi_reco = "Increase activity levels and moderate calorie intake."; bmi_color = "orange"
    elif 30 <= bmi < 40:
        bmi_category = "Obese"; bmi_reco = "Adopt a structured exercise and diet plan."; bmi_color = "red"
    else:
        bmi_category = "Severely Obese"; bmi_reco = "Seek professional medical guidance."; bmi_color = "darkred"

    # --- Body Fat % Classification ---
    if gender.lower() == "male":
        if body_fat_percentage < 6: fat_category = "Essential Fat"
        elif 6 <= body_fat_percentage < 14: fat_category = "Athlete"
        elif 14 <= body_fat_percentage < 18: fat_category = "Fit"
        elif 18 <= body_fat_percentage < 25: fat_category = "Average"
        else: fat_category = "Obese"
    else:
        if body_fat_percentage < 14: fat_category = "Essential Fat"
        elif 14 <= body_fat_percentage < 21: fat_category = "Athlete"
        elif 21 <= body_fat_percentage < 25: fat_category = "Fit"
        elif 25 <= body_fat_percentage < 32: fat_category = "Average"
        else: fat_category = "Obese"

    # --- Summary ---
    if bmi_category == "Normal weight" and fat_category in ["Fit", "Athlete"]:
        summary = "Excellent shape! Keep maintaining a balanced lifestyle."
    elif bmi_category == "Overweight" and fat_category in ["Average", "Obese"]:
        summary = "Moderate excess — increase activity and portion control."
    elif bmi_category in ["Obese", "Severely Obese"]:
        summary = "High body composition risk — start a sustainable calorie deficit and stay active."
    elif bmi_category == "Underweight":
        summary = "Low BMI — increase muscle mass with resistance training and higher protein intake."
    else:
        summary = "You're close to a healthy range — maintain balanced nutrition and regular exercise."

    # --- Display Results ---
    st.subheader("🧬 Derived Body Composition Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("BMI", f"{bmi:.2f}", f"{bmi_category}", delta_color="off")
    with col2:
        st.metric("Body Fat %", f"{body_fat_percentage:.2f}", f"{fat_category}", delta_color="off")
    with col3:
        st.metric("Lean Mass (kg)", f"{lean_mass_kg:.2f}")

    st.subheader("⚡ Advanced Fitness & Nutrition Metrics")
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("Protein per kg", f"{protein_per_kg:.2f} g/kg")
        st.metric("Workout Efficiency", f"{workout_efficiency:.0f} kcal/hr")
    with col5:
        st.metric("Carb Ratio (%)", f"{pct_carbs:.1f}%")
        st.metric("Calorie Balance", f"{cal_balance:.0f} kcal")
    with col6:
        st.metric("Hydration Score", f"{hydration_score:.2f}")
        st.metric("Heart Rate Reserve", f"{hr_reserve} bpm")

    st.subheader("🏆 Overall Fitness Indicator")
    st.progress(min(fitness_score / 100, 1.0))
    st.metric("Fitness Score", f"{fitness_score:.1f}/100")

    # --- Recommendations ---
    st.markdown("### 🩺 **Personalized Recommendations:**")
    st.markdown(f"**BMI Insight:** <span style='color:{bmi_color}'>{bmi_reco}</span>", unsafe_allow_html=True)
    st.markdown(f"**Body Fat Insight:** {fat_category} — Maintain or adjust as needed.")
    st.success(f"**Summary:** {summary}")

    # Additional health nudges
    if hydration_score < 0.8:
        st.warning("💧 You may be under-hydrated. Aim for ~35 ml water per kg body weight daily.")
    if protein_per_kg < 1.2:
        st.info("🥚 Increase protein intake to support muscle recovery.")
    if cal_balance < -300:
        st.info("⚖️ You're in a calorie deficit — good for fat loss if intentional.")
    elif cal_balance > 300:
        st.info("🍽️ Calorie surplus detected — could aid muscle gain or cause fat gain.")

# --- Run this app ---
if __name__ == "__main__":
    body_composition_dashboard(df)
