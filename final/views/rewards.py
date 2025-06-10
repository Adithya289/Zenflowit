import streamlit as st
from models.rewards import Reward
from streamlit_extras.let_it_rain import rain
import os
import base64
import pathlib

def get_unearned_badge_tagline(badge):
    """Generate a meaningful tagline for unearned badges"""
    condition_type = badge['condition_type']
    condition_value = badge['condition_value']
    
    taglines = {
        'task_completion': f"Complete your first task to earn this badge.",
        'focus_session': f"Complete a focus session to earn this badge.",
        'consecutive_days': f"Use the app for {condition_value} consecutive days to earn this badge.",
        'focus_sessions_total': f"Complete {condition_value} focus sessions to unlock this badge.",
        'consecutive_tasks': f"Complete {condition_value} tasks in a row to earn this badge.",
        'vision_board_created': f"Create your first vision board to earn this badge.",
        'tasks_total': f"Complete {condition_value} tasks to earn this badge."
    }
    
    return taglines.get(condition_type, "Continue using ZenFlow to unlock this badge.")

def get_badge_image_path(relative_path):
    """Convert relative badge path to absolute path"""
    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(workspace_root, relative_path)

def get_badge_image_as_base64(image_path):
    """Safely convert an image to base64 string with error handling"""
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        return None
    except Exception:
        return None

def get_milestone_message(reward_name):
    """Get celebratory message for each milestone"""
    messages = {
        "First Task": "🌟 Amazing start! You've taken your first step towards better productivity!",
        "Focus Master": "🎯 Incredible focus! You've mastered the art of concentration!",
        "Consistency Champion": "🔥 Three days in a row! Your dedication is truly inspiring!",
        "Focus Pro": "⚡ Five focus sessions complete! You're becoming a productivity powerhouse!",
        "Task Master": "📝 Three tasks in a row! You're on fire with your task management!",
        "Vision Creator": "🎨 Beautiful vision board! You're turning your dreams into plans!",
        "Focus Legend": "👑 Ten focus sessions! You've achieved legendary focus status!",
        "Task Legend": "🏆 Ten tasks complete! You're a true task management champion!"
    }
    return messages.get(reward_name, "🎉 Congratulations on your achievement!")

def show_celebration_effect():
    """Show a celebration effect when entering the rewards page"""
    rain(
        emoji="🎉",
        font_size=54,
        falling_speed=5,
        animation_length=1
    )

