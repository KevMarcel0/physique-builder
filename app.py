import math
import statistics
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple
import streamlit as st
import random
import time
import json
import os
from pathlib import Path

# =========================
# ENHANCED GAMIFIED PHYSIQUE BUILDER WITH ACCOUNTS & AVATARS
# =========================
st.set_page_config(
    page_title="Level Up Fitness",
    page_icon="🎮",
    layout="wide"
)

# Avatar system - Pixelated retro gaming characters
AVATARS = {
    "hero": {
        "name": "Retro Jumper",
        "description": "Classic jumping pixel character",
        "base_gif": "🦸‍♂️",
        "level_gifs": {
            1: "🧍‍♂️",  # Level 1-5: Standing
            6: "🏃‍♂️",  # Level 6-10: Running
            11: "🤸‍♂️", # Level 11-15: Jumping
            16: "⚔️",   # Level 16-20: Fighting
            21: "👑"    # Level 21+: Champion
        }
    },
    "princess": {
        "name": "Royal Pixel",
        "description": "Elegant pixelated royalty",
        "base_gif": "👸",
        "level_gifs": {
            1: "🧍‍♀️",
            6: "🏃‍♀️",
            11: "💃",
            16: "🛡️",
            21: "👸"
        }
    },
    "beast": {
        "name": "Fierce Pixel",
        "description": "Powerful pixelated monster",
        "base_gif": "🐉",
        "level_gifs": {
            1: "🐲",
            6: "🦖",
            11: "🔥",
            16: "👹",
            21: "🐉"
        }
    },
    "mystic": {
        "name": "Magical Pixel",
        "description": "Enchanted pixelated sorcerer",
        "base_gif": "🧙‍♂️",
        "level_gifs": {
            1: "🧙‍♂️",
            6: "🔮",
            11: "✨",
            16: "🌟",
            21: "🪄"
        }
    },
    "guardian": {
        "name": "Armored Pixel",
        "description": "Protective pixelated knight",
        "base_gif": "⚔️",
        "level_gifs": {
            1: "🛡️",
            6: "⚔️",
            11: "🏰",
            16: "👑",
            21: "⚔️"
        }
    }
}

# =========================
# DATA PERSISTENCE
# =========================
USERS_FILE = "users_data.json"

