import math
import statistics
from dataclasses import dataclass
from typing import Dict, List, Tuple
import streamlit as st

# =========================
# TEMPLATE 3: MOBILE-FRIENDLY CARDS
# =========================
st.set_page_config(
    page_title="FitTracker",
    page_icon="💪",
    layout="centered"
)

# Mobile-first CSS
st.markdown("""
<style>
/* Mobile responsive design */
@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem;
    }
}

.card {
    background: white;
    border-radius: 15px;
    padding: 20px;
    margin: 10px 0;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    border: 1px solid #e0e0e0;
    transition: transform 0.2s;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}

.primary-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.success-card {
    border-left: 4px solid #28a745;
}

.warning-card {
    border-left: 4px solid #ffc107;
}

.danger-card {
    border-left: 4px solid #dc3545;
}

.metric-large {
    font-size: 2.5rem;
    font-weight: bold;
    text-align: center;
}

.metric-label {
    font-size: 0.9rem;
    opacity: 0.8;
    text-align: center;
}

.button-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 10px;
    margin: 20px 0;
}

.action-button {
    background: #f8f9fa;
    border: 2px solid #dee2e6;
    border-radius: 10px;
    padding: 15px;
    text-align: center;
    text-decoration: none;
    transition: all 0.2s;
    display: block;
}

.action-button:hover {
    background: #e9ecef;
    border-color: #adb5bd;
    text-decoration: none;
}

.progress-circle {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 1.2rem;
    margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)

st.title("💪 FitTracker")
st.markdown("*Your personal fitness companion*")

# Quick stats cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""
    <div class="card primary-card">
        <div class="metric-large">175</div>
        <div class="metric-label">WEIGHT (lbs)</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card success-card">
        <div class="metric-large">14.2</div>
        <div class="metric-label">BODY FAT %</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card warning-card">
        <div class="metric-large">225</div>
        <div class="metric-label">BENCH PR</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="card danger-card">
        <div class="metric-large">12</div>
        <div class="metric-label">STREAK</div>
    </div>
    """, unsafe_allow_html=True)

# Today's workout card
st.markdown("""
<div class="card">
    <h3>🏋️ Today's Workout</h3>
    <p><strong>Upper Body Power</strong></p>
    <ul>
        <li>🏋️ Bench Press: 4 sets × 185 lbs × 8-10 reps</li>
        <li>🏋️ Overhead Press: 3 sets × 115 lbs × 10-12 reps</li>
        <li>🏋️ Tricep Dips: 3 sets × Bodyweight × 12-15 reps</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Quick actions
st.markdown('<div class="button-grid">', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("✅ Log Workout", use_container_width=True):
        st.success("Workout logged! 💪")

with col2:
    if st.button("📊 View Progress", use_container_width=True):
        st.info("Loading progress charts...")

with col3:
    if st.button("🎯 Set Goals", use_container_width=True):
        st.info("Opening goal settings...")

st.markdown('</div>', unsafe_allow_html=True)

# Progress overview
st.markdown("""
<div class="card">
    <h3>📈 Weekly Progress</h3>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""
    <div class="progress-circle" style="background: conic-gradient(#28a745 85%, #e9ecef 0deg); color: white;">
        85%
    </div>
    <p style="text-align: center; margin-top: 10px;"><strong>Workouts</strong></p>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="progress-circle" style="background: conic-gradient(#ffc107 65%, #e9ecef 0deg); color: white;">
        65%
    </div>
    <p style="text-align: center; margin-top: 10px;"><strong>Protein</strong></p>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="progress-circle" style="background: conic-gradient(#dc3545 90%, #e9ecef 0deg); color: white;">
        90%
    </div>
    <p style="text-align: center; margin-top: 10px;"><strong>Sleep</strong></p>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="progress-circle" style="background: conic-gradient(#17a2b8 75%, #e9ecef 0deg); color: white;">
        75%
    </div>
    <p style="text-align: center; margin-top: 10px;"><strong>Steps</strong></p>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Recent activity
st.markdown("""
<div class="card">
    <h3>📋 Recent Activity</h3>
    <div style="display: flex; align-items: center; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 8px;">
        <span style="font-size: 1.5rem; margin-right: 15px;">🏋️</span>
        <div>
            <strong>Upper Body Day</strong><br>
            <small style="color: #6c757d;">2 hours ago • 4 exercises completed</small>
        </div>
    </div>
    <div style="display: flex; align-items: center; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 8px;">
        <span style="font-size: 1.5rem; margin-right: 15px;">⚖️</span>
        <div>
            <strong>Weight Check</strong><br>
            <small style="color: #6c757d;">Yesterday • 175 lbs (-0.5 lbs)</small>
        </div>
    </div>
    <div style="display: flex; align-items: center; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 8px;">
        <span style="font-size: 1.5rem; margin-right: 15px;">🏆</span>
        <div>
            <strong>New Bench PR!</strong><br>
            <small style="color: #6c757d;">3 days ago • 225 lbs</small>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Quick add section
st.markdown("""
<div class="card">
    <h3>➕ Quick Add</h3>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    weight = st.number_input("Current Weight", 90.0, 400.0, 175.0, step=0.1)
    if st.button("Update Weight", use_container_width=True):
        st.success("Weight updated!")

with col2:
    calories = st.number_input("Today's Calories", 0, 5000, 2200)
    if st.button("Log Calories", use_container_width=True):
        st.success("Calories logged!")

st.markdown('</div>', unsafe_allow_html=True)