def show_rewards_page():
    """Display the rewards page with user's badges and achievements"""
    # Add warning banner at the top
    st.warning("""
        Stay tuned for more badges, achievements, and an enhanced reward system!
    """)
    
    # Get current user
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("Please log in to view your rewards")
        return

    # Apply global styles for the page including animation keyframes
    st.markdown("""
    <style>
    @keyframes fadeInAndPulse {
        0% { filter: grayscale(100%); opacity: 0.6; transform: scale(1); }
        50% { filter: grayscale(0); opacity: 1; transform: scale(1.1); }
        75% { filter: grayscale(0); opacity: 1; transform: scale(1); }
        100% { filter: grayscale(0); opacity: 1; transform: scale(1.05); }
    }
    .badge-card {
        text-align: center;
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .badge-image {
        width: 120px;
        height: auto;
        margin: 0 auto;
    }
    .badge-name {
        margin-bottom: 5px;
        font-weight: bold;
        font-size: 1.1rem;
        color: #333;
    }
    .badge-description {
        color: #666;
        font-size: 1rem;
        line-height: 1.4;
        margin-bottom: 15px;
    }
    .badge-earned-date {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 10px;
        font-size: 0.9rem;
        color: #666;
    }
    .badge-animation {
        animation: fadeInAndPulse 3s;
    }
    .badge-greyscale {
        filter: grayscale(100%);
        opacity: 0.6;
    }
    .notification-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        border: 1px solid #e0e0e0;
        text-align: center;
    }
    .notification-title {
        color: #1E88E5;
        margin-bottom: 10px;
    }
    .notification-image {
        width: 100px;
        height: auto;
        margin: 15px 0;
    }
    .notification-name {
        color: #1E88E5;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .notification-description {
        color: #666;
        font-size: 1rem;
    }
    .newly-earned-highlight {
        box-shadow: 0 0 15px #FFD700;
        border: 2px solid #FFD700;
    }
    </style>
    """, unsafe_allow_html=True)

    # Check for newly earned rewards and show celebration
    newly_earned_rewards = []
    if 'new_rewards' in st.session_state and st.session_state.new_rewards:
        # Only show celebrations for the current user's rewards
        for reward in st.session_state.new_rewards[:]:
            if reward.get('user_id') == user_id:
                newly_earned_rewards.append(reward)
                # Remove processed rewards to prevent showing again
                st.session_state.new_rewards.remove(reward)
        
        # Show celebration if there are new rewards for this user
        if newly_earned_rewards:
            show_celebration_effect()
            
            # Show notification for each newly earned badge
            for reward in newly_earned_rewards:
                show_reward_notification(
                    reward['name'], 
                    reward['description'],
                    reward['badge_image_path']
                )
    
    # Also show celebration if we just arrived from completing a task
    elif st.session_state.get("just_completed_task", False):
        show_celebration_effect()
    
    st.markdown("<h1 style='text-align: center; color: #1E88E5; margin-bottom: 2rem;'>🏆 Your Rewards</h1>", unsafe_allow_html=True)
    
    # Fetch all badges and user's earned badges
    all_badges = Reward.get_all_rewards()
    user_badges = {r['id']: r for r in Reward.get_user_rewards(user_id)}
    
    # Determine if any badges were just earned
    just_earned_badge_ids = [r['id'] for r in newly_earned_rewards] if newly_earned_rewards else []
    
    # Display badges in rows of 3
    for i in range(0, len(all_badges), 3):
        row_badges = all_badges[i:i+3]
        cols = st.columns(3)
        for col, badge in zip(cols, row_badges):
            with col:
                badge_path = get_badge_image_path(badge['badge_image_path'])
                earned = badge['id'] in user_badges
                newly_earned = badge['id'] in just_earned_badge_ids
                
                # Get badge image as base64
                img_data = get_badge_image_as_base64(badge_path)
                
                # Create badge HTML with classes instead of inline styles
                if img_data:
                    # Create image HTML with different classes based on badge state
                    img_class = "badge-animation" if newly_earned else ("badge-greyscale" if not earned else "")
                    img_html = f'<div><img src="data:image/png;base64,{img_data}" class="badge-image {img_class}" alt="{badge["name"]}"></div>'
                else:
                    img_html = '<div>Badge image not found</div>'
                
                # Add highlight class for newly earned badges
                highlight_class = " newly-earned-highlight" if newly_earned else ""
                
                # Create the badge card with appropriate classes
                st.markdown(f"""
                    <div class="badge-card{highlight_class}">
                        {img_html}
                        <div class="badge-name">{badge['name']}</div>
                        <div class="badge-description">
                            {badge['description'] if earned else get_unearned_badge_tagline(badge)}
                        </div>
                        {f'<div class="badge-earned-date">Earned on: {user_badges[badge["id"]]["earned_at"].strftime("%B %d, %Y")}</div>' if earned else ''}
                    </div>
                """, unsafe_allow_html=True)
    
    # Clear the just_completed_task flag after displaying the rewards
    if st.session_state.get("just_completed_task", False):
        st.session_state.just_completed_task = False
        if "just_completed_task_id" in st.session_state:
            del st.session_state.just_completed_task_id

def show_reward_notification(reward_name, reward_description, badge_path):
    """Display a notification when a reward is earned"""
    rain(
        emoji="🎉",
        font_size=54,
        falling_speed=5,
        animation_length=1
    )
    
    # Get the milestone message
    celebration_message = get_milestone_message(reward_name)
    
    # Get badge image as base64
    badge_path = get_badge_image_path(badge_path)
    img_data = get_badge_image_as_base64(badge_path)
    
    # Create the notification HTML using classes instead of inline styles
    if img_data:
        img_html = f'<img src="data:image/png;base64,{img_data}" class="notification-image" alt="{reward_name}">'
    else:
        img_html = '<div>Badge image not found</div>'
    
    # Display the notification
    st.markdown(f"""
        <div class="notification-card">
            <h3 class="notification-title">{celebration_message}</h3>
            <div>{img_html}</div>
            <div class="notification-name">{reward_name}</div>
            <div class="notification-description">{reward_description}</div>
        </div>
    """, unsafe_allow_html=True)