def load_all_users() -> List[Dict]:
    """Load all users from JSON file"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_all_users(users: List[Dict]) -> None:
    """Save all users to JSON file"""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def load_user(username: str) -> Dict | None:
    """Load a specific user from JSON file (case-insensitive)"""
    users = load_all_users()
    for user in users:
        if user.get("username", "").lower() == username.lower():
            return user
    return None

def save_user(user: Dict) -> None:
    """Save or update a user in JSON file"""
    users = load_all_users()
    # Remove existing user if present (case-insensitive)
    users = [u for u in users if u.get("username", "").lower() != user.get("username", "").lower()]
    # Add updated user
    users.append(user)
    save_all_users(users)

def user_exists(username: str) -> bool:
    """Check if a user already exists (case-insensitive)"""
    return load_user(username) is not None


# =========================
# INITIALIZE USERS
# =========================
# Load users from file
if 'all_users' not in st.session_state:
    saved_users = load_all_users()
    if saved_users:
        st.session_state.all_users = saved_users
    else:
        # Create default users if no saved data
        default_users = [
            {"username": "ProLifter", "avatar": "hero", "level": 12, "xp": 3200, "xp_to_next": 3600},
            {"username": "FitWarrior", "avatar": "princess", "level": 8, "xp": 1950, "xp_to_next": 2200},
            {"username": "GainsMaster", "avatar": "guardian", "level": 15, "xp": 4800, "xp_to_next": 5200},
            {"username": "BeastMode", "avatar": "beast", "level": 6, "xp": 1450, "xp_to_next": 1700},
            {"username": "MysticGains", "avatar": "mystic", "level": 10, "xp": 2650, "xp_to_next": 2900},
        ]
        save_all_users(default_users)
        st.session_state.all_users = default_users

if 'user_account' not in st.session_state:
    st.session_state.user_account = None


# =========================
# DATA MODELS
# =========================
@dataclass
class UserProfile:
    age: int
    sex: str
    height_in: float
    weight_lb: float
    body_fat: float
    training_age: str
    goal: str
    target_build: str
    days_per_week: int
    sleep_hours: float
    stress_level: int
    steps_per_day: int
    hydration_liters: float
    protein_g: int
    calories: int
    injuries: str = ""
    equipment: str = "Full Gym"


@dataclass
class LiftInputs:
    bench_5rm: float
    barbell_row_5rm: float
    pullups_reps: int
    strict_pushups_reps: int


# =========================
# HELPER FUNCTIONS
# =========================
def pounds_to_kg(lb: float) -> float:
    return lb * 0.45359237


def estimate_1rm_from_5rm(weight_5rm: float) -> float:
    """
    Epley formula approximation using 5 reps.
    """
    if weight_5rm <= 0:
        return 0.0
    return weight_5rm * (1 + 5 / 30)


def round_to_nearest_5(weight: float) -> int:
    return int(5 * round(weight / 5))


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def score_to_grade(score: float) -> str:
    if score >= 90:
        return "S"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def normalize_ratio_score(value: float, low: float, high: float) -> float:
    """
    Converts a value into a 0-100 score between low and high.
    """
    if high == low:
        return 50.0
    score = (value - low) / (high - low) * 100
    return clamp(score, 0, 100)


def compute_bmi(height_in: float, weight_lb: float) -> float:
    if height_in <= 0:
        return 0.0
    return (weight_lb / (height_in ** 2)) * 703


def compute_ffmi(height_in: float, weight_lb: float, body_fat: float) -> float:
    """
    Approximate FFMI.
    """
    height_m = height_in * 0.0254
    weight_kg = pounds_to_kg(weight_lb)
    lean_mass_kg = weight_kg * (1 - body_fat / 100)
    if height_m <= 0:
        return 0.0
    ffmi = lean_mass_kg / (height_m ** 2)
    return ffmi


def get_training_multiplier(training_age: str) -> float:
    mapping = {
        "Beginner": 0.90,
        "Novice": 1.00,
        "Intermediate": 1.08,
        "Advanced": 1.15
    }
    return mapping.get(training_age, 1.0)


def get_goal_bias(goal: str) -> Dict[str, float]:
    if goal == "Lean Bulk":
        return {"volume": 1.10, "intensity": 1.00, "cardio": 0.85}
    if goal == "Fat Loss":
        return {"volume": 0.95, "intensity": 0.95, "cardio": 1.20}
    if goal == "Recomp":
        return {"volume": 1.00, "intensity": 1.00, "cardio": 1.00}
    if goal == "Strength":
        return {"volume": 0.90, "intensity": 1.12, "cardio": 0.85}
    return {"volume": 1.0, "intensity": 1.0, "cardio": 1.0}


def get_target_profile(target_build: str) -> Dict[str, float]:
    """
    These are style targets, not promises of exact celebrity physiques.
    """
    profiles = {
        "Lean Actor Build": {
            "target_bf_male": 11.5,
            "target_bf_female": 20.0,
            "lat_emphasis": 1.15,
            "shoulder_emphasis": 1.20,
            "chest_emphasis": 1.05,
            "leg_emphasis": 0.95,
            "arm_emphasis": 1.10,
            "conditioning": 1.10,
        },
        "Athletic Superhero Build": {
            "target_bf_male": 10.0,
            "target_bf_female": 18.0,
            "lat_emphasis": 1.15,
            "shoulder_emphasis": 1.25,
            "chest_emphasis": 1.15,
            "leg_emphasis": 1.05,
            "arm_emphasis": 1.15,
            "conditioning": 1.00,
        },
        "Powerlifter Build": {
            "target_bf_male": 15.0,
            "target_bf_female": 24.0,
            "lat_emphasis": 1.00,
            "shoulder_emphasis": 0.95,
            "chest_emphasis": 1.00,
            "leg_emphasis": 1.20,
            "arm_emphasis": 0.90,
            "conditioning": 0.80,
        },
        "Balanced Aesthetic Build": {
            "target_bf_male": 12.5,
            "target_bf_female": 21.0,
            "lat_emphasis": 1.10,
            "shoulder_emphasis": 1.10,
            "chest_emphasis": 1.05,
            "leg_emphasis": 1.05,
            "arm_emphasis": 1.05,
            "conditioning": 1.00,
        }
    }
    return profiles[target_build]


# =========================
# SCORING ENGINE
# =========================
def compute_strength_score(profile: UserProfile, lifts: LiftInputs) -> Tuple[float, Dict[str, float]]:
    bw = profile.weight_lb if profile.weight_lb > 0 else 1
    bench_1rm = estimate_1rm_from_5rm(lifts.bench_5rm)
    row_1rm = estimate_1rm_from_5rm(lifts.barbell_row_5rm)

    ratios = {
        "Bench/BW": bench_1rm / bw,
        "Row/BW": row_1rm / bw,
        "Pull-Ups": lifts.pullups_reps,
        "Push-Ups": lifts.strict_pushups_reps
    }

    score_parts = [
        normalize_ratio_score(ratios["Bench/BW"], 0.75, 1.5),
        normalize_ratio_score(ratios["Row/BW"], 0.60, 1.25),
        normalize_ratio_score(ratios["Pull-Ups"], 0, 15),
        normalize_ratio_score(ratios["Push-Ups"], 0, 50),
    ]

    score = statistics.mean(score_parts) * get_training_multiplier(profile.training_age)
    score = clamp(score, 0, 100)
    return score, ratios


def compute_recovery_score(profile: UserProfile) -> float:
    sleep_score = normalize_ratio_score(profile.sleep_hours, 5.5, 9.0)
    stress_score = normalize_ratio_score(11 - profile.stress_level, 1, 10)
    hydration_score = normalize_ratio_score(profile.hydration_liters, 1.2, 4.0)
    protein_per_kg = profile.protein_g / max(1.0, pounds_to_kg(profile.weight_lb))
    protein_score = normalize_ratio_score(protein_per_kg, 1.0, 2.2)
    steps_score = normalize_ratio_score(profile.steps_per_day, 2500, 11000)

    score = (
        sleep_score * 0.30 +
        stress_score * 0.20 +
        hydration_score * 0.15 +
        protein_score * 0.20 +
        steps_score * 0.15
    )
    return clamp(score, 0, 100)


def compute_balance_score(profile: UserProfile, lifts: LiftInputs) -> float:
    bench_1rm = estimate_1rm_from_5rm(lifts.bench_5rm)
    row_1rm = estimate_1rm_from_5rm(lifts.barbell_row_5rm)

    push_pull_ratio = bench_1rm / max(row_1rm, 1)
    push_balance_ratio = lifts.strict_pushups_reps / max(lifts.pullups_reps, 1)

    push_pull_score = 100 - abs(push_pull_ratio - 1.0) * 55
    push_balance_score = 100 - abs(push_balance_ratio - 1.0) * 50

    days_score = normalize_ratio_score(profile.days_per_week, 2, 6)

    score = statistics.mean([
        clamp(push_pull_score, 0, 100),
        clamp(push_balance_score, 0, 100),
        clamp(days_score, 0, 100)
    ])
    return clamp(score, 0, 100)


def compute_physique_match_score(profile: UserProfile) -> float:
    target = get_target_profile(profile.target_build)
    ffmi = compute_ffmi(profile.height_in, profile.weight_lb, profile.body_fat)
    bmi = compute_bmi(profile.height_in, profile.weight_lb)

    if profile.sex == "Male":
        bf_target = target["target_bf_male"]
    else:
        bf_target = target["target_bf_female"]

    bodyfat_score = 100 - abs(profile.body_fat - bf_target) * 6
    ffmi_score = normalize_ratio_score(ffmi, 17.5, 23.0)
    bmi_score = normalize_ratio_score(bmi, 20.0, 27.0)

    score = (
        clamp(bodyfat_score, 0, 100) * 0.45 +
        ffmi_score * 0.35 +
        bmi_score * 0.20
    )
    return clamp(score, 0, 100)


def compute_hypertrophy_score(profile: UserProfile, lifts: LiftInputs) -> float:
    ffmi = compute_ffmi(profile.height_in, profile.weight_lb, profile.body_fat)
    protein_per_kg = profile.protein_g / max(1.0, pounds_to_kg(profile.weight_lb))
    days_score = normalize_ratio_score(profile.days_per_week, 2, 6)
    protein_score = normalize_ratio_score(protein_per_kg, 1.2, 2.2)
    sleep_score = normalize_ratio_score(profile.sleep_hours, 5.5, 9.0)
    ffmi_score = normalize_ratio_score(ffmi, 17.5, 23.5)

    score = (
        days_score * 0.25 +
        protein_score * 0.30 +
        sleep_score * 0.20 +
        ffmi_score * 0.25
    )
    return clamp(score, 0, 100)


def compute_overall_rating(strength: float, recovery: float, balance: float,
                           physique_match: float, hypertrophy: float) -> float:
    return clamp(
        strength * 0.24 +
        recovery * 0.22 +
        balance * 0.18 +
        physique_match * 0.18 +
        hypertrophy * 0.18,
        0, 100
    )


# =========================
# PROGRAMMING ENGINE
# =========================
def choose_split(days_per_week: int, goal: str, target_build: str) -> str:
    if days_per_week <= 3:
        return "Full Body x3"
    if days_per_week == 4:
        return "Upper / Lower x4"
    if days_per_week == 5:
        return "Push / Pull / Legs / Upper / Lower"
    return "Push / Pull / Legs / Upper / Lower / Arms+Conditioning"


def build_exercise_library() -> Dict[str, List[Dict]]:
    return {
        "Full Body x3": [
            {"day": "Day 1", "focus": "Strength + Upper Emphasis", "exercises": [
                ("Bench Press", "3-4", "5-6", "bench"),
                ("Barbell Row", "3-4", "6-8", "row"),
                ("Strict Push-Up", "3", "8-12", "pushup"),
                ("Lateral Raise", "3", "12-15", "none"),
                ("Cable Crunch", "3", "12-15", "none"),
            ]},
            {"day": "Day 2", "focus": "Hypertrophy + Pull Emphasis", "exercises": [
                ("Incline Dumbbell Press", "3", "8-12", "bench"),
                ("Lat Pulldown / Pull-Up", "3-4", "6-10", "pullup"),
                ("Chest-Supported Row", "3", "8-10", "row"),
                ("Strict Push-Up", "3", "10-15", "pushup"),
                ("Hammer Curl", "3", "10-12", "none"),
            ]},
            {"day": "Day 3", "focus": "Balanced Volume", "exercises": [
                ("Incline Bench Press", "3-4", "6-8", "bench"),
                ("Chest-Supported Row", "3-4", "8-10", "row"),
                ("Strict Push-Up", "3", "12-20", "pushup"),
                ("Cable Lateral Raise", "3", "12-15", "none"),
                ("Triceps Pushdown", "3", "10-12", "none"),
            ]},
        ],
        "Upper / Lower x4": [
            {"day": "Day 1", "focus": "Upper Strength", "exercises": [
                ("Bench Press", "4", "5-6", "bench"),
                ("Barbell Row", "4", "6-8", "row"),
                ("Pull-Up / Lat Pulldown", "3", "6-10", "pullup"),
                ("Incline Dumbbell Press", "3", "8-10", "bench"),
                ("Lateral Raise", "3", "12-15", "none"),
                ("EZ-Bar Curl", "3", "10-12", "none"),
            ]},
            {"day": "Day 2", "focus": "Push + Core", "exercises": [
                ("Strict Push-Up", "4", "8-12", "pushup"),
                ("Incline Dumbbell Press", "3", "8-10", "bench"),
                ("Cable Fly", "3", "12-15", "none"),
                ("Triceps Pushdown", "3", "10-12", "none"),
                ("Hanging Leg Raise", "3", "10-15", "none"),
            ]},
            {"day": "Day 3", "focus": "Upper Hypertrophy", "exercises": [
                ("Incline Bench Press", "4", "6-8", "bench"),
                ("Chest-Supported Row", "4", "8-10", "row"),
                ("Lat Pulldown", "3", "8-12", "pullup"),
                ("Strict Push-Up", "3", "10-15", "pushup"),
                ("Cable Fly", "3", "12-15", "none"),
                ("Cable Lateral Raise", "4", "12-20", "none"),
                ("Skull Crusher", "3", "10-12", "none"),
                ("Incline Curl", "3", "10-12", "none"),
            ]},
            {"day": "Day 4", "focus": "Pull + Conditioning", "exercises": [
                ("Barbell Row", "3-4", "8-10", "row"),
                ("Pull-Up / Lat Pulldown", "3", "8-12", "pullup"),
                ("Rear Delt Fly", "3", "12-15", "none"),
                ("EZ-Bar Curl", "3", "10-12", "none"),
                ("Bike / Incline Walk", "1", "12-20 min", "none"),
            ]},
        ],
        "Push / Pull / Legs / Upper / Lower": [
            {"day": "Day 1", "focus": "Push", "exercises": [
                ("Bench Press", "4", "5-6", "bench"),
                ("Incline Dumbbell Press", "3", "8-10", "bench"),
                ("Strict Push-Up", "3", "10-15", "pushup"),
                ("Cable Fly", "3", "12-15", "none"),
                ("Lateral Raise", "4", "12-20", "none"),
                ("Triceps Pushdown", "3", "10-12", "none"),
            ]},
            {"day": "Day 2", "focus": "Pull", "exercises": [
                ("Barbell Row", "4", "6-8", "row"),
                ("Weighted Pull-Up / Lat Pulldown", "4", "6-10", "pullup"),
                ("Chest-Supported Row", "3", "8-10", "row"),
                ("Rear Delt Fly", "3", "12-15", "none"),
                ("EZ-Bar Curl", "3", "10-12", "none"),
                ("Hammer Curl", "3", "10-12", "none"),
            ]},
            {"day": "Day 3", "focus": "Push + Core", "exercises": [
                ("Incline Bench Press", "4", "6-8", "bench"),
                ("Strict Push-Up", "3", "12-20", "pushup"),
                ("Cable Fly", "3", "12-15", "none"),
                ("Triceps Pushdown", "3", "10-12", "none"),
                ("Cable Crunch", "3", "12-15", "none"),
            ]},
            {"day": "Day 4", "focus": "Upper Aesthetic", "exercises": [
                ("Incline Bench Press", "4", "6-8", "bench"),
                ("Chest-Supported Row", "4", "8-10", "row"),
                ("Lat Pulldown", "3", "8-12", "pullup"),
                ("Strict Push-Up", "3", "10-15", "pushup"),
                ("Cable Lateral Raise", "4", "12-20", "none"),
                ("Cable Curl", "3", "10-12", "none"),
                ("Overhead Rope Extension", "3", "10-12", "none"),
            ]},
            {"day": "Day 5", "focus": "Pull + Conditioning", "exercises": [
                ("Barbell Row", "3-4", "8-10", "row"),
                ("Pull-Up / Lat Pulldown", "3", "8-12", "pullup"),
                ("Rear Delt Fly", "3", "12-15", "none"),
                ("EZ-Bar Curl", "3", "10-12", "none"),
                ("Incline Walk / Bike", "1", "15-20 min", "none"),
            ]},
        ],
        "Push / Pull / Legs / Upper / Lower / Arms+Conditioning": [
            {"day": "Day 1", "focus": "Push Strength", "exercises": [
                ("Bench Press", "4", "4-6", "bench"),
                ("Incline Dumbbell Press", "3", "8-10", "bench"),
                ("Strict Push-Up", "3", "8-12", "pushup"),
                ("Cable Fly", "3", "12-15", "none"),
                ("Lateral Raise", "4", "12-20", "none"),
                ("Triceps Pushdown", "3", "10-12", "none"),
            ]},
            {"day": "Day 2", "focus": "Pull Strength", "exercises": [
                ("Barbell Row", "4", "5-8", "row"),
                ("Weighted Pull-Up / Lat Pulldown", "4", "6-10", "pullup"),
                ("Chest-Supported Row", "3", "8-10", "row"),
                ("Rear Delt Fly", "3", "12-15", "none"),
                ("EZ-Bar Curl", "3", "10-12", "none"),
            ]},
            {"day": "Day 3", "focus": "Push Hypertrophy", "exercises": [
                ("Incline Bench Press", "4", "6-8", "bench"),
                ("Strict Push-Up", "3", "12-20", "pushup"),
                ("Cable Fly", "3", "12-15", "none"),
                ("Triceps Pushdown", "3", "10-12", "none"),
                ("Standing Calf Raise", "4", "12-15", "none"),
            ]},
            {"day": "Day 4", "focus": "Upper Aesthetic", "exercises": [
                ("Incline Bench Press", "4", "6-8", "bench"),
                ("Lat Pulldown", "4", "8-12", "pullup"),
                ("Strict Push-Up", "3", "10-15", "pushup"),
                ("Cable Lateral Raise", "4", "12-20", "none"),
                ("Cable Fly", "3", "12-15", "none"),
                ("Cable Curl", "3", "10-12", "none"),
                ("Overhead Rope Extension", "3", "10-12", "none"),
            ]},
            {"day": "Day 5", "focus": "Pull Volume + Core", "exercises": [
                ("Barbell Row", "3-4", "8-10", "row"),
                ("Pull-Up / Lat Pulldown", "3", "8-12", "pullup"),
                ("Rear Delt Fly", "3", "12-15", "none"),
                ("EZ-Bar Curl", "3", "10-12", "none"),
                ("Cable Crunch", "3", "12-15", "none"),
            ]},
            {"day": "Day 6", "focus": "Arms + Conditioning", "exercises": [
                ("Close-Grip Bench or Dip", "3", "6-8", "bench"),
                ("EZ-Bar Curl", "3", "8-10", "none"),
                ("Incline Curl", "3", "10-12", "none"),
                ("Skull Crusher", "3", "10-12", "none"),
                ("Lateral Raise Mechanical Drop Set", "3", "15-20", "none"),
                ("Incline Walk / Bike / Row", "1", "20-25 min", "none"),
            ]},
        ],
    }


def get_intensity_percentage(goal: str, rep_range: str) -> float:
    """
    Approximate training percentages for working sets.
    """
    if "4-6" in rep_range:
        return 0.80 if goal != "Fat Loss" else 0.75
    if "5-6" in rep_range:
        return 0.78
    if "5-8" in rep_range:
        return 0.75
    if "6-8" in rep_range:
        return 0.73
    if "6-10" in rep_range:
        return 0.70
    if "8-10" in rep_range:
        return 0.67
    if "8-12" in rep_range:
        return 0.65
    if "10-12" in rep_range:
        return 0.60
    if "12-15" in rep_range:
        return 0.55
    if "12-20" in rep_range:
        return 0.45
    return 0.65


def estimate_working_weight(exercise_key: str, lifts: LiftInputs, goal: str) -> str:
    one_rms = {
        "bench": estimate_1rm_from_5rm(lifts.bench_5rm),
        "row": estimate_1rm_from_5rm(lifts.barbell_row_5rm),
    }

    if exercise_key == "pullup":
        return "Bodyweight or weighted as able"
    if exercise_key == "pushup":
        return "Bodyweight"
    if exercise_key == "none":
        return "Choose a weight that leaves 1-2 reps in reserve"

    base_1rm = one_rms.get(exercise_key, 0)
    if base_1rm <= 0:
        return "Enter lifts to estimate"

    pct = 0.70
    est = round_to_nearest_5(base_1rm * pct)
    return f"~{est} lb baseline"

def estimate_working_weight_with_reps(exercise_key: str, rep_range: str, lifts: LiftInputs, goal: str) -> str:
    one_rms = {
        "bench": estimate_1rm_from_5rm(lifts.bench_5rm),
        "row": estimate_1rm_from_5rm(lifts.barbell_row_5rm),
    }

    if exercise_key == "pullup":
        if lifts.pullups_reps >= 10:
            return "Bodyweight; add 5-25 lb if reps exceed target"
        return "Bodyweight; build reps until top of range"
    if exercise_key == "pushup":
        if lifts.strict_pushups_reps >= 30:
            return "Bodyweight; add weight or elevate feet if reps exceed target"
        return "Bodyweight; build reps until top of range"

    if exercise_key == "none":
        return "Pick a load that ends with 1-2 reps left in the tank"

    base_1rm = one_rms.get(exercise_key, 0)
    if base_1rm <= 0:
        return "Not enough lift data"

    pct = get_intensity_percentage(goal, rep_range)
    est = round_to_nearest_5(base_1rm * pct)

    if "Dumbbell" in rep_range:
        return f"~{est} lb"
    return f"~{est} lb"


def adjust_program_for_target(program: List[Dict], target_build: str) -> List[Dict]:
    """
    Small emphasis adjustments based on desired style.
    """
    if target_build == "Lean Actor Build":
        for day in program:
            if "Upper" in day["focus"] or day["focus"] in ["Push", "Pull", "Upper Aesthetic", "Upper Strength", "Upper Hypertrophy"]:
                day["exercises"].append(("Vacuum Holds / Plank", "2-3", "30-45 sec", "none"))
        return program

    if target_build == "Athletic Superhero Build":
        for day in program:
            if "Conditioning" in day["focus"]:
                day["exercises"].append(("Sled Push / Intervals", "1", "8-12 min", "none"))
        return program

    if target_build == "Powerlifter Build":
        for day in program:
            if "Strength" in day["focus"] or day["focus"] in ["Push Strength", "Pull Strength", "Legs Strength", "Upper Strength", "Lower Strength"]:
                day["exercises"].append(("Paused Compound Backoff Set", "1-2", "3-5", "none"))
        return program

    return program


def generate_program(profile: UserProfile, lifts: LiftInputs) -> Tuple[str, List[Dict]]:
    split = choose_split(profile.days_per_week, profile.goal, profile.target_build)
    library = build_exercise_library()
    program = library[split]
    program = adjust_program_for_target(program, profile.target_build)
    return split, program


# =========================
# RECOVERY / SUPPLEMENT LOGIC
# =========================
def generate_recovery_recommendations(profile: UserProfile, recovery_score: float) -> List[str]:
    recs = []

    protein_per_kg = profile.protein_g / max(1.0, pounds_to_kg(profile.weight_lb))

    if profile.sleep_hours < 7:
        recs.append("Increase sleep toward 7.5-9 hours to improve recovery, performance, and muscle retention.")
    if protein_per_kg < 1.6:
        recs.append("Raise daily protein toward 1.6-2.2 g/kg bodyweight.")
    if profile.hydration_liters < 2.5:
        recs.append("Increase water intake, especially around training.")
    if profile.stress_level >= 7:
        recs.append("Reduce life/training stress: keep 1-2 reps in reserve and consider one lower-fatigue week every 4-6 weeks.")
    if profile.steps_per_day < 5000:
        recs.append("Increase daily movement slightly to improve conditioning and recovery capacity.")
    if recovery_score >= 80:
        recs.append("Recovery looks strong. Stay consistent and avoid adding junk volume.")

    return recs


def generate_supplement_recommendations(profile: UserProfile) -> List[str]:
    suggestions = [
        "Creatine monohydrate: 3-5 g daily.",
        "Protein powder only if needed to help hit your daily protein target.",
        "Electrolytes can help if you sweat heavily or train in hot conditions.",
        "Caffeine pre-workout can help performance if tolerated well."
    ]

    if profile.sleep_hours < 7:
        suggestions.append("Magnesium glycinate at night is sometimes used for relaxation, but it is not a substitute for sleep habits.")

    suggestions.append("For any remedy, supplement, or pain issue beyond general wellness, check with a licensed clinician.")
    return suggestions


# =========================
# Custom CSS for game-like UI
st.markdown("""
<style>
/* Animated vibrant background */
@keyframes gradientShift {
    0% {
        background-position: 0% 50%;
    }
    50% {
        background-position: 100% 50%;
    }
    100% {
        background-position: 0% 50%;
    }
}

