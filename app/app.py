import streamlit as st
import pandas as pd
import numpy as np
import yaml

try:
    with open("../config.yaml", "r") as file:
        config = yaml.safe_load(file)
except:
    print("Yaml configuration file not found!")

df = pd.read_csv(config['output_data']['file'])

def body_composition_dashboard(df):
    st.title(" FitTrack360 — Body Composition Analyzer")

    st.write("Use this tool to calculate your BMI, Body Fat %, Lean Mass, and personalized health insights based on your details and dataset trends.")

    # --- User Inputs ---
    col1, col2 = st.columns(2)
    with col1:
        gender = st.selectbox("Select Gender", ["Male", "Female"])
        age = st.slider("Age (years)", min_value=18, max_value=59, value=30, step=1)
    with col2:
        height_m = st.slider("Height (m)", min_value=1.49, max_value=2.01, value=1.70, step=0.01)
        weight_kg = st.slider("Weight (kg)", min_value=39, max_value=130, value=70, step=1)

    st.divider()

    # --- Find Closest Match from Dataset ---
    df_gender = df[df['gender'].str.title() == gender].copy()
    df_gender["total_diff"] = (
        abs(df_gender["age"] - age)
        + abs(df_gender["height_m"] - height_m)
        + (abs(df_gender["weight_kg"] - weight_kg) / 10)
    )

    match = df_gender.nsmallest(1, "total_diff")
    matched_row = match.iloc[0]

    st.info(f"**Closest dataset match:** Age {matched_row['age']}, Height {matched_row['height_m']} m, Weight {matched_row['weight_kg']} kg")

    # --- Calculations ---
    bmi = weight_kg / (height_m ** 2)
    gender_factor = 1 if gender.lower() == "male" else 0
    body_fat_percentage = (1.20 * bmi) + (0.23 * age) - (10.8 * gender_factor) - 5.4
    fat_mass_kg = weight_kg * (body_fat_percentage / 100)
    lean_mass_kg = weight_kg - fat_mass_kg
    muscle_to_fat_ratio = round(lean_mass_kg / fat_mass_kg, 2) if fat_mass_kg > 0 else None

    # --- BMI Classification ---
    if bmi < 18.5:
        bmi_category = "Underweight"
        bmi_reco = "Increase calorie intake and focus on nutrient-rich foods."
        bmi_color = "orange"
    elif 18.5 <= bmi < 25:
        bmi_category = "Normal weight"
        bmi_reco = "Maintain current lifestyle with balanced diet and exercise."
        bmi_color = "green"
    elif 25 <= bmi < 30:
        bmi_category = "Overweight"
        bmi_reco = "Increase activity levels and moderate calorie intake."
        bmi_color = "orange"
    elif 30 <= bmi < 40:
        bmi_category = "Obese"
        bmi_reco = "Follow a structured diet and regular exercise; consider medical advice."
        bmi_color = "red"
    else:
        bmi_category = "Severely Obese"
        bmi_reco = "Seek professional medical guidance for supervised weight management."
        bmi_color = "darkred"

    # --- Body Fat % Classification ---
    if gender.lower() == "male":
        if body_fat_percentage < 6:
            fat_category = "Essential Fat"
        elif 6 <= body_fat_percentage < 14:
            fat_category = "Athlete"
        elif 14 <= body_fat_percentage < 18:
            fat_category = "Fit"
        elif 18 <= body_fat_percentage < 25:
            fat_category = "Average"
        else:
            fat_category = "Obese"
    else:
        if body_fat_percentage < 14:
            fat_category = "Essential Fat"
        elif 14 <= body_fat_percentage < 21:
            fat_category = "Athlete"
        elif 21 <= body_fat_percentage < 25:
            fat_category = "Fit"
        elif 25 <= body_fat_percentage < 32:
            fat_category = "Average"
        else:
            fat_category = "Obese"

    # --- Personalized Summary ---
    if bmi_category == "Normal weight" and fat_category in ["Fit", "Athlete"]:
        summary = "You are in excellent shape! Maintain a balanced diet and regular workouts."
    elif bmi_category == "Overweight" and fat_category in ["Average", "Obese"]:
        summary = "You have moderate excess — focus on consistent exercise and portion control."
    elif bmi_category in ["Obese", "Severely Obese"]:
        summary = "Your metrics suggest obesity — adopt a calorie deficit, increase activity, and seek professional support."
    elif bmi_category == "Underweight":
        summary = "Low BMI — aim to increase muscle mass with resistance training and higher protein intake."
    else:
        summary = "You're close to a healthy range — prioritize balanced nutrition and strength training."

    # --- Display Results ---
    st.subheader("Derived Body Composition Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("BMI", f"{bmi:.2f}", f"{bmi_category}", delta_color="off")
    with col2:
        st.metric("Body Fat %", f"{body_fat_percentage:.2f}", f"{fat_category}", delta_color="off")
    with col3:
        st.metric("Lean Mass (kg)", f"{lean_mass_kg:.2f}")

    col4, col5 = st.columns(2)
    with col4:
        st.metric("Muscle-to-Fat Ratio", f"{muscle_to_fat_ratio}")
    with col5:
        st.metric("Fat Mass (kg)", f"{fat_mass_kg:.2f}")

    st.markdown(f"###  **Personalized Recommendation:**")
    st.markdown(f"**BMI Insight:** <span style='color:{bmi_color}'>{bmi_reco}</span><br>", unsafe_allow_html=True)
    st.markdown(f"**Body Fat Insight:** {fat_category} — Maintain or adjust as needed.")
    st.success(f"**Summary:** {summary}")


# --- Run this app ---
# Example: streamlit run fittrack360_body_composition.py
# Ensure df is loaded before running the function
# body_composition_dashboard(df)
if __name__ == "__main__":
    body_composition_dashboard(df)