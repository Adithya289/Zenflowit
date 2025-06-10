import streamlit as st
import os
from dotenv import load_dotenv
import psycopg2
from utils.db import init_db, get_db_connection
from utils.theme import apply_theme_aware_styles, get_theme_colors
from views.landing import show_landing_page
from views.auth import show_auth_page
from views.dashboard import show_dashboard
from views.tasks import show_tasks
from views.focus import show_focus
from views.vision_board import show_vision_board
from views.assistant import show_assistant
from views.rewards import show_rewards_page, show_reward_notification
from models.rewards import Reward

# Set up page configuration before any other Streamlit commands
st.set_page_config(
    page_title="ZenFlow - Focus, Flow & Freedom",
    page_icon="static/ZenFlowIt_Logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://streamlit.io/community',
        'Report a bug': None,
        'About': "ZenFlow - Your personal productivity assistant"
    }
)

# Load environment variables
load_dotenv()

# Apply our centralized theme styling
is_dark_theme = apply_theme_aware_styles()
theme_colors = get_theme_colors()

# Initialize the database once
init_db()  # This will handle both main DB and rewards table initialization

# Initialize session state variables if they don't exist
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = "landing"  # Default to landing page
if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = "login"  # Default auth mode to login
if 'active_list' not in st.session_state:
    st.session_state.active_list = "Miscellaneous"
if 'error' not in st.session_state:
    st.session_state.error = None
if 'success' not in st.session_state:
    st.session_state.success = None

# Vision board session states
if 'editing_tile_id' not in st.session_state:
    st.session_state.editing_tile_id = None
if 'editing_tile_data' not in st.session_state:
    st.session_state.editing_tile_data = None
if 'deleting_tile_id' not in st.session_state:
    st.session_state.deleting_tile_id = None
if 'deleting_tile_title' not in st.session_state:
    st.session_state.deleting_tile_title = None

def main():
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'landing'
    if 'new_rewards' not in st.session_state:
        st.session_state.new_rewards = []

    # Check if we need to redirect to rewards page after earning a badge
    if st.session_state.get('redirect_to_rewards', False) and st.session_state.authenticated:
        st.session_state.redirect_to_rewards = False  # Clear the flag
        st.session_state.current_page = "rewards"  # Set the page to rewards
        # Don't clear new_rewards - we want to display them

    # Display error/success messages if they exist
    if st.session_state.error:
        st.error(st.session_state.error)
        st.session_state.error = None
    
    if st.session_state.success:
        st.success(st.session_state.success)
        st.session_state.success = None

    # Show appropriate page based on authentication and current_page
    if not st.session_state.authenticated:
        if st.session_state.current_page == "landing":
            show_landing_page()
        elif st.session_state.current_page == "auth":
            show_auth_page()
        else:
            # Default to landing page
            st.session_state.current_page = "landing"
            show_landing_page()
    else:
        # User is authenticated, show dashboard and sidebar
        with st.sidebar:
            st.title("ZenFlowIt")
            
            # Get user's first name for personalized greeting
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT first_name FROM users WHERE id = %s", (st.session_state.user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                st.write(f"Welcome, {result['first_name']}!")
            
            st.write("---")
            
            # Navigation buttons
            if st.button("📊 Dashboard", key="nav_dashboard", use_container_width=True):
                st.session_state.current_page = "dashboard"
                st.rerun()
            
            if st.button("📝 Tasks", key="nav_tasks", use_container_width=True):
                st.session_state.current_page = "tasks"
                st.rerun()
            
            if st.button("🎯 Focus", key="nav_focus", use_container_width=True):
                st.session_state.current_page = "focus"
                st.rerun()
            
            if st.button("✨ Vision Board", key="nav_vision", use_container_width=True):
                st.session_state.current_page = "vision_board"
                st.rerun()
                
            if st.button("💬 AI Assistant", key="nav_assistant", use_container_width=True):
                st.session_state.current_page = "assistant"
                st.rerun()
            
            if st.button("🎖️ Rewards", key="nav_rewards", use_container_width=True):
                st.session_state.current_page = "rewards"
                st.rerun()
            
            st.write("---")
            
            # Logout button
            if st.button("Logout", use_container_width=True):
                # Clear chat history before logging out
                if "assistant_messages" in st.session_state:
                    del st.session_state.assistant_messages
                if "chat_history" in st.session_state:
                    del st.session_state.chat_history
                
                st.session_state.authenticated = False
                st.session_state.user_id = None
                st.session_state.current_page = "landing"
                st.rerun()
        
        # Render the selected page
        if st.session_state.current_page == "dashboard":
            show_dashboard()
        elif st.session_state.current_page == "tasks":
            show_tasks()
        elif st.session_state.current_page == "focus":
            show_focus()
        elif st.session_state.current_page == "vision_board":
            show_vision_board()
        elif st.session_state.current_page == "assistant":
            show_assistant()
        elif st.session_state.current_page == "rewards":
            show_rewards_page()
        else:
            show_dashboard()  # Default to dashboard

if __name__ == "__main__":
    main()