/* Full page vibrant animated background */
.stApp {
    background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #667eea);
    background-size: 400% 400%;
    animation: gradientShift 15s ease infinite;
    min-height: 100vh;
}

.main {
    background: transparent;
}

/* Mobile responsive design */
@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem;
    }
}

.game-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 30px;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 20px;
}

.level-badge {
    background: linear-gradient(45deg, #ffd700, #ffed4e);
    color: #333;
    padding: 10px 20px;
    border-radius: 25px;
    font-weight: bold;
    font-size: 1.2rem;
    display: inline-block;
    margin: 10px;
}

.xp-bar {
    width: 100%;
    height: 20px;
    background: #e9ecef;
    border-radius: 10px;
    overflow: hidden;
    margin: 10px 0;
}

.xp-fill {
    height: 100%;
    background: linear-gradient(90deg, #28a745, #20c997);
    transition: width 0.3s ease;
}

.quest-card {
    background: white;
    border: 2px solid #dee2e6;
    border-radius: 15px;
    padding: 20px;
    margin: 10px 0;
    transition: all 0.3s;
}

.quest-card:hover {
    border-color: #007bff;
    box-shadow: 0 4px 8px rgba(0,123,255,0.2);
}

.quest-active {
    border-color: #28a745;
    background: rgba(40, 167, 69, 0.05);
}

.reward-badge {
    background: linear-gradient(45deg, #ff6b6b, #ee5a24);
    color: white;
    padding: 5px 10px;
    border-radius: 15px;
    font-size: 0.8rem;
    font-weight: bold;
}

.achievement-card {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    padding: 15px;
    border-radius: 10px;
    margin: 5px;
    text-align: center;
}

.stat-card {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    margin: 5px;
}

.leaderboard-item {
    display: flex;
    align-items: center;
    padding: 10px;
    background: white;
    border-radius: 8px;
    margin: 5px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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


# Check if user has account
if st.session_state.user_account is None:
    # Account Creation Screen
    st.markdown("""
    <div style="text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 20px; margin-bottom: 30px;">
        <h1>🎮 Fitness Battle Arena</h1>
        <p>Login to your character or create a new one!</p>
    </div>
    """, unsafe_allow_html=True)

    # Tab for Login vs Create Account
    login_tab, create_tab = st.tabs(["🔓 Login", "✨ Create Character"])

    with login_tab:
        st.subheader("Login to Existing Character")
        login_username = st.text_input("Enter your username", key="login_username")
        
        if st.button("⚔️ Login", type="primary", use_container_width=True):
            if login_username:
                user_data = load_user(login_username)
                if user_data:
                    st.session_state.user_account = user_data
                    st.balloons()
                    st.success(f"Welcome back, {login_username}! Level {user_data['level']}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ No character found with username '{login_username}'")
            else:
                st.error("Please enter a username")

    with create_tab:
        st.subheader("Create New Character")
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("📝 Account Details")
            username = st.text_input("Choose Username", max_chars=20, key="new_username")
            if st.button("Generate Random Name"):
                random_names = ["FitHero", "GainzMaster", "LiftLegend", "MuscleMage", "PowerPaladin", "EnduranceElf"]
                username = random.choice(random_names)
                st.rerun()

        with col2:
            st.subheader("🎭 Choose Your Avatar")

            # Avatar selection
            avatar_cols = st.columns(3)
            selected_avatar = None

            for i, (avatar_key, avatar_data) in enumerate(AVATARS.items()):
                with avatar_cols[i % 3]:
                    # Get current level gif (default to level 1)
                    current_gif = avatar_data["level_gifs"][1]

                    if st.button(f"{current_gif}\n{avatar_data['name']}", key=f"avatar_{avatar_key}"):
                        selected_avatar = avatar_key

                    st.caption(avatar_data["description"])
                    st.markdown("---")

            if selected_avatar:
                st.session_state.selected_avatar = selected_avatar
                st.success(f"Selected: {AVATARS[selected_avatar]['name']}")

        # Create account button
        if username and hasattr(st.session_state, 'selected_avatar'):
            if st.button("🚀 Create Character & Start Journey!", type="primary", use_container_width=True):
                # Check if username already exists
                if user_exists(username):
                    st.error(f"❌ Username '{username}' already taken! Try another one.")
                else:
                    # Create new user account
                    new_user = {
                        "username": username,
                        "avatar": st.session_state.selected_avatar,
                        "level": 1,
                        "xp": 0,
                        "xp_to_next": 200,
                        "achievements": ["Welcome Warrior"],
                        "join_date": time.time()
                    }

                    # Save to JSON file
                    save_user(new_user)
                    
                    # Update session state
                    st.session_state.user_account = new_user
                    st.session_state.all_users.append(new_user)
                    
                    st.balloons()
                    st.success(f"Welcome, {username}! Your fitness adventure begins now! 🎮")
                    time.sleep(2)
                    st.rerun()

        st.markdown("---")
        st.subheader("👥 Existing Players")
        sample_users = random.sample(st.session_state.all_users, min(3, len(st.session_state.all_users)))
        for user in sample_users:
            avatar_emoji = AVATARS[user["avatar"]]["level_gifs"].get(user["level"], AVATARS[user["avatar"]]["level_gifs"][1])
            st.write(f"{avatar_emoji} **{user['username']}** - Level {user['level']}")

else:
    # Main Game Interface
    user = st.session_state.user_account

    # Get current avatar based on level
    current_level = user["level"]
    avatar_data = AVATARS[user["avatar"]]

    # Find appropriate avatar gif based on level
    avatar_gif = avatar_data["level_gifs"][1]  # default
    for level_threshold in sorted(avatar_data["level_gifs"].keys(), reverse=True):
        if current_level >= level_threshold:
            avatar_gif = avatar_data["level_gifs"][level_threshold]
            break

    # Game header with avatar
    st.markdown(f"""
    <div class="game-header">
        <div style="display: flex; align-items: center; justify-content: center; gap: 20px;">
            <div style="font-size: 4rem;">{avatar_gif}</div>
            <div>
                <h1>🎮 {user["username"]}'s Fitness Quest</h1>
                <div class="level-badge">Level {user["level"]}</div>
            </div>
        </div>
        <p>XP: {user["xp"]} / {user["xp_to_next"]}</p>
        <div class="xp-bar">
            <div class="xp-fill" style="width: {user["xp"] / user["xp_to_next"] * 100}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


    # Main game tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["⚔️ Quests", "🏋️ Physique Builder", "🏆 Achievements", "📊 Stats", "👥 Leaderboard"])

    with tab1:
        st.header("⚔️ Daily Quests")

        quests = [
            {
                "title": "Complete Upper Body Workout",
                "description": "Finish all exercises in today's upper body session",
                "reward": "150 XP",
                "progress": 3,
                "total": 4,
                "active": True
            },
            {
                "title": "Hit Protein Goal",
                "description": "Consume 200g of protein today",
                "reward": "100 XP",
                "progress": 180,
                "total": 200,
                "active": True
            },
            {
                "title": "7-Day Streak",
                "description": "Work out for 7 consecutive days",
                "reward": "500 XP + Badge",
                "progress": 5,
                "total": 7,
                "active": True
            },
            {
                "title": "Bench Press PR",
                "description": "Set a new personal record",
                "reward": "200 XP",
                "progress": 0,
                "total": 1,
                "active": False
            }
        ]

        for quest in quests:
            card_class = "quest-card quest-active" if quest["active"] else "quest-card"
            progress_pct = quest["progress"] / quest["total"] * 100

            st.markdown(f"""
            <div class="{card_class}">
                <h4>{quest['title']} <span class="reward-badge">{quest['reward']}</span></h4>
                <p>{quest['description']}</p>
                <div style="margin: 10px 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <small>Progress</small>
                        <small>{quest['progress']}/{quest['total']}</small>
                    </div>
                    <div style="width: 100%; height: 8px; background: #e9ecef; border-radius: 4px;">
                        <div style="width: {progress_pct}%; height: 100%; background: linear-gradient(90deg, #28a745, #20c997); border-radius: 4px;"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if quest["active"] and st.button(f"Complete '{quest['title']}'", key=f"complete_{quest['title'].replace(' ', '_')}"):
                xp_reward = int(quest["reward"].split()[0])
                user["xp"] += xp_reward

                if user["xp"] >= user["xp_to_next"]:
                    user["level"] += 1
                    user["xp"] = user["xp"] - user["xp_to_next"]
                    user["xp_to_next"] = int(user["xp_to_next"] * 1.2)
                    st.balloons()
                    st.success(f"🎉 Level Up! You are now Level {user['level']}!")

                    # Avatar evolution message
                    new_avatar_gif = avatar_data["level_gifs"].get(user["level"], avatar_gif)
                    if new_avatar_gif != avatar_gif:
                        st.info(f"🌟 Your avatar evolved! {avatar_data['name']} is now more powerful!")

                else:
                    st.success(f"Quest completed! +{xp_reward} XP")
                
                # Save user data to JSON file
                save_user(user)
                st.session_state.user_account = user
                time.sleep(0.5)
                st.rerun()

    with tab2:
        st.header("🏋️ Physique Builder Engine")

        # Sidebar inputs for physique builder
        st.sidebar.header("⚡ Profile Setup")

        age = st.sidebar.number_input("Age", min_value=16, max_value=70, value=24)
        sex = st.sidebar.selectbox("Sex", ["Male", "Female"])
        height_in = st.sidebar.number_input("Height (inches)", min_value=55.0, max_value=84.0, value=70.0, step=0.5)
        weight_lb = st.sidebar.number_input("Weight (lb)", min_value=90.0, max_value=400.0, value=170.0, step=1.0)
        body_fat = st.sidebar.number_input("Body Fat %", min_value=5.0, max_value=45.0, value=16.0, step=0.5)

        training_age = st.sidebar.selectbox("Training Level", ["Beginner", "Novice", "Intermediate", "Advanced"])
        goal = st.sidebar.selectbox("Goal", ["Lean Bulk", "Fat Loss", "Recomp", "Strength"])
        target_build = st.sidebar.selectbox("Target Build", ["Lean Actor", "Athletic Hero", "Balanced", "Powerlifter"])

        days_per_week = st.sidebar.slider("Training Days/Week", 2, 6, 4)
        sleep_hours = st.sidebar.slider("Sleep Hours", 4.0, 10.0, 7.0, 0.5)
        stress_level = st.sidebar.slider("Stress Level (1-10)", 1, 10, 5)
        steps_per_day = st.sidebar.slider("Daily Steps", 1000, 20000, 6500, 500)
        hydration_liters = st.sidebar.slider("Water Intake (L)", 0.5, 6.0, 2.5, 0.1)
        protein_g = st.sidebar.number_input("Daily Protein (g)", 40, 350, 140, 5)
        calories = st.sidebar.number_input("Daily Calories", 1000, 6000, 2400, 50)

        st.sidebar.header("💪 Current Lifts")
        bench_5rm = st.sidebar.number_input("Bench Press 5RM (lb)", 0, 700, 165, 5)
        barbell_row_5rm = st.sidebar.number_input("Barbell Row 5RM (lb)", 0, 500, 135, 5)
        pullups_reps = st.sidebar.number_input("Pull-ups (max)", 0, 40, 6)
        strict_pushups_reps = st.sidebar.number_input("Push-ups (max)", 0, 100, 20)

        if st.sidebar.button("🚀 Generate Plan", type="primary"):
            # Create profile and calculate
            profile = UserProfile(
                age=age, sex=sex, height_in=height_in, weight_lb=weight_lb, body_fat=body_fat,
                training_age=training_age, goal=goal, target_build=target_build, days_per_week=days_per_week,
                sleep_hours=sleep_hours, stress_level=stress_level, steps_per_day=steps_per_day,
                hydration_liters=hydration_liters, protein_g=protein_g, calories=calories,
                injuries="", equipment="Full Gym"
            )

            lifts = LiftInputs(bench_5rm=bench_5rm, barbell_row_5rm=barbell_row_5rm,
                             pullups_reps=pullups_reps, strict_pushups_reps=strict_pushups_reps)

            # Calculate scores
            strength_score, ratios = compute_strength_score(profile, lifts)
            recovery_score = compute_recovery_score(profile)
            balance_score = compute_balance_score(profile, lifts)
            physique_match_score = compute_physique_match_score(profile)
            hypertrophy_score = compute_hypertrophy_score(profile, lifts)
            overall_score = compute_overall_rating(strength_score, recovery_score, balance_score, physique_match_score, hypertrophy_score)

            # Generate program
            split, program = generate_program(profile, lifts)
            recovery_recs = generate_recovery_recommendations(profile, recovery_score)
            supplement_recs = generate_supplement_recommendations(profile)

            ffmi = compute_ffmi(profile.height_in, profile.weight_lb, profile.body_fat)
            bmi = compute_bmi(profile.height_in, profile.weight_lb)

            # Display results
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            stats = [
                ("Overall", overall_score), ("Strength", strength_score), ("Recovery", recovery_score),
                ("Balance", balance_score), ("Hypertrophy", hypertrophy_score), ("Physique Match", physique_match_score)
            ]

            for col, (label, score) in zip([col1, col2, col3, col4, col5, col6], stats):
                with col:
                    st.markdown('<div class="card primary-card">', unsafe_allow_html=True)
                    st.metric(label=label, value=f"{score:.0f}/100")
                    st.progress(int(score))
                    st.markdown('</div>', unsafe_allow_html=True)

            # Program display
            st.subheader("📋 Your Training Program")
            st.info(f"**Recommended Split:** {split}")

            for day in program[:3]:  # Show first 3 days
                with st.expander(f"{day['day']} — {day['focus']}", expanded=False):
                    st.write("**Exercises:**")
                    for ex_name, sets, reps, key in day["exercises"][:4]:  # Show first 4 exercises
                        weight_hint = estimate_working_weight_with_reps(key, reps, lifts, profile.goal)
                        st.write(f"- {ex_name}: {sets} sets × {reps} reps @{weight_hint}")

            # Recovery recommendations
            st.subheader("🛌 Recovery Tips")
            for rec in recovery_recs[:3]:
                st.write(f"• {rec}")

    with tab3:
        st.header("🏆 Achievements")

        achievements = [
            {"name": "First Steps", "description": "Complete your first workout", "unlocked": True, "rarity": "Common"},
            {"name": "Consistency King", "description": "Work out for 30 consecutive days", "unlocked": True, "rarity": "Rare"},
            {"name": "Strength Master", "description": "Bench press 225+ lbs", "unlocked": True, "rarity": "Epic"},
            {"name": "Nutrition Guru", "description": "Hit protein goals for 30 days", "unlocked": False, "rarity": "Rare"},
            {"name": "Transformation", "description": "Lose 20 lbs of fat", "unlocked": False, "rarity": "Legendary"}
        ]

        unlocked_count = sum(1 for a in achievements if a["unlocked"])

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Achievements Unlocked", f"{unlocked_count}/{len(achievements)}")
        with col2:
            st.metric("Total Points", user["xp"])
        with col3:
            st.metric("Current Streak", "12 days")

        for achievement in achievements:
            if achievement["unlocked"]:
                rarity_colors = {"Common": "#6c757d", "Rare": "#007bff", "Epic": "#6f42c1", "Legendary": "#fd7e14"}
                color = rarity_colors.get(achievement["rarity"], "#6c757d")

                st.markdown(f"""
                <div class="achievement-card" style="border: 3px solid {color};">
                    <h4>🏆 {achievement['name']}</h4>
                    <p>{achievement['description']}</p>
                    <small style="opacity: 0.8;">{achievement['rarity'].upper()}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="quest-card" style="opacity: 0.6;">
                    <h4>🔒 {achievement['name']}</h4>
                    <p>{achievement['description']}</p>
                    <small>{achievement['rarity'].upper()}</small>
                </div>
                """, unsafe_allow_html=True)

    with tab4:
        st.header("📊 Character Stats")

        # Character stats grid
        stats = [
            {"name": "Strength", "value": 85, "max": 100, "color": "#dc3545"},
            {"name": "Endurance", "value": 72, "max": 100, "color": "#28a745"},
            {"name": "Recovery", "value": 68, "max": 100, "color": "#007bff"},
            {"name": "Nutrition", "value": 91, "max": 100, "color": "#ffc107"},
            {"name": "Consistency", "value": 78, "max": 100, "color": "#6f42c1"},
            {"name": "Technique", "value": 82, "max": 100, "color": "#fd7e14"}
        ]

        cols = st.columns(2)
        for i, stat in enumerate(stats):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="stat-card">
                    <h4>{stat['name']}</h4>
                    <div style="font-size: 2rem; font-weight: bold; color: {stat['color']};">
                        {stat['value']}/{stat['max']}
                    </div>
                    <div style="width: 100%; height: 8px; background: #e9ecef; border-radius: 4px; margin-top: 10px;">
                        <div style="width: {stat['value']}%; height: 100%; background: {stat['color']}; border-radius: 4px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with tab5:
        st.header("👥 Global Leaderboard")

        # Sort users by level (descending), then by XP (descending)
        sorted_users = sorted(st.session_state.all_users,
                             key=lambda x: (x["level"], x["xp"]), reverse=True)

        # Add rank to each user
        for i, user_data in enumerate(sorted_users, 1):
            user_data["rank"] = i

        # Find current user
        current_user_data = next((u for u in sorted_users if u.get("username") == user["username"]), None)

        # Show current user's rank prominently
        if current_user_data:
            rank = current_user_data["rank"]
            total_players = len(sorted_users)

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px;">
                <h3>🏆 Your Rank: #{rank} of {total_players}</h3>
                <p>You are in the top {int((total_players - rank + 1) / total_players * 100)}% of players!</p>
            </div>
            """, unsafe_allow_html=True)

        # Show top 10 players
        st.subheader("Top Champions")
        for player in sorted_users[:10]:
            is_current_user = player.get("username") == user["username"]
            bg_color = "#e3f2fd" if is_current_user else "white"
            border_style = "border: 3px solid #007bff;" if is_current_user else ""

            avatar_emoji = AVATARS[player["avatar"]]["level_gifs"].get(player["level"],
                AVATARS[player["avatar"]]["level_gifs"][1])

            # Rank badge
            rank_badge = "🥇" if player["rank"] == 1 else "🥈" if player["rank"] == 2 else "🥉" if player["rank"] == 3 else f"#{player['rank']}"

            st.markdown(f"""
            <div class="leaderboard-item" style="background: {bg_color}; {border_style}">
                <span style="font-weight: bold; margin-right: 15px; font-size: 1.2rem;">{rank_badge}</span>
                <span style="font-size: 2rem; margin-right: 10px;">{avatar_emoji}</span>
                <span style="flex-grow: 1; font-weight: bold;">{player['username']}</span>
                <span style="margin-left: 15px;">Level {player['level']}</span>
                <span style="margin-left: 15px; color: #28a745; font-weight: bold;">{player['xp']} XP</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("💬 Community Activity")
        activities = [
            f"🏆 {random.choice(sorted_users)['username']} reached Level {random.randint(5, 20)}!",
            f"💪 {random.choice(sorted_users)['username']} completed 'Upper Body Blast' (+150 XP)",
            f"🏃 {random.choice(sorted_users)['username']} hit a new cardio PR (+100 XP)",
            f"⚔️ {random.choice(sorted_users)['username']} finished their daily quest (+200 XP)",
            f"👑 {random.choice(sorted_users)['username']} unlocked 'Legendary Lifter' achievement!"
        ]

        for activity in random.sample(activities, 3):
            st.write(activity)

    # Quick actions at bottom
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("⚔️ Start Quest", use_container_width=True):
            st.info("Choose a quest from the Quests tab!")
    with col2:
        if st.button("📝 Log Workout", use_container_width=True):
            st.success("Workout logged! +50 XP")
            user["xp"] += 50
            if user["xp"] >= user["xp_to_next"]:
                user["level"] += 1
                user["xp"] = user["xp"] - user["xp_to_next"]
                user["xp_to_next"] = int(user["xp_to_next"] * 1.2)
                st.balloons()
                st.info(f"🎉 Level Up! You are now Level {user['level']}!")
            # Save user data to JSON file
            save_user(user)
            st.session_state.user_account = user
    with col3:
        if st.button("🎁 Daily Reward", use_container_width=True):
            reward_xp = random.randint(10, 50)
            user["xp"] += reward_xp
            st.success(f"Daily reward claimed! +{reward_xp} XP")
            # Save user data to JSON file
            save_user(user)
            st.session_state.user_account = user
    with col4:
        if st.button("🔄 Switch Account", use_container_width=True):
            if st.checkbox("Confirm account switch"):
                st.session_state.user_account = None
                st.rerun()
    
