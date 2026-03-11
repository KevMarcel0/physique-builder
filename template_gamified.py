import math
import statistics
from dataclasses import dataclass
from typing import Dict, List, Tuple
import streamlit as st
import random
import time

# =========================
# ENHANCED GAMIFIED EXPERIENCE WITH ACCOUNTS & AVATARS
# =========================
st.set_page_config(
    page_title="Level Up Fitness",
    page_icon="🎮",
    layout="wide"
)

# Avatar system - Minecraft-style GIF characters
AVATARS = {
    "steve": {
        "name": "Steve",
        "description": "Classic Minecraft hero",
        "base_gif": "🏃‍♂️",  # Using emojis as placeholders for GIFs
        "level_gifs": {
            1: "🧍‍♂️",  # Level 1-5: Standing
            6: "🏃‍♂️",  # Level 6-10: Running
            11: "⚔️",   # Level 11-15: Fighting
            16: "🛡️",   # Level 16-20: Shield
            21: "👑"    # Level 21+: King
        }
    },
    "alex": {
        "name": "Alex",
        "description": "Minecraft heroine",
        "base_gif": "🏃‍♀️",
        "level_gifs": {
            1: "🧍‍♀️",
            6: "🏃‍♀️",
            11: "🏹",
            16: "🛡️",
            21: "👸"
        }
    },
    "creeper": {
        "name": "Creeper",
        "description": "Sneaky explosive friend",
        "base_gif": "💚",
        "level_gifs": {
            1: "💚",
            6: "🟢",
            11: "🟡",
            16: "🟠",
            21: "🔴"
        }
    },
    "enderman": {
        "name": "Enderman",
        "description": "Tall teleporting entity",
        "base_gif": "🧑‍🚀",
        "level_gifs": {
            1: "🧑‍🚀",
            6: "🚀",
            11: "🌌",
            16: "⭐",
            21: "👑"
        }
    },
    "iron_golem": {
        "name": "Iron Golem",
        "description": "Protective village guardian",
        "base_gif": "🤖",
        "level_gifs": {
            1: "🤖",
            6: "⚙️",
            11: "🔧",
            16: "🛡️",
            21: "👑"
        }
    }
}

# Initialize session state
if 'user_account' not in st.session_state:
    st.session_state.user_account = None
if 'all_users' not in st.session_state:
    # Mock user database
    st.session_state.all_users = [
        {"username": "ProLifter", "avatar": "steve", "level": 12, "xp": 3200, "xp_to_next": 3600},
        {"username": "FitWarrior", "avatar": "alex", "level": 8, "xp": 1950, "xp_to_next": 2200},
        {"username": "GainsMaster", "avatar": "iron_golem", "level": 15, "xp": 4800, "xp_to_next": 5200},
        {"username": "CreeperKing", "avatar": "creeper", "level": 6, "xp": 1450, "xp_to_next": 1700},
        {"username": "EnderBoss", "avatar": "enderman", "level": 10, "xp": 2650, "xp_to_next": 2900},
    ]

# Custom CSS for game-like UI
st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)

# Check if user has account
if st.session_state.user_account is None:
    # Account Creation Screen
    st.markdown("""
    <div style="text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 20px; margin-bottom: 30px;">
        <h1>🎮 Create Your Fitness Character</h1>
        <p>Choose your avatar and start your fitness journey!</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📝 Account Details")
        username = st.text_input("Choose Username", max_chars=20)
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

            st.session_state.user_account = new_user
            st.session_state.all_users.append(new_user)
            st.balloons()
            st.success(f"Welcome, {username}! Your fitness adventure begins now!")
            time.sleep(2)
            st.rerun()

    st.markdown("---")
    st.subheader("👥 Existing Players")
    for user in random.sample(st.session_state.all_users, min(3, len(st.session_state.all_users))):
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
tab1, tab2, tab3, tab4 = st.tabs(["⚔️ Quests", "🏆 Achievements", "📊 Stats", "👥 Social"])

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
            time.sleep(0.5)
            st.rerun()

with tab2:
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
            rarity_colors = {
                "Common": "#6c757d",
                "Rare": "#007bff",
                "Epic": "#6f42c1",
                "Legendary": "#fd7e14"
            }
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

with tab3:
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

    # Recent activity
    st.subheader("Recent Level Ups")
    activities = [
        {"action": "Completed Upper Body Quest", "xp": "+150", "time": "2 hours ago"},
        {"action": "Hit Protein Goal", "xp": "+100", "time": "1 day ago"},
        {"action": "New Bench PR", "xp": "+200", "time": "3 days ago"},
        {"action": "7-Day Streak", "xp": "+500", "time": "1 week ago"}
    ]

    for activity in activities:
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; background: #f8f9fa; border-radius: 8px; margin: 5px 0;">
            <span>{activity['action']}</span>
            <span style="color: #28a745; font-weight: bold;">{activity['xp']} XP</span>
        </div>
        """, unsafe_allow_html=True)

with tab4:
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
with col3:
    if st.button("🎁 Daily Reward", use_container_width=True):
        reward_xp = random.randint(10, 50)
        user["xp"] += reward_xp
        st.success(f"Daily reward claimed! +{reward_xp} XP")
with col4:
    if st.button("🔄 Switch Account", use_container_width=True):
        if st.checkbox("Confirm account switch"):
            st.session_state.user_account = None
            st.rerun()