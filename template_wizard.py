import math
import statistics
from dataclasses import dataclass
from typing import Dict, List, Tuple
import streamlit as st

# =========================
# TEMPLATE 1: WIZARD-STYLE ONBOARDING
# =========================
st.set_page_config(
    page_title="Physique Builder - Wizard",
    page_icon="🧙‍♂️",
    layout="centered"
)

st.title("🧙‍♂️ Physique Builder Wizard")
st.markdown("**Step-by-step guided setup for your perfect training plan**")

# Progress indicator
current_step = st.session_state.get('step', 1)
steps = ["Profile", "Goals", "Lifts", "Review", "Results"]
progress = (current_step - 1) / len(steps)

st.progress(progress)
st.markdown(f"**Step {current_step} of {len(steps)}: {steps[current_step-1]}**")

# Step navigation
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if current_step > 1:
        if st.button("⬅️ Previous"):
            st.session_state.step = current_step - 1
            st.rerun()
with col3:
    if current_step < len(steps):
        if st.button("Next ➡️"):
            st.session_state.step = current_step + 1
            st.rerun()

# Step content
if current_step == 1:
    st.header("👤 Your Profile")
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", 16, 70, 24)
            height = st.number_input("Height (inches)", 55.0, 84.0, 70.0)
            sex = st.selectbox("Sex", ["Male", "Female"])
        with col2:
            weight = st.number_input("Weight (lb)", 90.0, 400.0, 170.0)
            body_fat = st.slider("Body Fat %", 5.0, 45.0, 16.0)
            training_level = st.selectbox("Experience Level", ["Beginner", "Intermediate", "Advanced"])

        submitted = st.form_submit_button("Continue to Goals")
        if submitted:
            st.session_state.profile = {"age": age, "height": height, "sex": sex,
                                      "weight": weight, "body_fat": body_fat, "level": training_level}
            st.session_state.step = 2
            st.rerun()

elif current_step == 2:
    st.header("🎯 Your Goals")
    with st.form("goals_form"):
        goal = st.selectbox("What's your main goal?",
                           ["Build Muscle", "Lose Fat", "Get Stronger", "Improve Fitness"])
        target_body = st.selectbox("What's your ideal physique?",
                                  ["Athletic", "Muscular", "Lean", "Powerful"])
        days = st.slider("How many days can you train per week?", 2, 6, 4)

        submitted = st.form_submit_button("Continue to Assessment")
        if submitted:
            st.session_state.goals = {"goal": goal, "target": target_body, "days": days}
            st.session_state.step = 3
            st.rerun()

elif current_step == 3:
    st.header("💪 Current Strength")
    st.markdown("*Estimate your current capabilities*")

    with st.form("lifts_form"):
        st.subheader("Upper Body")
        bench = st.number_input("Bench Press (max weight)", 0, 500, 135, help="Weight you can lift for 1 rep")
        pullups = st.number_input("Pull-ups (max reps)", 0, 50, 5)

        st.subheader("Lower Body")
        squat = st.number_input("Squat (max weight)", 0, 600, 185, help="Weight you can lift for 1 rep")

        submitted = st.form_submit_button("Review Your Plan")
        if submitted:
            st.session_state.lifts = {"bench": bench, "pullups": pullups, "squat": squat}
            st.session_state.step = 4
            st.rerun()

elif current_step == 4:
    st.header("📋 Plan Review")
    if 'profile' in st.session_state and 'goals' in st.session_state and 'lifts' in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Your Profile")
            p = st.session_state.profile
            st.write(f"**Age:** {p['age']}")
            st.write(f"**Height:** {p['height']} inches")
            st.write(f"**Weight:** {p['weight']} lb")
            st.write(f"**Body Fat:** {p['body_fat']}%")

        with col2:
            st.subheader("Your Goals")
            g = st.session_state.goals
            st.write(f"**Goal:** {g['goal']}")
            st.write(f"**Target:** {g['target']}")
            st.write(f"**Training Days:** {g['days']}/week")

        if st.button("🚀 Generate My Plan!", type="primary"):
            st.session_state.step = 5
            st.rerun()
    else:
        st.error("Please complete all previous steps first.")

elif current_step == 5:
    st.header("🎉 Your Custom Plan")
    st.success("Plan generated successfully!")

    # Mock results
    st.subheader("Weekly Training Split")
    st.info("**4-Day Upper/Lower Split** recommended for your goals")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Day 1: Upper Body**")
        st.write("- Bench Press: 4 sets × 8-10 reps")
        st.write("- Pull-ups: 3 sets × 6-8 reps")
        st.write("- Shoulder Press: 3 sets × 10-12 reps")

    with col2:
        st.markdown("**Day 2: Lower Body**")
        st.write("- Squats: 4 sets × 8-10 reps")
        st.write("- Deadlifts: 3 sets × 6-8 reps")
        st.write("- Lunges: 3 sets × 10-12 reps")

    st.subheader("Nutrition Guidelines")
    st.info("Based on your profile: 2,500 calories, 200g protein daily")

    if st.button("🔄 Start Over"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()