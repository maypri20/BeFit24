import streamlit as st
import pandas as pd
import numpy as np
import yaml
import gower
import plotly.express as px
import plotly.graph_objects as go

# =========================
# Load your config + dataset
# =========================
try:
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    df = pd.read_csv(config['output_data']['file'])
except Exception as e:
    st.error(f"Error loading data/config: {e}")
    st.stop()

# =========================
# Streamlit Page Config
# =========================
st.set_page_config(
    page_title="BeFit24 - Nutrition & Fitness journey",
    page_icon="figures/image.png",
    layout="wide"
)
col1, col2 = st.columns([1, 4])

with col1:
    st.image("figures/image.png", width=120) 

with col2:
    st.markdown("""
        <div style='padding-top: 10px;'>
            <h1 style='margin-bottom:0; color:#3963d5;'>BeFit24  </h1>
            <h4 style='margin-top:5px; color:#d55339;'>Nutrition & Fitness journey</h4>
            <p style='font-size:16px; color:#444;'>Body Composition & Personalized Recommendations</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---") 

#st.title(" ")
#st.caption("")

# =========================
# Sidebar — User Inputs
# =========================
st.sidebar.header("Your Profile Input")

# --- Body & Workout Info ---
st.sidebar.subheader("Body Metrics")
gender = st.sidebar.selectbox("Gender", ["Male", "Female"])
age = st.sidebar.slider("Age (years)", min_value=16, max_value=80, value=35)
height_m = st.sidebar.slider("Height (m)", min_value=1.3, max_value=2.1, value=1.80, step=0.01)
weight_kg = st.sidebar.slider("Weight (kg)", min_value=39.0, max_value=130.0, value=78.0, step=0.1)

st.sidebar.subheader("Workout Details")
workout_type = st.sidebar.selectbox("Workout Type", ["Cardio", "Hiit", "Strength", "Yoga"])
avg_bpm = st.sidebar.slider("Average Workout BPM", min_value=80, max_value=200, value=140, step=1)
calories_burned = st.sidebar.slider("Calories Burned per Session (kcal)", min_value=100, max_value=3000, value=800, step=10)

st.sidebar.subheader("Hydration")
water_intake_liters = st.sidebar.slider("Water Intake (L/day)", min_value=1.0, max_value=4.0, value=2.0, step=0.1)

# --- Nutrition Info ---
st.sidebar.subheader("Nutrition Intake (per day)")
diet_type = st.sidebar.selectbox("Diet Type", ["Balanced", "Keto", "Low-Carb", "Paleo", "Vegan", "Vegetarian"])
proteins = st.sidebar.slider("Protein (g)", min_value=20, max_value=200, value=80, step=5)
carbs = st.sidebar.slider("Carbohydrates (g)", min_value=50, max_value=500, value=250, step=10)
fats = st.sidebar.slider("Fats (g)", min_value=10, max_value=150, value=60, step=5)

# derived calories
calories_intake = (proteins * 4) + (carbs * 4) + (fats * 9)
st.sidebar.write(f"**Total Calories: {calories_intake:.0f} kcal**")

st.sidebar.subheader("Fitness Goal")
goal = st.sidebar.selectbox(
    "What is your current goal?",
    ["Maintain Weight", "Lose Weight", "Build Muscle", "Improve Endurance", "General Fitness"]
)

run_button = st.sidebar.button("Run Analysis")

# =========================
# Main Functionality
# =========================
def analyze_body_composition(df,gender, age, height_m, weight_kg, diet_type,
                             workout_type, avg_bpm, calories_burned, water_intake_liters,calories_intake, proteins, carbs, fats, goal):
    cols_for_match = [
        "gender", "age", "height_m", "weight_kg",
        "diet_type", "workout_type", "avg_bpm",
        "calories_burned", "water_intake_liters"
    ]
    cols_for_match = [c for c in cols_for_match if c in df.columns]

    input_data = pd.DataFrame([{
        "gender": gender,
        "age": age,
        "height_m": height_m,
        "weight_kg": weight_kg,
        "diet_type": diet_type,
        "workout_type": workout_type,
        "avg_bpm": avg_bpm,
        "calories_burned": calories_burned,
        "water_intake_liters": water_intake_liters
    }])

    df_subset = df[cols_for_match].dropna().copy()

    # --- Gower Distance Similarity (Top 3 Neighbors) ---
    gower_distances = gower.gower_matrix(df_subset, input_data)
    gower_flat = gower_distances.flatten()

    top_k = 3
    topk_idx = np.argsort(gower_flat)[:top_k]
    matched_rows = df.iloc[topk_idx]
    matched_row = matched_rows.mean(numeric_only=True)


    # Prepare comparison dataframe
    comparison_df = matched_rows[["age", "height_m", "weight_kg", "calories_burned", "avg_bpm","calories", "proteins", "carbs", "fats"
                                 ]].copy()

# Add user's own data as a row
    user_data = {
        "age": age,
        "height_m": height_m,
        "weight_kg": weight_kg,
        "calories_burned": calories_burned,
        "avg_bpm": avg_bpm,
        "calories": calories_intake,
        "proteins": proteins,
        "carbs": carbs,
        "fats": fats}
    comparison_df = pd.concat([comparison_df, pd.DataFrame([user_data])], ignore_index=True)
    comparison_df["Profile"] = ["Profile 1", "Profile 2", "Profile 3", "You"]

    # --- Derived Metrics ---
    bmi = weight_kg / (height_m ** 2)
    gender_factor = 1 if gender.lower() == "male" else 0
    body_fat_percentage = (1.20 * bmi) + (0.23 * age) - (10.8 * gender_factor) - 5.4
    fat_mass_kg = weight_kg * (body_fat_percentage / 100)
    lean_mass_kg = weight_kg - fat_mass_kg

    calories = matched_row.get("calories", 0)
    calories_burned = matched_row.get("calories_burned", calories_burned)
    proteins = matched_row.get("proteins", 0)
    carbs = matched_row.get("carbs", 0)
    fats = matched_row.get("fats", 0)
    session_duration_hours = matched_row.get("session_duration_hours", 1)
    water_intake_liters = matched_row.get("water_intake_liters", water_intake_liters)
    max_bpm = matched_row.get("max_bpm", 180)
    avg_bpm = matched_row.get("avg_bpm", avg_bpm)
    resting_bpm = matched_row.get("resting_bpm", 70)

    total_calories = (carbs * 4) + (proteins * 4) + (fats * 9)
    pct_carbs = (carbs * 4 / total_calories) * 100 if total_calories > 0 else 0
    protein_per_kg = proteins / weight_kg if weight_kg > 0 else 0
    cal_balance = calories - calories_burned
    workout_efficiency = calories_burned / session_duration_hours if session_duration_hours > 0 else 0
    hydration_score = water_intake_liters / (weight_kg * 0.033)
    nutrition_quality = (0.4 * protein_per_kg) + (0.3 * (100 - abs(pct_carbs - 50)) / 100) + (0.3 * hydration_score)

    # --- Classification ---
    if bmi < 18.5:
        bmi_category = "Underweight"
        bmi_reco = "Increase calorie intake and focus on nutrient-rich foods."
    elif bmi < 25:
        bmi_category = "Normal weight"
        bmi_reco = "Maintain your current healthy habits."
    elif bmi < 30:
        bmi_category = "Overweight"
        bmi_reco = "Increase activity and moderate calories."
    elif bmi < 40:
        bmi_category = "Obese"
        bmi_reco = "Adopt a structured exercise and diet plan."
    else:
        bmi_category = "Severely Obese"
        bmi_reco = "Seek professional medical guidance."

    if gender.lower() == "male":
        if body_fat_percentage < 6: fat_category = "Essential Fat"
        elif body_fat_percentage < 14: fat_category = "Athlete"
        elif body_fat_percentage < 18: fat_category = "Fit"
        elif body_fat_percentage < 25: fat_category = "Average"
        else: fat_category = "Obese"
    else:
        if body_fat_percentage < 14: fat_category = "Essential Fat"
        elif body_fat_percentage < 21: fat_category = "Athlete"
        elif body_fat_percentage < 25: fat_category = "Fit"
        elif body_fat_percentage < 32: fat_category = "Average"
        else: fat_category = "Obese"

    return {
        "matched_rows": matched_rows,"comparison_df": comparison_df,
        "bmi": bmi,
        "bmi_category": bmi_category,
        "bmi_reco": bmi_reco,
        "body_fat_percentage": body_fat_percentage,
        "fat_category": fat_category,
        "lean_mass_kg": lean_mass_kg,
        "protein_per_kg": protein_per_kg,
        "cal_balance": cal_balance,
        "workout_efficiency": workout_efficiency,
        "hydration_score": hydration_score,
        "nutrition_quality": nutrition_quality
    }

# =========================
# Display Dashboard
# =========================
if run_button:
    results = analyze_body_composition(
        df, gender, age, height_m, weight_kg, diet_type, workout_type,
        avg_bpm, calories_burned, water_intake_liters,
        calories_intake, proteins, carbs, fats, goal
    )
    matched_rows = results["matched_rows"]
    comparison_df = results["comparison_df"]

    #st.subheader("Top 3 Similar Profiles (Gower Similarity)")
    #st.dataframe(matched_rows[["age", "height_m", "weight_kg", "diet_type", "workout_type"]])

    # KPI Cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("BMI", f"{results['bmi']:.2f}", results['bmi_category'])
    c2.metric("Body Fat %", f"{results['body_fat_percentage']:.2f}", results['fat_category'])
    c3.metric("Protein / kg", f"{results['protein_per_kg']:.2f}")
    c4.metric("Workout Efficiency", f"{results['workout_efficiency']:.0f} kcal/hr")

    c5, c6, c7, _ = st.columns(4)
    c5.metric("Hydration Score", f"{results['hydration_score']:.2f}")
    c6.metric("Calorie Balance", f"{results['cal_balance']:.0f} kcal")
    c7.metric("Nutrition Quality", f"{results['nutrition_quality']:.2f}")

    # =========================
    # 📊 Comparison with Similar Profiles
    # =========================
    st.markdown("---")
    st.markdown("### Comparison with Similar Profiles")

    col1, col2 = st.columns(2)

    with col1:
        # --- 1️⃣ Calorie Balance Chart ---
        comparison_df["Calorie Balance"] = comparison_df["calories"] - comparison_df["calories_burned"]
        comparison_df["Calorie Status"] = comparison_df["Calorie Balance"].apply(lambda x: "Surplus" if x >= 0 else "Deficit")

            
        fig1 = px.bar(
            comparison_df,
            x="Calorie Balance",
            y="Profile",
            orientation="h",
            color="Calorie Balance",
            color_continuous_scale= ["#3963d5", "#d55339"],
            title="Calorie Balance"
        )
        st.plotly_chart(fig1, use_container_width=True)


    with col2:
        # --- 2️⃣ Horizontal Bar Chart: Core Fitness & Nutrition Metrics ---
        core_metrics = pd.DataFrame({
            "Metric": ["BMI", "Body Fat %", "Protein/kg", "Hydration", "Nutrition Quality"],
            "You": [
                results["bmi"], results["body_fat_percentage"], results["protein_per_kg"],
                results["hydration_score"], results["nutrition_quality"]
            ],
            "Profile's Avg": [
                (matched_rows["weight_kg"].mean() / (matched_rows["height_m"].mean() ** 2)),
                results["body_fat_percentage"],
                (matched_rows["proteins"].mean() / matched_rows["weight_kg"].mean()),
                matched_rows["water_intake_liters"].mean() / (matched_rows["weight_kg"].mean() * 0.033),
                results["nutrition_quality"]
            ]
        })

        fig2 = px.bar(
            core_metrics,
            x=["You", "Profile's Avg"],
            y="Metric",
            barmode="group",
            orientation="h",
            title="Core Fitness & Nutrition Metrics",
            labels={"value": "Score", "Metric": "Metric"},
            color_discrete_sequence=["#3963d5", "#d55339"]
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ---- SECOND ROW ----
    col3, col4 = st.columns(2)

    with col3:
        # --- 3️⃣ Pie Chart for Workout Efficiency Comparison ---
        workout_eff_df = pd.DataFrame({
            "Profile": ["You", "Profile's Avg"],
            "Workout Efficiency (kcal/hr)": [results["workout_efficiency"], matched_rows["calories_burned"].mean()]
        })

        fig3 = px.pie(
            workout_eff_df,
            names="Profile",
            values="Workout Efficiency (kcal/hr)",
            hole=0.4,
            title="Workout Efficiency Distribution",
            color="Profile",
            color_discrete_sequence=["#3963d5", "#d55339"]
        )
        fig3.update_traces(textinfo="percent+label", pull=[0.05, 0])
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        # --- 4️⃣ Donut Chart: Macronutrient Distribution ---
        macros = pd.DataFrame({
            "Nutrient": ["Protein", "Carbs", "Fats"],
            "Grams": [proteins, carbs, fats],
            "Calories": [proteins * 4, carbs * 4, fats * 9]
        })

        total_cals = macros["Calories"].sum()
        macros["% of Calories"] = (macros["Calories"] / total_cals) * 100

        fig4 = px.pie(
            macros,
            values="% of Calories",
            names="Nutrient",
            hole=0.5,
            title="Macronutrient Distribution (% of Total Calories)",
            color_discrete_sequence=["#3963d5", "#d55339", "#f8961e"]  #"#0077b6", "#90be6d", "#f8961e"
        )
        fig4.update_traces(textinfo="percent+label", pull=[0.05, 0, 0])
        st.plotly_chart(fig4, use_container_width=True)

    # =========================
    # Recommendations
    # =========================
    st.subheader(f" Personalized Recommendations for Your Goal: *{goal}*")

    recs = []

    # --- Goal-Specific Recommendations ---
    if goal == "Lose Weight":
        if results["cal_balance"] > 0:
            recs.append(" Create a calorie deficit — burn more than you consume.")
        if results["protein_per_kg"] < 1.5:
            recs.append(" Increase protein to preserve lean mass while cutting.")
        if results["hydration_score"] < 1:
            recs.append(" Stay hydrated to aid metabolism and reduce fatigue.")
        recs.append(" Add 30–45 mins brisk walking or cardio 5x/week.")

    elif goal == "Build Muscle":
        if results["cal_balance"] < 200:
            recs.append("Slight calorie surplus helps muscle growth (200–300 kcal/day).")
        if results["protein_per_kg"] < 1.8:
            recs.append(" Boost protein intake to at least 1.8g/kg for hypertrophy.")
        recs.append(" Focus on progressive overload strength training (3–5x/week).")

    elif goal == "Maintain Weight":
        recs.append(" Aim for a calorie balance near zero — steady intake & output.")
        recs.append(" Keep macros balanced (~50% carbs, 25% protein, 25% fats).")
        recs.append(" Maintain regular activity to stabilize body composition.")

    elif goal == "Improve Endurance":
        recs.append(" Incorporate moderate-intensity cardio 4–5 days/week.")
        recs.append(" Maintain carbs at 50–60% of total calories for energy.")
        if results["hydration_score"] < 1:
            recs.append(" Increase hydration for endurance performance.")

    elif goal == "General Fitness":
        recs.append(" Combine strength + cardio sessions 4–5 days/week.")
        recs.append(" Follow a balanced diet with adequate protein and fiber.")
        recs.append(" Include flexibility and recovery days.")

    # --- Metric-Based Refinements ---
    if results["hydration_score"] < 0.8:
        recs.append(" Increase water intake — aim for ~35ml/kg body weight.")
    if results["protein_per_kg"] < 1.2:
        recs.append(" Add high-quality protein: eggs, Greek yogurt, paneer/tofu, lentils.")
    if results["cal_balance"] < -300:
        recs.append(" You’re in a calorie deficit — ideal for fat loss if intentional.")
    elif results["cal_balance"] > 300:
        recs.append(" You’re in a calorie surplus — good for muscle gain, monitor fat.")
    if results["nutrition_quality"] < 1:
        recs.append(" Improve diet balance: ensure good carb:protein:fat ratio and hydration.")

    # --- Display Recommendations ---
    if recs:
        for r in recs:
            st.write(f"- {r}")
    else:
        st.success(" You're on track! Keep it up!")

else:
    st.info(" Fill in your profile and click **Run Analysis** to view insights.")