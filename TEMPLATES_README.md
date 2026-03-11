# Physique Builder - UI Templates

This repository contains multiple user-friendly templates for the Physique Builder fitness application. Each template demonstrates a different approach to making fitness tracking more engaging and intuitive.

## Available Templates

### 1. Wizard Template (`template_wizard.py`)
**Best for:** New users, guided onboarding
- Step-by-step setup process
- Progress indicators
- Form-based input collection
- Clear navigation between steps

**Key Features:**
- 5-step wizard flow (Profile → Goals → Lifts → Review → Results)
- Progress bar showing completion status
- Back/Next navigation
- Form validation
- Success animations

### 2. Dashboard Template (`template_dashboard.py`)
**Best for:** Power users, comprehensive tracking
- Tabbed interface for different functions
- Visual progress charts
- Goal tracking with progress bars
- Settings management

**Key Features:**
- 4 main tabs: Today's Workout, Progress, Goals, Settings
- Interactive charts and graphs
- Goal progress visualization
- Workout logging with checkboxes
- Comprehensive settings

### 3. Mobile-Friendly Template (`template_mobile.py`)
**Best for:** Mobile users, quick interactions
- Card-based layout
- Touch-friendly buttons
- Progress circles
- Activity feed

**Key Features:**
- Responsive card design
- Quick action buttons
- Visual progress indicators
- Recent activity timeline
- Mobile-optimized input forms

### 4. Gamified Template (`template_gamified.py`)
**Best for:** Motivating users, long-term engagement
- RPG-style progression system
- Achievement system
- XP and leveling mechanics
- Quest-based tasks

**Key Features:**
- Level/XP progression
- Achievement unlocks
- Daily quests with rewards
- Leaderboard system
- Character stats
- Social features

## How to Run Templates

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run any template:
```bash
streamlit run template_wizard.py
# or
streamlit run template_dashboard.py
# or
streamlit run template_mobile.py
# or
streamlit run template_gamified.py
```

## Template Comparison

| Feature | Wizard | Dashboard | Mobile | Gamified |
|---------|--------|-----------|--------|----------|
| Best For | Beginners | Power Users | Mobile | Motivation |
| Complexity | Low | High | Medium | Medium |
| Onboarding | Guided | Self-guided | Quick | Fun |
| Data Entry | Forms | Direct input | Quick add | Quest-based |
| Visualization | Minimal | Charts | Cards | Game UI |
| Engagement | Linear | Comprehensive | Fast | Addictive |

## Customization

Each template can be customized by:
- Modifying the CSS styles
- Adding/removing features
- Changing color schemes
- Adjusting layouts
- Integrating with real data sources

## Original App

The original `app.py` contains the core fitness calculation engine. These templates demonstrate different ways to present that functionality in a more user-friendly manner.

## Contributing

Feel free to create new templates or improve existing ones by:
- Adding new UI patterns
- Improving mobile responsiveness
- Adding new gamification elements
- Enhancing accessibility
- Integrating with fitness APIs</content>
<parameter name="filePath">/workspaces/physique-builder/TEMPLATES_README.md