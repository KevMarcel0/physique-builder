import math
import statistics
from dataclasses import dataclass
from typing import Dict, List, Tuple

import streamlit as st


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Physique Builder Engine",
    page_icon="🎮",
    layout="wide"
)


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
    protein_g: float
    calories: int
    injuries: str
    equipment: str


@dataclass
class LiftInputs:
    bench_5rm: float
    squat_5rm: float
    deadlift_5rm: float
    overhead_press_5rm: float
    barbell_row_5rm: float
    pullups_reps: int


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
    squat_1rm = estimate_1rm_from_5rm(lifts.squat_5rm)
    deadlift_1rm = estimate_1rm_from_5rm(lifts.deadlift_5rm)
    ohp_1rm = estimate_1rm_from_5rm(lifts.overhead_press_5rm)
    row_1rm = estimate_1rm_from_5rm(lifts.barbell_row_5rm)

    ratios = {
        "Bench/BW": bench_1rm / bw,
        "Squat/BW": squat_1rm / bw,
        "Deadlift/BW": deadlift_1rm / bw,
        "OHP/BW": ohp_1rm / bw,
        "Row/BW": row_1rm / bw,
        "Pull-Ups": lifts.pullups_reps
    }

    score_parts = [
        normalize_ratio_score(ratios["Bench/BW"], 0.75, 1.5),
        normalize_ratio_score(ratios["Squat/BW"], 1.0, 2.25),
        normalize_ratio_score(ratios["Deadlift/BW"], 1.25, 2.75),
        normalize_ratio_score(ratios["OHP/BW"], 0.45, 0.95),
        normalize_ratio_score(ratios["Row/BW"], 0.60, 1.25),
        normalize_ratio_score(ratios["Pull-Ups"], 0, 15),
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
    squat_1rm = estimate_1rm_from_5rm(lifts.squat_5rm)
    deadlift_1rm = estimate_1rm_from_5rm(lifts.deadlift_5rm)
    ohp_1rm = estimate_1rm_from_5rm(lifts.overhead_press_5rm)

    push_pull_ratio = bench_1rm / max(row_1rm, 1)
    squat_hinge_ratio = squat_1rm / max(deadlift_1rm, 1)
    upper_balance_ratio = ohp_1rm / max(bench_1rm, 1)

    push_pull_score = 100 - abs(push_pull_ratio - 1.0) * 55
    squat_hinge_score = 100 - abs(squat_hinge_ratio - 0.85) * 70
    upper_balance_score = 100 - abs(upper_balance_ratio - 0.65) * 100

    days_score = normalize_ratio_score(profile.days_per_week, 2, 6)

    score = statistics.mean([
        clamp(push_pull_score, 0, 100),
        clamp(squat_hinge_score, 0, 100),
        clamp(upper_balance_score, 0, 100),
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
                ("Back Squat", "3-4", "5-6", "squat"),
                ("Bench Press", "3-4", "5-6", "bench"),
                ("Barbell Row", "3-4", "6-8", "row"),
                ("Romanian Deadlift", "3", "8-10", "deadlift"),
                ("Lateral Raise", "3", "12-15", "none"),
                ("Cable Crunch", "3", "12-15", "none"),
            ]},
            {"day": "Day 2", "focus": "Hypertrophy + Pull Emphasis", "exercises": [
                ("Deadlift", "3", "4-5", "deadlift"),
                ("Overhead Press", "3-4", "5-8", "ohp"),
                ("Lat Pulldown / Pull-Up", "3-4", "6-10", "pullup"),
                ("Bulgarian Split Squat", "3", "8-10", "none"),
                ("Incline Dumbbell Press", "3", "8-12", "bench"),
                ("Hammer Curl", "3", "10-12", "none"),
            ]},
            {"day": "Day 3", "focus": "Balanced Volume", "exercises": [
                ("Front Squat or Leg Press", "3", "6-10", "squat"),
                ("Incline Bench Press", "3-4", "6-8", "bench"),
                ("Chest-Supported Row", "3-4", "8-10", "row"),
                ("Hip Hinge Machine / RDL", "3", "8-10", "deadlift"),
                ("Cable Lateral Raise", "3", "12-15", "none"),
                ("Triceps Pushdown", "3", "10-12", "none"),
            ]},
        ],
        "Upper / Lower x4": [
            {"day": "Day 1", "focus": "Upper Strength", "exercises": [
                ("Bench Press", "4", "5-6", "bench"),
                ("Barbell Row", "4", "6-8", "row"),
                ("Overhead Press", "3", "5-6", "ohp"),
                ("Pull-Up / Lat Pulldown", "3", "6-10", "pullup"),
                ("Incline Dumbbell Press", "3", "8-10", "bench"),
                ("Lateral Raise", "3", "12-15", "none"),
                ("EZ-Bar Curl", "3", "10-12", "none"),
            ]},
            {"day": "Day 2", "focus": "Lower Strength", "exercises": [
                ("Back Squat", "4", "5-6", "squat"),
                ("Romanian Deadlift", "3", "6-8", "deadlift"),
                ("Walking Lunge", "3", "8-10/leg", "none"),
                ("Leg Curl", "3", "10-12", "none"),
                ("Calf Raise", "4", "10-15", "none"),
                ("Hanging Leg Raise", "3", "10-15", "none"),
            ]},
            {"day": "Day 3", "focus": "Upper Hypertrophy", "exercises": [
                ("Incline Bench Press", "4", "6-8", "bench"),
                ("Chest-Supported Row", "4", "8-10", "row"),
                ("Seated Dumbbell Shoulder Press", "3", "8-10", "ohp"),
                ("Lat Pulldown", "3", "8-12", "pullup"),
                ("Cable Fly", "3", "12-15", "none"),
                ("Cable Lateral Raise", "4", "12-20", "none"),
                ("Skull Crusher", "3", "10-12", "none"),
                ("Incline Curl", "3", "10-12", "none"),
            ]},
            {"day": "Day 4", "focus": "Lower Hypertrophy + Conditioning", "exercises": [
                ("Front Squat / Hack Squat", "3-4", "6-10", "squat"),
                ("RDL or Hip Thrust", "3", "8-10", "deadlift"),
                ("Bulgarian Split Squat", "3", "8-10/leg", "none"),
                ("Leg Extension", "3", "12-15", "none"),
                ("Seated Leg Curl", "3", "12-15", "none"),
                ("Standing Calf Raise", "4", "12-15", "none"),
                ("Bike / Incline Walk", "1", "12-20 min", "none"),
            ]},
        ],
        "Push / Pull / Legs / Upper / Lower": [
            {"day": "Day 1", "focus": "Push", "exercises": [
                ("Bench Press", "4", "5-6", "bench"),
                ("Incline Dumbbell Press", "3", "8-10", "bench"),
                ("Seated Dumbbell Press", "3", "8-10", "ohp"),
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
            {"day": "Day 3", "focus": "Legs", "exercises": [
                ("Back Squat", "4", "5-6", "squat"),
                ("Romanian Deadlift", "3", "6-8", "deadlift"),
                ("Leg Press", "3", "10-12", "none"),
                ("Leg Curl", "3", "10-12", "none"),
                ("Calf Raise", "4", "12-15", "none"),
                ("Cable Crunch", "3", "12-15", "none"),
            ]},
            {"day": "Day 4", "focus": "Upper Aesthetic", "exercises": [
                ("Incline Bench Press", "4", "6-8", "bench"),
                ("Chest-Supported Row", "4", "8-10", "row"),
                ("Overhead Press", "3", "5-8", "ohp"),
                ("Lat Pulldown", "3", "8-12", "pullup"),
                ("Cable Lateral Raise", "4", "12-20", "none"),
                ("Cable Curl", "3", "10-12", "none"),
                ("Overhead Rope Extension", "3", "10-12", "none"),
            ]},
            {"day": "Day 5", "focus": "Lower + Conditioning", "exercises": [
                ("Front Squat / Hack Squat", "3-4", "6-10", "squat"),
                ("Hip Thrust / RDL", "3", "8-10", "deadlift"),
                ("Walking Lunge", "3", "8-10/leg", "none"),
                ("Leg Extension", "3", "12-15", "none"),
                ("Seated Leg Curl", "3", "12-15", "none"),
                ("Incline Walk / Bike", "1", "15-20 min", "none"),
            ]},
        ],
        "Push / Pull / Legs / Upper / Lower / Arms+Conditioning": [
            {"day": "Day 1", "focus": "Push Strength", "exercises": [
                ("Bench Press", "4", "4-6", "bench"),
                ("Incline Dumbbell Press", "3", "8-10", "bench"),
                ("Overhead Press", "3", "5-6", "ohp"),
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
            {"day": "Day 3", "focus": "Legs Strength", "exercises": [
                ("Back Squat", "4", "4-6", "squat"),
                ("Romanian Deadlift", "3", "6-8", "deadlift"),
                ("Leg Press", "3", "10-12", "none"),
                ("Leg Curl", "3", "10-12", "none"),
                ("Standing Calf Raise", "4", "12-15", "none"),
            ]},
            {"day": "Day 4", "focus": "Upper Aesthetic", "exercises": [
                ("Incline Bench Press", "4", "6-8", "bench"),
                ("Lat Pulldown", "4", "8-12", "pullup"),
                ("Seated Dumbbell Shoulder Press", "3", "8-10", "ohp"),
                ("Cable Lateral Raise", "4", "12-20", "none"),
                ("Cable Fly", "3", "12-15", "none"),
                ("Cable Curl", "3", "10-12", "none"),
                ("Overhead Rope Extension", "3", "10-12", "none"),
            ]},
            {"day": "Day 5", "focus": "Lower Volume + Core", "exercises": [
                ("Front Squat / Hack Squat", "3-4", "6-10", "squat"),
                ("Hip Thrust / RDL", "3", "8-10", "deadlift"),
                ("Bulgarian Split Squat", "3", "8-10/leg", "none"),
                ("Leg Extension", "3", "12-15", "none"),
                ("Seated Leg Curl", "3", "12-15", "none"),
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
        "squat": estimate_1rm_from_5rm(lifts.squat_5rm),
        "deadlift": estimate_1rm_from_5rm(lifts.deadlift_5rm),
        "ohp": estimate_1rm_from_5rm(lifts.overhead_press_5rm),
        "row": estimate_1rm_from_5rm(lifts.barbell_row_5rm),
    }

    if exercise_key == "pullup":
        return "Bodyweight or weighted as able"
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
        "squat": estimate_1rm_from_5rm(lifts.squat_5rm),
        "deadlift": estimate_1rm_from_5rm(lifts.deadlift_5rm),
        "ohp": estimate_1rm_from_5rm(lifts.overhead_press_5rm),
        "row": estimate_1rm_from_5rm(lifts.barbell_row_5rm),
    }

    if exercise_key == "pullup":
        if lifts.pullups_reps >= 10:
            return "Bodyweight; add 5-25 lb if reps exceed target"
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
# UI STYLING
# =========================
st.markdown("""
<style>
.main-title {
    font-size: 2.2rem;
    font-weight: 800;
    margin-bottom: 0.2rem;
}
.sub-title {
    font-size: 1.0rem;
    color: #9aa0a6;
    margin-bottom: 1.2rem;
}
.stat-box {
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px;
    padding: 18px;
    background: rgba(255,255,255,0.03);
}
.section-card {
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 16px;
    background: rgba(255,255,255,0.03);
}
.small-muted {
    color: #9aa0a6;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)


# =========================
# HEADER
# =========================
st.markdown('<div class="main-title">🎮 Physique Builder Engine</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Build a balanced workout plan, recovery score, and target-physique roadmap.</div>',
    unsafe_allow_html=True
)


# =========================
# SIDEBAR INPUTS
# =========================
st.sidebar.header("Profile")

age = st.sidebar.number_input("Age", min_value=16, max_value=70, value=24)
sex = st.sidebar.selectbox("Sex", ["Male", "Female"])
height_in = st.sidebar.number_input("Height (inches)", min_value=55.0, max_value=84.0, value=70.0, step=0.5)
weight_lb = st.sidebar.number_input("Weight (lb)", min_value=90.0, max_value=400.0, value=170.0, step=1.0)
body_fat = st.sidebar.number_input("Estimated Body Fat %", min_value=5.0, max_value=45.0, value=16.0, step=0.5)

training_age = st.sidebar.selectbox("Training Age", ["Beginner", "Novice", "Intermediate", "Advanced"])
goal = st.sidebar.selectbox("Goal", ["Lean Bulk", "Fat Loss", "Recomp", "Strength"])
target_build = st.sidebar.selectbox(
    "Target Build Style",
    ["Lean Actor Build", "Athletic Superhero Build", "Balanced Aesthetic Build", "Powerlifter Build"]
)

days_per_week = st.sidebar.slider("Training Days Per Week", 2, 6, 4)
sleep_hours = st.sidebar.slider("Sleep Hours", 4.0, 10.0, 7.0, 0.5)
stress_level = st.sidebar.slider("Stress Level (1 low - 10 high)", 1, 10, 5)
steps_per_day = st.sidebar.slider("Average Steps Per Day", 1000, 20000, 6500, 500)
hydration_liters = st.sidebar.slider("Water Intake (liters/day)", 0.5, 6.0, 2.5, 0.1)
protein_g = st.sidebar.number_input("Daily Protein (g)", min_value=40.0, max_value=350.0, value=140.0, step=5.0)
calories = st.sidebar.number_input("Daily Calories", min_value=1000, max_value=6000, value=2400, step=50)
injuries = st.sidebar.text_area("Injuries / Limitations", "")
equipment = st.sidebar.selectbox("Equipment", ["Full Gym", "Dumbbells + Bench", "Home Gym", "Machines Mostly"])

st.sidebar.header("Current Lift Inputs")
bench_5rm = st.sidebar.number_input("Bench Press 5RM (lb)", min_value=0.0, max_value=700.0, value=165.0, step=5.0)
squat_5rm = st.sidebar.number_input("Back Squat 5RM (lb)", min_value=0.0, max_value=900.0, value=225.0, step=5.0)
deadlift_5rm = st.sidebar.number_input("Deadlift 5RM (lb)", min_value=0.0, max_value=1000.0, value=275.0, step=5.0)
overhead_press_5rm = st.sidebar.number_input("Overhead Press 5RM (lb)", min_value=0.0, max_value=400.0, value=95.0, step=5.0)
barbell_row_5rm = st.sidebar.number_input("Barbell Row 5RM (lb)", min_value=0.0, max_value=500.0, value=135.0, step=5.0)
pullups_reps = st.sidebar.number_input("Strict Pull-Up Reps", min_value=0, max_value=40, value=6, step=1)

run_engine = st.sidebar.button("Generate Build Plan")


# =========================
# MAIN ENGINE
# =========================
if run_engine:
    profile = UserProfile(
        age=age,
        sex=sex,
        height_in=height_in,
        weight_lb=weight_lb,
        body_fat=body_fat,
        training_age=training_age,
        goal=goal,
        target_build=target_build,
        days_per_week=days_per_week,
        sleep_hours=sleep_hours,
        stress_level=stress_level,
        steps_per_day=steps_per_day,
        hydration_liters=hydration_liters,
        protein_g=protein_g,
        calories=calories,
        injuries=injuries,
        equipment=equipment
    )

    lifts = LiftInputs(
        bench_5rm=bench_5rm,
        squat_5rm=squat_5rm,
        deadlift_5rm=deadlift_5rm,
        overhead_press_5rm=overhead_press_5rm,
        barbell_row_5rm=barbell_row_5rm,
        pullups_reps=pullups_reps
    )

    strength_score, ratios = compute_strength_score(profile, lifts)
    recovery_score = compute_recovery_score(profile)
    balance_score = compute_balance_score(profile, lifts)
    physique_match_score = compute_physique_match_score(profile)
    hypertrophy_score = compute_hypertrophy_score(profile, lifts)
    overall_score = compute_overall_rating(
        strength_score, recovery_score, balance_score, physique_match_score, hypertrophy_score
    )

    split, program = generate_program(profile, lifts)
    recovery_recs = generate_recovery_recommendations(profile, recovery_score)
    supplement_recs = generate_supplement_recommendations(profile)

    ffmi = compute_ffmi(profile.height_in, profile.weight_lb, profile.body_fat)
    bmi = compute_bmi(profile.height_in, profile.weight_lb)

    # =========================
    # TOP STATS
    # =========================
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    stats = [
        ("Overall", overall_score),
        ("Strength", strength_score),
        ("Recovery", recovery_score),
        ("Balance", balance_score),
        ("Hypertrophy", hypertrophy_score),
        ("Physique Match", physique_match_score),
    ]

    for col, (label, score) in zip([c1, c2, c3, c4, c5, c6], stats):
        with col:
            st.markdown('<div class="stat-box">', unsafe_allow_html=True)
            st.metric(label=label, value=f"{score:.0f}/100", delta=f"Tier {score_to_grade(score)}")
            st.progress(int(score))
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")

    # =========================
    # BODY METRICS
    # =========================
    left, right = st.columns([1, 1])

    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("📊 Body Metrics")
        st.write(f"**BMI:** {bmi:.1f}")
        st.write(f"**FFMI:** {ffmi:.1f}")
        st.write(f"**Protein per kg:** {profile.protein_g / max(1.0, pounds_to_kg(profile.weight_lb)):.2f} g/kg")
        st.write(f"**Recommended Split:** {split}")
        st.write(f"**Goal:** {profile.goal}")
        st.write(f"**Target Style:** {profile.target_build}")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("🏋️ Strength Ratios")
        for k, v in ratios.items():
            if k == "Pull-Ups":
                st.write(f"**{k}:** {v}")
            else:
                st.write(f"**{k}:** {v:.2f}")
        st.markdown("</div>", unsafe_allow_html=True)

    # =========================
    # PROGRAM
    # =========================
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("🧩 Custom Training Program")

    for day in program:
        with st.expander(f"{day['day']} — {day['focus']}", expanded=False):
            st.write("**Workout Table**")
            table_rows = []
            for ex_name, sets, reps, key in day["exercises"]:
                weight_hint = estimate_working_weight_with_reps(key, reps, lifts, profile.goal)
                table_rows.append({
                    "Exercise": ex_name,
                    "Sets": sets,
                    "Reps": reps,
                    "Suggested Working Weight": weight_hint
                })
            st.table(table_rows)

    st.markdown("</div>", unsafe_allow_html=True)

    # =========================
    # GAME-LIKE BUILD REPORT
    # =========================
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("🎯 Build Report")

    weaknesses = []
    if recovery_score < 70:
        weaknesses.append("Recovery")
    if balance_score < 70:
        weaknesses.append("Structural balance")
    if strength_score < 70:
        weaknesses.append("Base strength")
    if hypertrophy_score < 70:
        weaknesses.append("Muscle-building support")
    if physique_match_score < 70:
        weaknesses.append("Current body composition vs target look")

    strengths = []
    if recovery_score >= 75:
        strengths.append("Recovery habits")
    if balance_score >= 75:
        strengths.append("Movement balance")
    if strength_score >= 75:
        strengths.append("Base strength")
    if hypertrophy_score >= 75:
        strengths.append("Growth potential")
    if physique_match_score >= 75:
        strengths.append("Good match to target style")

    if not weaknesses:
        weaknesses.append("No major red flags detected")
    if not strengths:
        strengths.append("You have room to build across all categories")

    st.write(f"**Player Rank:** {score_to_grade(overall_score)}")
    st.write(f"**Primary Strengths:** {', '.join(strengths)}")
    st.write(f"**Main Bottlenecks:** {', '.join(weaknesses)}")

    if profile.target_build == "Lean Actor Build":
        st.write("**Target Look Focus:** Keep waist tight, build upper chest, lats, delts, and visible arm definition without oversized bulk.")
    elif profile.target_build == "Athletic Superhero Build":
        st.write("**Target Look Focus:** Emphasize shoulders, chest, upper back, athletic legs, and strong conditioning.")
    elif profile.target_build == "Powerlifter Build":
        st.write("**Target Look Focus:** Maximize squat, bench, and deadlift performance with enough accessory volume to stay healthy.")
    else:
        st.write("**Target Look Focus:** Balanced size, good proportions, and strong all-around training.")

    st.markdown("</div>", unsafe_allow_html=True)

    # =========================
    # RECOVERY / SUPPLEMENTS
    # =========================
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("🛌 Recovery Recommendations")
        for item in recovery_recs:
            st.write(f"- {item}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("🧪 Supplement Suggestions")
        for item in supplement_recs:
            st.write(f"- {item}")
        st.markdown("</div>", unsafe_allow_html=True)

    # =========================
    # PROGRESSION RULES
    # =========================
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("📈 Progression Algorithm")
    st.code(
        """For each exercise:
1. Start with the suggested working weight.
2. Stay 1-2 reps away from failure on most sets.
3. When you hit the TOP of the rep range for all work sets:
      increase upper-body lifts by 5 lb
      increase lower-body lifts by 5-10 lb
4. If performance drops for 2 weeks:
      reduce volume by 25-35% for 1 week
5. If sleep/stress is poor:
      keep the weight but perform 1 less set
6. Re-test estimated 5RM every 6-8 weeks
        """,
        language="text"
    )
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("Enter your profile in the sidebar and click **Generate Build Plan**.")
    st.markdown("""
### What this app does
- Scores your current training status like a game character build
- Recommends a split based on your schedule
- Gives sets, reps, and estimated working weights
- Suggests recovery and supplement basics
- Tries to align your training style with your target physique

### Important note
This estimates a **physique style**, not an exact celebrity body. Bone structure, height, proportions, and genetics matter too.
""")
    
