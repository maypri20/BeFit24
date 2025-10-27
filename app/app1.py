import streamlit as st
import pandas as pd
import numpy as np

# -------------------------------------------------------
# 1️⃣ Load Dataset
# -------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("../data/clean/clean_data.csv")  # change to your dataset path
    return df

df = load_data()

# -------------------------------------------------------
# 2️⃣ Derived Metrics
# -------------------------------------------------------
def ensure_derived(df_):
    df = df_.copy()
    w = df["weight_kg"].astype(float)
    h = df["height_m"].astype(float)
    age = df["age"].astype(float)
    gender_factor = (df["gender"].str.strip().str.title() == "Male").astype(int)
    carbs = df["carbs"].astype(float)
    proteins = df["proteins"].astype(float)
    fats = df["fats"].astype(float)
    calories = df["calories"].astype(float)
    calories_burned = df["calories_burned"].astype(float).fillna(0.0)

    df["bmi"] = w / (h**2)
    df["fat_percentage"] = (1.20 * df["bmi"]) + (0.23 * age) - (10.8 * gender_factor) - 5.4
    df["lean_mass_kg"] = w * (1 - df["fat_percentage"]/100.0)
    total_cals = (carbs*4) + (proteins*4) + (fats*9)
    df["pct_carbs"] = np.where(total_cals > 0, (carbs*4 / total_cals)*100.0, 0.0)
    df["protein_per_kg"] = np.where(w > 0, proteins / w, 0.0)
    df["cal_balance"] = calories - calories_burned
    return df

df = ensure_derived(df)

# -------------------------------------------------------
# 3️⃣ Gower Distance Function
# -------------------------------------------------------
def gower_distance_to_df(df_base, row, num_cols, cat_cols, weights):
    Xn = df_base[num_cols].astype(float)
    rn = row[num_cols].astype(float)
    col_min = Xn.min(axis=0)
    col_max = Xn.max(axis=0)
    rng = (col_max - col_min).replace(0, 1e-9)
    num_diff = np.abs(Xn.values - rn.values) / rng.values

    Xc = df_base[cat_cols].astype(str).apply(lambda s: s.str.strip().str.title())
    rc = row[cat_cols].astype(str).str.strip().str.title()
    cat_diff = (Xc.values != rc.values).astype(float)

    w_num = np.array([weights[c] for c in num_cols])[None, :]
    w_cat = np.array([weights[c] for c in cat_cols])[None, :]
    num_part = (num_diff * w_num).sum(axis=1)
    cat_part = (cat_diff * w_cat).sum(axis=1)
    w_sum = w_num.sum() + w_cat.sum()
    return (num_part + cat_part) / w_sum

# -------------------------------------------------------
# 4️⃣ Streamlit UI – User Input
# -------------------------------------------------------
st.set_page_config(page_title="FitTrack360 – Wellness Recommender", layout="centered")
st.title("🏋️‍♀️ FitTrack360 – AI-Driven Wellness & Lifestyle Recommendations")

st.markdown("""
Welcome to **FitTrack360**, your intelligent fitness and nutrition analytics dashboard.  
We'll analyze your data, compare it with real users in our database,  
and provide actionable recommendations for a healthier you.
""")

# --- Step 1: Profile
st.header("1️⃣ Your Profile")
col1, col2 = st.columns(2)
with col1:
    gender = st.selectbox("Gender", ["Female", "Male"])
    age = st.number_input("Age", 18, 80, 35)
    height_m = st.number_input("Height (m)", 1.3, 2.2, 1.68)
with col2:
    weight_kg = st.number_input("Weight (kg)", 40, 150, 106)
    water_intake_liters = st.number_input("Water Intake (L/day)", 0.5, 5.0, 2.5)

# --- Step 2: Workout
st.header("2️⃣ Workout Details")
col3, col4 = st.columns(2)
with col3:
    workout_type = st.selectbox("Workout Type", ["Cardio", "Strength", "Yoga", "Mixed"])
    session_duration_hours = st.number_input("Session Duration (hours)", 0.2, 3.0, 0.8)
    calories_burned = st.number_input("Calories Burned", 100, 1500, 400)
with col4:
    avg_bpm = st.number_input("Average BPM", 60, 190, 140)
    max_bpm = st.number_input("Max BPM", 80, 220, 175)
    resting_bpm = st.number_input("Resting BPM", 40, 120, 80)

# --- Step 3: Nutrition
st.header("3️⃣ Nutrition & Meals")
col5, col6 = st.columns(2)
with col5:
    diet_type = st.selectbox("Diet Type", ["Vegetarian", "Vegan", "Non-Vegetarian"])
    meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner"])
    calories = st.number_input("Calories Consumed", 500, 3500, 1700)
