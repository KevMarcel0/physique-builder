import math
import statistics
from dataclasses import dataclass
from typing import Dict, List, Tuple
import streamlit as st
import pandas as pd

# =========================
# TEMPLATE 2: DASHBOARD-STYLE
# =========================
st.set_page_config(
    page_title="Physique Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for dashboard look
st.markdown("""
<style>
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 10px;
    color: white;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.progress-card {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #28a745;
}
.tab-content {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Physique Development Dashboard")
st.markdown("*Track, analyze, and optimize your fitness journey*")

# Top metrics row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Current Weight", "175 lbs", "+2 lbs")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Body Fat", "14.2%", "-0.5%")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Bench PR", "225 lbs", "+10 lbs")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Workout Streak", "12 days", "🔥")
    st.markdown('</div>', unsafe_allow_html=True)

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(["🏋️ Today's Workout", "📈 Progress", "🎯 Goals", "⚙️ Settings"])

with tab1:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.header("Today's Workout: Upper Body Push")

    # Workout checklist
    st.subheader("Complete these exercises:")

    exercises = [
        {"name": "Bench Press", "sets": "4 sets × 8-10 reps", "weight": "175 lbs", "completed": False},
        {"name": "Overhead Press", "sets": "3 sets × 10-12 reps", "weight": "115 lbs", "completed": False},
        {"name": "Tricep Dips", "sets": "3 sets × 12-15 reps", "weight": "Bodyweight", "completed": False},
        {"name": "Lateral Raises", "sets": "3 sets × 15 reps", "weight": "25 lbs", "completed": False}
    ]

    for i, exercise in enumerate(exercises):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        with col1:
            st.write(f"**{exercise['name']}**")
        with col2:
            st.write(exercise['sets'])
        with col3:
            st.write(f"@{exercise['weight']}")
        with col4:
            completed = st.checkbox("", key=f"exercise_{i}")
            if completed:
                st.success("✅ Done!")

    st.markdown("---")
    if st.button("🎉 Finish Workout", type="primary"):
        st.balloons()
        st.success("Great job! Workout logged successfully!")

    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.header("Progress Tracking")

    # Progress charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Weight Progress")
        # Mock data
        weight_data = pd.DataFrame({
            'Date': pd.date_range(start='2024-01-01', periods=12, freq='W'),
            'Weight': [170, 171, 172, 173, 172, 174, 175, 176, 175, 177, 176, 175]
        })
        st.line_chart(weight_data.set_index('Date'))

    with col2:
        st.subheader("Strength Gains")
        strength_data = pd.DataFrame({
            'Exercise': ['Bench', 'Squat', 'Deadlift', 'Pull-ups'],
            'Starting': [185, 225, 275, 8],
            'Current': [205, 245, 295, 12],
            'Progress': [11, 9, 7, 50]
        })
        st.bar_chart(strength_data.set_index('Exercise')['Progress'])

    # Progress cards
    st.subheader("Goal Progress")
    goals = [
        {"name": "Lose 10 lbs", "current": 7, "target": 10, "unit": "lbs"},
        {"name": "Bench Press 225", "current": 205, "target": 225, "unit": "lbs"},
        {"name": "6-pack abs", "current": 14.2, "target": 10, "unit": "% BF"}
    ]

    for goal in goals:
        progress = min(goal['current'] / goal['target'] * 100, 100)
        st.markdown(f'<div class="progress-card">', unsafe_allow_html=True)
        st.write(f"**{goal['name']}**")
        st.progress(progress / 100)
        st.write(f"{goal['current']}/{goal['target']} {goal['unit']} ({progress:.1f}%)")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.header("Goal Setting")

    st.subheader("Set New Goals")

    with st.form("new_goal"):
        goal_type = st.selectbox("Goal Type", ["Weight Loss", "Strength", "Body Composition", "Endurance"])
        goal_description = st.text_input("Goal Description", "e.g., Bench press 225 lbs")
        target_value = st.number_input("Target Value", 0.0, 1000.0, 0.0)
        unit = st.selectbox("Unit", ["lbs", "kg", "%", "reps", "days"])
        deadline = st.date_input("Target Date")

        submitted = st.form_submit_button("Add Goal")
        if submitted:
            st.success("Goal added successfully!")

    st.subheader("Active Goals")
    active_goals = [
        {"name": "Bench Press 225 lbs", "progress": 91, "deadline": "2024-06-01"},
        {"name": "Lose 10 lbs", "progress": 70, "deadline": "2024-05-15"},
        {"name": "12% body fat", "progress": 85, "deadline": "2024-07-01"}
    ]

    for goal in active_goals:
        col1, col2, col3 = st.columns([4, 2, 1])
        with col1:
            st.write(f"**{goal['name']}**")
        with col2:
            st.progress(goal['progress'] / 100)
            st.write(f"{goal['progress']}%")
        with col3:
            st.write(f"📅 {goal['deadline']}")

    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.header("Settings & Preferences")

    st.subheader("Profile Settings")
    with st.form("profile_settings"):
        name = st.text_input("Name", "John Doe")
        units = st.selectbox("Preferred Units", ["Imperial (lbs)", "Metric (kg)"])
        notifications = st.checkbox("Email workout reminders", True)
        public_profile = st.checkbox("Make profile public", False)

        submitted = st.form_submit_button("Save Settings")
        if submitted:
            st.success("Settings saved!")

    st.subheader("App Preferences")
    theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
    language = st.selectbox("Language", ["English", "Spanish", "French"])

    st.subheader("Data Management")
    if st.button("Export Data"):
        st.info("Data export feature coming soon!")

    if st.button("Reset App", type="secondary"):
        st.warning("This will reset all your data. Are you sure?")
        confirm = st.button("Yes, reset everything", type="secondary")
        if confirm:
            st.error("App reset! (This is just a demo)")

    st.markdown('</div>', unsafe_allow_html=True)