with col6:
    carbs = st.number_input("Carbs (g)", 0, 500, 180)
    proteins = st.number_input("Proteins (g)", 0, 200, 65)
    fats = st.number_input("Fats (g)", 0, 150, 50)

# -------------------------------------------------------
# 5️⃣ Generate Recommendations
# -------------------------------------------------------
if st.button("🚀 Generate My Personalized Wellness Plan"):
    user_data = {
        "gender": gender, "age": age, "height_m": height_m, "weight_kg": weight_kg,
        "max_bpm": max_bpm, "avg_bpm": avg_bpm, "resting_bpm": resting_bpm,
        "session_duration_hours": session_duration_hours, "calories_burned": calories_burned,
        "water_intake_liters": water_intake_liters, "carbs": carbs, "proteins": proteins,
        "fats": fats, "calories": calories, "workout_type": workout_type,
        "meal_type": meal_type, "diet_type": diet_type
    }

    new_input_df = pd.DataFrame([user_data])
    new_input_df = ensure_derived(new_input_df)

    # --- Columns for Gower
    cat_cols = ["gender", "workout_type", "meal_type", "diet_type"]
    num_cols = [
        "age","weight_kg","height_m","max_bpm","avg_bpm","resting_bpm",
        "session_duration_hours","calories_burned","water_intake_liters",
        "carbs","proteins","fats","calories",
        "bmi","fat_percentage","lean_mass_kg","pct_carbs","protein_per_kg","cal_balance"
    ]
    weights = {col: 1.0 for col in num_cols + cat_cols}
    for col in ["avg_bpm","resting_bpm","cal_balance","protein_per_kg","bmi"]:
        weights[col] = 1.5

    # --- Compute similarity
    dist_vec = gower_distance_to_df(df, new_input_df.iloc[0], num_cols, cat_cols, weights)
    k = 5
    topk_idx = np.argpartition(dist_vec, kth=min(k, len(dist_vec)-1))[:k]
    similar_users = df.iloc[topk_idx]
    avg_profile = similar_users.mean(numeric_only=True)

    st.success("✅ Analysis complete! Comparing you with similar users in our database...")

    # -------------------------------------------------------
    # 6️⃣ Personalized Recommendations
    # -------------------------------------------------------
    user = new_input_df.iloc[0]
    recs = []

    # --- Calorie balance
    if user["cal_balance"] > avg_profile["cal_balance"] + 150:
        recs.append("⚖️ You're eating more than similar users — consider a slight calorie deficit to improve body composition.")
    elif user["cal_balance"] < avg_profile["cal_balance"] - 150:
        recs.append("🔥 You're eating less than similar users — ensure you're not under-fueling for workouts.")
    else:
        recs.append("✅ Your calorie intake is well-aligned with similar healthy profiles.")

    # --- Protein
    if user["protein_per_kg"] < avg_profile["protein_per_kg"]:
        recs.append("🍳 Increase protein intake to reach the average of similar users — it supports lean mass growth.")
    else:
        recs.append("💪 Your protein intake is above average — great for recovery and strength.")

    # --- Water
    if user["water_intake_liters"] < avg_profile["water_intake_liters"]:
        recs.append("💧 Try to increase hydration — similar users drink more water daily.")
    else:
        recs.append("🚰 Your hydration is optimal compared to similar profiles.")

    # --- Workout Duration
    if user["session_duration_hours"] < avg_profile["session_duration_hours"]:
        recs.append("🏋️ Increase workout duration slightly to match the activity level of peers.")
    else:
        recs.append("🔥 Your workout duration is on par or better than similar users.")

    # --- Heart Health
    if user["resting_bpm"] > avg_profile["resting_bpm"] + 5:
        recs.append("❤️ Higher resting BPM — consider adding low-intensity cardio or rest days.")
    else:
        recs.append("🫀 Your cardiovascular metrics are comparable to fit individuals.")

    # --- Display summary
    st.header("💡 Personalized Wellness Insights")
    st.write(f"**Your BMI:** {user['bmi']:.1f} | **Fat %:** {user['fat_percentage']:.1f}% | **Lean Mass:** {user['lean_mass_kg']:.1f} kg")
    st.write(f"**Calorie Balance:** {user['cal_balance']:.0f} kcal | **Protein/kg:** {user['protein_per_kg']:.2f} g/kg | **Hydration:** {user['water_intake_liters']:.1f} L")

    st.markdown("### 🧠 Recommendations Based on Similar Users")
    for r in recs:
        st.write("- " + r)

    st.markdown("### 👥 Group Insights (Top 5 Similar Profiles)")
    st.dataframe(similar_users[["gender","age","bmi","fat_percentage","protein_per_kg","cal_balance","workout_type","diet_type"]])
