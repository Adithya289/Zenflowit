import streamlit as st
import time
import datetime
from streamlit_extras.stylable_container import stylable_container
from utils.db import (
    get_focus_stats, update_focus_stats, reset_focus_stats, get_tasks,
    get_task_id_by_name, update_task_focus_stats, get_task_focus_stats,
    get_timer_settings, update_timer_settings, get_focus_stats_by_list,
    get_unlinked_focus_stats, get_task_focus_stats_for_user,
    save_focus_session, update_focus_flow_state, get_focus_flow_state
)
from utils.theme import apply_theme_aware_styles, get_theme_colors, get_component_styles

def format_time(seconds):
    """Format seconds into MM:SS display format"""
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"

def show_focus():
    """Display the modernized Focus page with Pomodoro timer"""
    # Apply theme-aware styling
    is_dark_theme = apply_theme_aware_styles()
    colors = get_theme_colors()
    styles = get_component_styles()  # Get reusable component styles
    
    # Initialize session state variables if they don't exist
    if 'timer_mode' not in st.session_state:
        st.session_state.timer_mode = 'pomodoro'  # 'pomodoro', 'short_break', or 'long_break'
    
    # Load timer settings from database if user is logged in
    if ('timer_settings_loaded' not in st.session_state) and hasattr(st.session_state, 'user_id') and st.session_state.user_id:
        # Get timer settings from database
        timer_settings = get_timer_settings(st.session_state.user_id)
        
        # Update session state with settings from the database
        st.session_state.pomodoro_duration = timer_settings["pomodoro_duration"]
        st.session_state.short_break_duration = timer_settings["short_break_duration"]
        st.session_state.long_break_duration = timer_settings["long_break_duration"]
        
        # Mark as loaded to avoid reloading on every rerun
        st.session_state.timer_settings_loaded = True
    else:
        # Set defaults if not loaded from database or no user is logged in
        if 'pomodoro_duration' not in st.session_state:
            st.session_state.pomodoro_duration = 25  # minutes
            
        if 'short_break_duration' not in st.session_state:
            st.session_state.short_break_duration = 5  # minutes
            
        if 'long_break_duration' not in st.session_state:
            st.session_state.long_break_duration = 15  # minutes
    
    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = False
        
    if 'timer_paused' not in st.session_state:
        st.session_state.timer_paused = False
    
    if 'time_remaining' not in st.session_state:
        st.session_state.time_remaining = st.session_state.pomodoro_duration * 60  # seconds
    
    if 'last_update_time' not in st.session_state:
        st.session_state.last_update_time = None
        
    if 'target_end_time' not in st.session_state:
        st.session_state.target_end_time = None
    
    # Enhanced task linking variables
    if 'linked_task' not in st.session_state:
        st.session_state.linked_task = None
        
    if 'linked_task_id' not in st.session_state:
        st.session_state.linked_task_id = None
    
    # Flag to track if task was just linked from Tasks page
    if 'task_just_linked' not in st.session_state:
        st.session_state.task_just_linked = False
    
    # Flag to track if user has explicitly unlinked a task
    if 'task_explicitly_unlinked' not in st.session_state:
        st.session_state.task_explicitly_unlinked = False
    
    # Track focus flow state
    if 'focus_flow_state' not in st.session_state:
        st.session_state.focus_flow_state = 'ready'  # 'ready', 'focusing', 'break', 'completed'
    
    # Define user-specific session state keys
    user_prefix = f"user_{st.session_state.user_id}_" if hasattr(st.session_state, 'user_id') and st.session_state.user_id else "anonymous_"
    
    # Stats tracking with user-specific keys
    if f'{user_prefix}total_focus_time' not in st.session_state:
        st.session_state[f'{user_prefix}total_focus_time'] = 0
    
    if f'{user_prefix}sessions_completed' not in st.session_state:
        st.session_state[f'{user_prefix}sessions_completed'] = 0
    
    # Break tracking with user-specific keys
    if f'{user_prefix}total_break_time' not in st.session_state:
        st.session_state[f'{user_prefix}total_break_time'] = 0
    
    if f'{user_prefix}breaks_completed' not in st.session_state:
        st.session_state[f'{user_prefix}breaks_completed'] = 0
    
    # Track daily sessions for different tasks with user-specific keys
    if f'{user_prefix}daily_task_sessions' not in st.session_state:
        st.session_state[f'{user_prefix}daily_task_sessions'] = {}
    
    # Load persistent stats for the logged-in user
    if (f'{user_prefix}stats_loaded' not in st.session_state):
        if hasattr(st.session_state, 'user_id') and st.session_state.user_id:
            saved_stats = get_focus_stats(st.session_state.user_id)
            st.session_state[f'{user_prefix}total_focus_time'] = saved_stats["total_focus_time"]
            st.session_state[f'{user_prefix}sessions_completed'] = saved_stats["pomodoros_completed"]
            st.session_state[f'{user_prefix}stats_loaded'] = True
            
            # Load the current focus flow state from the database
            flow_state = get_focus_flow_state(st.session_state.user_id)
            
            # If there's an active state in the database, restore it
            if flow_state and flow_state['flow_state'] != 'ready' and flow_state['last_updated']:
                # Only restore if it's recent (within the last 2 hours)
                last_updated = flow_state['last_updated']
                now = datetime.datetime.now()
                if last_updated and (now - last_updated).total_seconds() < 7200:  # 2 hours
                    # Restore task linkage
                    if flow_state['current_task_id'] and flow_state['task_name']:
                        st.session_state.linked_task_id = flow_state['current_task_id']
                        st.session_state.linked_task = flow_state['task_name']
                    
                    # Restore timer state
                    st.session_state.timer_mode = flow_state['current_mode']
                    st.session_state.focus_flow_state = flow_state['flow_state']
                    
                    # Only restore time remaining if it's not null
                    if flow_state['time_remaining_seconds']:
                        st.session_state.time_remaining = flow_state['time_remaining_seconds']
                    
                    # If it was in progress, automatically resume
                    if flow_state['flow_state'] in ['focusing', 'break']:
                        st.session_state.timer_running = True
                        st.session_state.timer_paused = False
                        
                        # Calculate new target end time
                        current_time = time.time()
                        st.session_state.last_update_time = current_time
                        st.session_state.target_end_time = current_time + st.session_state.time_remaining
                    
                    # If it was in completed state, set awaiting_user_action
                    elif flow_state['flow_state'] == 'completed':
                        st.session_state.awaiting_user_action = True
                        if flow_state['current_mode'] == 'pomodoro':
                            st.session_state.completed_mode = 'pomodoro'
                        else:
                            st.session_state.completed_mode = 'break'
        else:
            # Set defaults if no user is logged in
            st.session_state[f'{user_prefix}total_focus_time'] = 0
            st.session_state[f'{user_prefix}sessions_completed'] = 0
    
    # Initialize session state for tracking changes
    if 'settings_changed' not in st.session_state:
        st.session_state.settings_changed = False
    
    # Check if we should auto-start a Pomodoro session from the tasks page
    if st.session_state.get('start_pomodoro', False):
        # Set the timer mode to pomodoro
        st.session_state.timer_mode = 'pomodoro'
        
        # Set the time remaining to the pomodoro duration
        st.session_state.time_remaining = st.session_state.pomodoro_duration * 60
        
        # Set the linked task
        if 'focus_task_name' in st.session_state:
            st.session_state.linked_task = st.session_state.focus_task_name
            st.session_state.task_just_linked = True
            
        # Store the task ID directly if available
        if 'focus_task_id' in st.session_state:
            st.session_state.linked_task_id = st.session_state.focus_task_id
        else:
            # If no task ID provided, try to find it
            st.session_state.linked_task_id = None
        
        # Update focus flow state
        st.session_state.focus_flow_state = 'ready'
        
        # Clear the flags to prevent auto-starting on page refresh
        st.session_state.start_pomodoro = False
    
    # Function to set the timer mode
    def set_timer_mode(mode):
        # Edge case: Prevent starting a break when no focus session has taken place
        if (mode == 'short_break' or mode == 'long_break') and st.session_state[f'{user_prefix}sessions_completed'] == 0:
            st.error("You need to complete at least one focus session before taking a break.")
            return False
        
        # If timer is running, just store the mode for next time
        if st.session_state.timer_running and not st.session_state.timer_paused:
            st.error("Please finish or stop your current session before starting a new one.")
            return False
        
        st.session_state.timer_mode = mode
        # Set the appropriate duration based on the mode
        if mode == 'pomodoro':
            st.session_state.time_remaining = st.session_state.pomodoro_duration * 60
        elif mode == 'short_break':
            st.session_state.time_remaining = st.session_state.short_break_duration * 60
        else:  # 'long_break'
            st.session_state.time_remaining = st.session_state.long_break_duration * 60
        
        st.session_state.timer_running = False
        st.session_state.timer_paused = False
        st.session_state.target_end_time = None
        return True
    
    # Function to update timer when slider values change
    def update_pomodoro_time():
        if not st.session_state.timer_running and st.session_state.timer_mode == 'pomodoro':
            # We'll now only track that something changed, not update the timer yet
            st.session_state.settings_changed = True
            
    def update_short_break_time():
        if not st.session_state.timer_running and st.session_state.timer_mode == 'short_break':
            # We'll now only track that something changed, not update the timer yet
            st.session_state.settings_changed = True
            
    def update_long_break_time():
        if not st.session_state.timer_running and st.session_state.timer_mode == 'long_break':
            # We'll now only track that something changed, not update the timer yet
            st.session_state.settings_changed = True
    
    # Page layout - changed to full width since settings moved to sidebar
    st.markdown(f"""
    <style>
    .main-focus-container {{
        display: flex;
        flex-direction: column;
        width: 100%;
        max-width: 1200px;
        margin: 0 auto;
    }}
    .info-cards-container {{
        display: flex;
        width: 100%;
        gap: 20px;
    }}
    .info-card {{
        flex: 1;
        min-width: 0;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Main container div
    st.markdown('<div class="main-focus-container">', unsafe_allow_html=True)
    
    # Create top info cards section
    st.markdown('<div class="info-cards-container">', unsafe_allow_html=True)
    
    # Timer Settings Card
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    with st.expander("⚙️ Timer Settings", expanded=False):
        st.markdown("""
        <style>
        div[data-testid="stExpander"] {
            width: 100%;
        }
        div[data-testid="stExpander"] > div {
            width: 100%;
        }
        </style>
        """, unsafe_allow_html=True)
        # 5. Settings
        # Check if we should reset to defaults
        use_default_values = False
        if 'reset_to_defaults' in st.session_state and st.session_state.reset_to_defaults:
            use_default_values = True
            # Clear the flag after we've detected it
            st.session_state.reset_to_defaults = False
        
        # Pomodoro Duration
        st.markdown(f"<p style='color: {colors['primary_color']}; font-weight: 600;'><strong>Pomodoro Duration (min)</strong></p>", unsafe_allow_html=True)
        pomodoro_duration = st.slider(
            "Pomodoro Duration",
            min_value=5,
            max_value=60,
            value=max(5, 25 if use_default_values else st.session_state.pomodoro_duration),
            step=5,
            disabled=st.session_state.timer_running and not st.session_state.timer_paused,
            label_visibility="collapsed",
            key="pomodoro_slider",
            on_change=update_pomodoro_time
        )
        
        # Short Break Duration
        st.markdown(f"<p style='color: {colors['primary_color']}; font-weight: 600;'><strong>Short Break Duration (min)</strong></p>", unsafe_allow_html=True)
        short_break_duration = st.slider(
            "Short Break Duration",
            min_value=5,
            max_value=15,
            value=max(5, 5 if use_default_values else st.session_state.short_break_duration),
            step=1,
            disabled=st.session_state.timer_running and not st.session_state.timer_paused,
            label_visibility="collapsed",
            key="short_break_slider",
            on_change=update_short_break_time
        )
        
        # Long Break Duration
        st.markdown(f"<p style='color: {colors['primary_color']}; font-weight: 600;'><strong>Long Break Duration (min)</strong></p>", unsafe_allow_html=True)
        long_break_duration = st.slider(
            "Long Break Duration",
            min_value=15,
            max_value=30,
            value=max(15, 15 if use_default_values else st.session_state.long_break_duration),
            step=5,
            disabled=st.session_state.timer_running and not st.session_state.timer_paused,
            label_visibility="collapsed",
            key="long_break_slider",
            on_change=update_long_break_time
        )
        
        # Check if settings have changed from their saved values
        settings_changed = (
            pomodoro_duration != st.session_state.pomodoro_duration or
            short_break_duration != st.session_state.short_break_duration or
            long_break_duration != st.session_state.long_break_duration or
            st.session_state.settings_changed
        )
        
        # Save button - only show if settings have changed
        save_disabled = st.session_state.timer_running and not st.session_state.timer_paused
        
        # Create a container with controlled width
        save_btn_col = st.container()
        with save_btn_col:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Only show the save button if settings have changed or reset was clicked
                if settings_changed:
                    save_btn = st.button("Save Settings", disabled=save_disabled, key="save_settings", type="primary", use_container_width=True)
                    if save_btn:
                        # Update session state with new values
                        st.session_state.pomodoro_duration = pomodoro_duration
                        st.session_state.short_break_duration = short_break_duration
                        st.session_state.long_break_duration = long_break_duration
                        
                        # Save settings to database if user is logged in
                        if hasattr(st.session_state, 'user_id') and st.session_state.user_id:
                            update_timer_settings(
                                st.session_state.user_id,
                                pomodoro_duration, 
                                short_break_duration, 
                                long_break_duration
                            )
                        
                        # Reset settings changed flag
                        st.session_state.settings_changed = False
                        
                        # Update timer based on whether it's running
                        if not st.session_state.timer_running:
                            # Simply reset the timer mode
                            set_timer_mode(st.session_state.timer_mode)
                        else:
                            # Timer is running, update time remaining based on new duration
                            if st.session_state.timer_mode == 'pomodoro':
                                new_duration_seconds = pomodoro_duration * 60
                                elapsed_seconds = (st.session_state.pomodoro_duration * 60) - st.session_state.time_remaining
                                if elapsed_seconds < new_duration_seconds:
                                    st.session_state.time_remaining = new_duration_seconds - elapsed_seconds
                                    if st.session_state.target_end_time is not None:
                                        st.session_state.target_end_time = time.time() + st.session_state.time_remaining
                            elif st.session_state.timer_mode == 'short_break':
                                new_duration_seconds = short_break_duration * 60
                                elapsed_seconds = (st.session_state.short_break_duration * 60) - st.session_state.time_remaining
                                if elapsed_seconds < new_duration_seconds:
                                    st.session_state.time_remaining = new_duration_seconds - elapsed_seconds
                                    if st.session_state.target_end_time is not None:
                                        st.session_state.target_end_time = time.time() + st.session_state.time_remaining
                            else:  # long_break
                                new_duration_seconds = long_break_duration * 60
                                elapsed_seconds = (st.session_state.long_break_duration * 60) - st.session_state.time_remaining
                                if elapsed_seconds < new_duration_seconds:
                                    st.session_state.time_remaining = new_duration_seconds - elapsed_seconds
                                    if st.session_state.target_end_time is not None:
                                        st.session_state.target_end_time = time.time() + st.session_state.time_remaining
                        
                        # Show success message and refresh the UI
                        st.success("Settings saved!")
                        st.rerun()  # Force a rerun to update the display
            
            with col2:
                # Add reset button to restore default values
                reset_btn = st.button("Reset", key="reset_settings", disabled=save_disabled, use_container_width=True)
                if reset_btn:
                    # Default values
                    default_pomodoro = 25
                    default_short_break = 5
                    default_long_break = 15
                    
                    # Update session state timer duration values
                    st.session_state.pomodoro_duration = default_pomodoro
                    st.session_state.short_break_duration = default_short_break
                    st.session_state.long_break_duration = default_long_break
                    
                    # Don't try to directly modify slider values as this causes errors
                    # Instead, store the values we want to use on the next render
                    st.session_state.reset_to_defaults = True
                    
                    # Set flags to ensure save button appears
                    st.session_state.settings_changed = True
                    
                    # Reset timer if it's not running
                    if not st.session_state.timer_running:
                        set_timer_mode(st.session_state.timer_mode)
                    
                    st.success("Settings reset to defaults! Click Save Settings to keep these defaults.")
                    st.rerun()  # Force a rerun to update the display
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Pomodoro Technique Card
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    with st.expander("🍅 Pomodoro Technique", expanded=False):
        st.markdown("""
        <style>
        div[data-testid="stExpander"] {
            width: 100%;
        }
        div[data-testid="stExpander"] > div {
            width: 100%;
        }
        </style>
        """, unsafe_allow_html=True)
        # Use separate markdown calls to avoid issues with complex HTML rendering
        st.markdown("<p>A time management method that breaks work into focused intervals separated by short breaks.</p>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #549aff; margin-bottom: 10px;'>Benefits:</h4>", unsafe_allow_html=True)
        
        # Use bullet points with Streamlit's native markdown support
        st.markdown("• Improves focus and concentration")
        st.markdown("• Reduces mental fatigue")
        st.markdown("• Increases productivity")
        st.markdown("• Creates better work/break balance")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Create the main column for timer
    col1 = st.container()
    
    with col1:
        # Create a clean container for the timer
        with stylable_container(
            key="timer_container",
            css_styles=styles["timer_container"]
        ):
            # 1. Mode Selector
            st.markdown("""
            <style>
            .mode-selector {
                display: flex;
                justify-content: center;
                gap: 10px;
                margin-bottom: 20px;
            }
            .mode-button {
                padding: 8px 16px;
                border-radius: 30px;
                cursor: pointer;
                font-weight: 500;
                font-size: 14px;
                transition: all 0.2s ease;
                text-align: center;
                min-width: 120px;
            }
            .mode-button.active {
                color: white;
                transform: scale(1.05);
            }
            .mode-button:hover {
                transform: translateY(-2px);
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Instead of HTML buttons + hidden Streamlit buttons, use direct Streamlit buttons with styling
            cols = st.columns(3)
            with cols[0]:
                pomodoro_style = f"background-color: {colors['primary_color']}; color: white;" if st.session_state.timer_mode == "pomodoro" else f"background-color: white; color: {colors['text_color']}; border: 1px solid {colors['border_color']};"
                pomodoro_btn = st.button("Pomodoro", key="pomodoro_btn", use_container_width=True)
                if pomodoro_btn:
                    set_timer_mode('pomodoro')
                    st.rerun()
                st.markdown(f"""
                <style>
                    div[data-testid="stButton"]:nth-of-type(1) button {{
                        {pomodoro_style}
                        border-radius: 30px;
                        font-weight: 500;
                    }}
                </style>
                """, unsafe_allow_html=True)
                
            with cols[1]:
                short_break_style = f"background-color: {colors['primary_color']}; color: white;" if st.session_state.timer_mode == "short_break" else f"background-color: white; color: {colors['text_color']}; border: 1px solid {colors['border_color']};"
                short_break_btn = st.button("Short Break", key="short_break_btn", use_container_width=True)
                if short_break_btn:
                    set_timer_mode('short_break')
                    st.rerun()
                # Apply custom styling to the button
                st.markdown(f"""
                <style>
                    div[data-testid="stButton"]:nth-of-type(2) button {{
                        {short_break_style}
                        border-radius: 30px;
                        font-weight: 500;
                    }}
                </style>
                """, unsafe_allow_html=True)
                
            with cols[2]:
                long_break_style = f"background-color: {colors['primary_color']}; color: white;" if st.session_state.timer_mode == "long_break" else f"background-color: white; color: {colors['text_color']}; border: 1px solid {colors['border_color']};"
                long_break_btn = st.button("Long Break", key="long_break_btn", use_container_width=True)
                if long_break_btn:
                    set_timer_mode('long_break')
                    st.rerun()
                # Apply custom styling to the button
                st.markdown(f"""
                <style>
                    div[data-testid="stButton"]:nth-of-type(3) button {{
                        {long_break_style}
                        border-radius: 30px;
                        font-weight: 500;
                    }}
                </style>
                """, unsafe_allow_html=True)
            
            # 2. Task Display - Show currently linked task and add unlinking functionality
            if st.session_state.linked_task:
                # Create a task info container
                with stylable_container(
                    key="task_info_container",
                    css_styles=f"""
                    {{
                        background-color: {colors['light_accent']}30;
                        border-radius: 8px;
                        padding: 15px;
                        margin: 15px 0;
                        border: 1px solid {colors['border_color']};
                    }}
                    """
                ):
                    task_cols = st.columns([5, 1])
                    with task_cols[0]:
                        st.markdown(f"""
                        <div style="margin-bottom: 5px;">
                            <strong>You are currently focusing on:</strong>
                        </div>
                        <div style="font-size: 1.1rem; font-weight: 500; color: {colors['primary_color']};">
                            {st.session_state.linked_task}
                        </div>
                        <div style="margin-top: 5px; font-size: 0.9rem; color: {colors['text_color']}80;">
                            All focus sessions will be linked to this task until you change or unlink it.
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with task_cols[1]:
                        if st.button("Unlink", key="unlink_task", help="Remove linked task"):
                            st.session_state.showing_unlink_confirmation = True
                            st.rerun()

                    # Show confirmation dialog outside of the columns
                    if hasattr(st.session_state, 'showing_unlink_confirmation') and st.session_state.showing_unlink_confirmation:
                        st.markdown("<div style='margin: 20px 0;'>", unsafe_allow_html=True)
                        unlink_confirmation = st.warning("Are you sure you want to unlink this task? Future sessions will not be associated with it.")
                        
                        # Stack buttons vertically
                        if st.button("Yes, unlink", key="confirm_unlink", use_container_width=True):
                            st.session_state.linked_task = None
                            st.session_state.linked_task_id = None
                            st.session_state.task_explicitly_unlinked = True
                            st.session_state.showing_unlink_confirmation = False
                            st.rerun()
                        
                        if st.button("Unlink and Switch to New Task", key="unlink_and_switch", use_container_width=True):
                            st.session_state.linked_task = None
                            st.session_state.linked_task_id = None
                            st.session_state.task_explicitly_unlinked = False  # Don't set this to True since we're switching
                        
                        if st.button("Cancel", key="cancel_unlink", use_container_width=True):
                            st.session_state.showing_unlink_confirmation = False
                            st.rerun()
                        
                        st.markdown("</div>", unsafe_allow_html=True)
            # If no task is linked, show options to link one or proceed without
            elif not st.session_state.timer_running and not st.session_state.task_explicitly_unlinked:
                with stylable_container(
                    key="no_task_container",
                    css_styles=f"""
                    {{
                        background-color: {colors['light_accent']}30;
                        border-radius: 8px;
                        padding: 15px;
                        margin: 15px 0;
                        border: 1px solid {colors['border_color']};
                    }}
                    """
                ):
                    st.markdown(f"""
                    <div style="margin-bottom: 10px;">
                        <strong>No task is currently linked to your focus session.</strong>
                    </div>
                    <div style="font-size: 0.9rem; color: {colors['text_color']}80; margin-bottom: 10px;">
                        You can proceed with a general focus session or select a specific task to track.
                    </div>
                    """, unsafe_allow_html=True)
                    
                    task_option_cols = st.columns(2)
                    with task_option_cols[0]:
                        if st.button("Select a Task", key="go_to_tasks", use_container_width=True):
                            st.session_state.current_page = "tasks"
                            st.rerun()
                    with task_option_cols[1]:
                        if st.button("Continue Without Task", key="continue_no_task", use_container_width=True):
                            st.session_state.task_explicitly_unlinked = True
                            st.rerun()
            
            # 3. Timer Display
            st.markdown("""
            <style>
            .timer-display {
                font-size: 8rem;
                font-weight: 700;
                font-family: 'Roboto Mono', monospace;
                margin: 30px 0;
                padding: 20px;
        text-align: center;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Calculate progress
            if st.session_state.timer_mode == 'pomodoro':
                # Use the session state's slider value for progress calculation
                if 'pomodoro_slider' in st.session_state:
                    total_secs = st.session_state.pomodoro_slider * 60
                else:
                    total_secs = st.session_state.pomodoro_duration * 60
            elif st.session_state.timer_mode == 'short_break':
                if 'short_break_slider' in st.session_state:
                    total_secs = st.session_state.short_break_slider * 60
                else:
                    total_secs = st.session_state.short_break_duration * 60
            else:  # long_break
                if 'long_break_slider' in st.session_state:
                    total_secs = st.session_state.long_break_slider * 60
                else:
                    total_secs = st.session_state.long_break_duration * 60
            
            # Ensure time_remaining never exceeds total_secs to avoid negative progress values
            elapsed_seconds = max(0, total_secs - st.session_state.time_remaining)
            progress_percentage = min(1.0, max(0.0, elapsed_seconds / total_secs if total_secs > 0 else 0))
            
            # Progress bar
            st.progress(progress_percentage)
            
            # Display the timer - fixed indentation
            minutes, seconds = divmod(st.session_state.time_remaining, 60)
            st.markdown(f"""
            <div class="timer-display">
                {minutes:02d}:{seconds:02d}
            </div>
            """, unsafe_allow_html=True)
            
            # 4. Control Buttons
            st.markdown("""
            <style>
            /* Center all buttons in the timer container */
            .main-controls-container {
                display: flex;
                justify-content: center;
                gap: 20px;
                margin: 20px auto;
            }
            
            /* Style for all control buttons */
            .control-button button {
                width: 60px !important;
                height: 60px !important;
                border-radius: 50% !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                font-size: 24px !important;
                padding: 0 !important;
                margin: 0 auto !important;
            }
            
            /* Fix the issue with the column divs */
            [data-testid="column"] {
                display: flex !important;
                justify-content: center !important;
                align-items: center !important;
            }
            
            /* Ensure buttons are centered inside their containers */
            [data-testid="stButton"] {
                display: flex !important;
                justify-content: center !important;
                margin: 0 auto !important;
            }
            
            /* Make the actual button elements centered */
            [data-testid="stButton"] > button {
                margin: 0 auto !important;
                display: block !important;
            }
            
            /* Transition prompt styling */
            .transition-prompt {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                text-align: center;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .transition-prompt h3 {
                margin-bottom: 15px;
            }
            .action-button {
                margin: 0 10px;
            }
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown("<div class='main-controls-container'>", unsafe_allow_html=True)
            
            # Create control buttons directly using Streamlit - only if not in transition mode
            if not ("awaiting_user_action" in st.session_state and st.session_state.awaiting_user_action):
                # Create a single row for all buttons
                cols = st.columns([1, 1, 1])
                
                # Start button
                with cols[0]:
                    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
                    start_disabled = st.session_state.timer_running and not st.session_state.timer_paused
                    if st.button("▶️", key="start_btn", disabled=start_disabled):
                        # Check if we're ready to start
                        can_start = True
                        
                        # Display a warning if no task is linked and user hasn't explicitly chosen to continue
                        if not st.session_state.linked_task and not st.session_state.task_explicitly_unlinked:
                            st.warning("No task is linked. Are you sure you want to start a general focus session?")
                            confirm_cols = st.columns([1, 1])
                            with confirm_cols[0]:
                                if st.button("Yes, start without task", key="confirm_no_task"):
                                    st.session_state.task_explicitly_unlinked = True
                                    can_start = True
                                else:
                                    can_start = False
                            with confirm_cols[1]:
                                if st.button("No, select a task", key="go_select_task"):
                                    st.session_state.current_page = "tasks"
                                    st.rerun()
                                    can_start = False
                        
                        if can_start:
                            current_time = time.time()
                            st.session_state.timer_running = True
                            st.session_state.timer_paused = False
                            st.session_state.last_update_time = current_time
                            st.session_state.target_end_time = current_time + st.session_state.time_remaining
                            
                            # Update flow state
                            if st.session_state.timer_mode == 'pomodoro':
                                st.session_state.focus_flow_state = 'focusing'
                            else:
                                st.session_state.focus_flow_state = 'break'
                            
                            # Save flow state to database if user is logged in
                            if hasattr(st.session_state, 'user_id') and st.session_state.user_id:
                                # Convert current_time to datetime for database
                                session_start = datetime.datetime.fromtimestamp(current_time)
                                update_focus_flow_state(
                                    st.session_state.user_id,
                                    st.session_state.focus_flow_state,
                                    st.session_state.timer_mode,
                                    st.session_state.time_remaining,
                                    st.session_state.linked_task_id,
                                    session_start
                                )
                                
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Apply custom styling to the button
                    st.markdown(f"""
                    <style>
                        div[data-testid="stButton"]:nth-of-type(4) button {{
                            {styles["control_button"]}
                        }}
                    </style>
                    """, unsafe_allow_html=True)
                
                # Pause button
                with cols[1]:
                    pause_icon = "▶️" if st.session_state.timer_paused else "⏸️"
                    pause_disabled = not st.session_state.timer_running
                    if st.button(pause_icon, key="pause_btn", disabled=pause_disabled):
                        if st.session_state.timer_running:
                            st.session_state.timer_paused = not st.session_state.timer_paused
                            current_time = time.time()
                            
                            if st.session_state.timer_paused:
                                # When pausing, store the pause time
                                st.session_state.pause_time = current_time
                            else:
                                # When resuming, adjust the target end time
                                if hasattr(st.session_state, 'pause_time'):
                                    pause_duration = current_time - st.session_state.pause_time
                                    if st.session_state.target_end_time is not None:
                                        st.session_state.target_end_time += pause_duration
                            
                            # Set the last update time to now
                            st.session_state.last_update_time = current_time
                        st.rerun()
                    
                    # Apply custom styling to the button
                    st.markdown(f"""
                    <style>
                        div[data-testid="stButton"]:nth-of-type(5) button {{
                            {styles["pause_button"]}
                        }}
                    </style>
                    """, unsafe_allow_html=True)
                
                # Reset button
                with cols[2]:
                    if st.button("🔄", key="reset_btn"):
                        # If a completed session, log it before resetting
                        if st.session_state.timer_running and st.session_state.timer_mode == 'pomodoro':
                            elapsed_seconds = st.session_state.pomodoro_duration * 60 - st.session_state.time_remaining
                            if elapsed_seconds > 0:
                                # Log the partial session
                                st.session_state[f'{user_prefix}total_focus_time'] += elapsed_seconds
                        
                        # Reset timer
                        set_timer_mode(st.session_state.timer_mode)  # This resets the time based on current mode
                        st.rerun()
                    
                    # Apply custom styling to the button
                    st.markdown(f"""
                    <style>
                        div[data-testid="stButton"]:nth-of-type(6) button {{
                            {styles["reset_button"]}
                        }}
                    </style>
                    """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # MOVED: Show transition prompt outside the main timer container
    if "awaiting_user_action" in st.session_state and st.session_state.awaiting_user_action:
        with stylable_container(
            key="transition_container",
            css_styles=styles["transition_container"],
        ):
            if st.session_state.completed_mode == "pomodoro":
                # Show different messages based on task linking status
                if st.session_state.linked_task:
                    st.markdown(f"""
                    <h3 style='color: #00BFFF;'>🎉 Focus Session Complete!</h3>
                    <p style='color: #00BFFF;'>You've completed a focus session for: <strong>{st.session_state.linked_task}</strong></p>
                    <p>This session has been logged under this task.</p>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <h3 style='color: #00BFFF;'>🎉 Focus Session Complete!</h3>
                    <p style='color: #00BFFF;'>You've completed a general focus session (not linked to any task).</p>
                    """, unsafe_allow_html=True)
                
                # Create a grid of action buttons with clear options
                action_cols = st.columns([1, 1])
                with action_cols[0]:
                    st.markdown("<div style='text-align: center;'><strong>Continue with:</strong></div>", unsafe_allow_html=True)
                    if st.button("⏱️ Start Short Break", key="start_short_break", use_container_width=True):
                        # Reset awaiting action
                        st.session_state.awaiting_user_action = False
                        # Change mode to short break
                        set_timer_mode("short_break")
                        # Update flow state
                        st.session_state.focus_flow_state = 'break'
                        # Auto-start timer
                        current_time = time.time()
                        st.session_state.timer_running = True
                        st.session_state.timer_paused = False
                        st.session_state.last_update_time = current_time
                        st.session_state.target_end_time = current_time + st.session_state.time_remaining
                        
                        # Save flow state to database if logged in
                        if hasattr(st.session_state, 'user_id') and st.session_state.user_id:
                            session_start = datetime.datetime.fromtimestamp(current_time)
                            update_focus_flow_state(
                                st.session_state.user_id,
                                'break',
                                'short_break',
                                st.session_state.time_remaining,
                                st.session_state.linked_task_id,
                                session_start
                            )
                            
                        st.rerun()
                    
                    if st.button("🧠 Start Long Break", key="start_long_break", use_container_width=True):
                        # Reset awaiting action
                        st.session_state.awaiting_user_action = False
                        # Change mode to long break
                        set_timer_mode("long_break")
                        # Update flow state
                        st.session_state.focus_flow_state = 'break'
                        # Auto-start timer
                        current_time = time.time()
                        st.session_state.timer_running = True
                        st.session_state.timer_paused = False
                        st.session_state.last_update_time = current_time
                        st.session_state.target_end_time = current_time + st.session_state.time_remaining
                        st.rerun()
                
                with action_cols[1]:
                    st.markdown("<div style='text-align: center;'><strong>Other options:</strong></div>", unsafe_allow_html=True)
                    if st.button("🚀 Start New Focus Session", key="start_new_pomodoro", use_container_width=True):
                        # Reset awaiting action
                        st.session_state.awaiting_user_action = False
                        # Change mode to pomodoro
                        set_timer_mode("pomodoro")
                        # Update flow state
                        st.session_state.focus_flow_state = 'ready'
                        # Auto-start timer
                        current_time = time.time()
                        st.session_state.timer_running = True
                        st.session_state.timer_paused = False
                        st.session_state.last_update_time = current_time
                        st.session_state.target_end_time = current_time + st.session_state.time_remaining
                        st.rerun()
                    
                    if st.session_state.linked_task:
                        if st.button("📋 Switch Task", key="switch_task", use_container_width=True):
                            # Redirect to tasks page to select a new task
                            st.session_state.awaiting_user_action = False
                            st.session_state.current_page = "tasks"
                            st.rerun()
                    else:
                        if st.button("📋 Select a Task", key="select_task", use_container_width=True):
                            # Redirect to tasks page to select a new task
                            st.session_state.awaiting_user_action = False
                            st.session_state.current_page = "tasks"
                            st.rerun()
                
            else:  # Break completed
                # Show break completion message
                break_type = "short" if st.session_state.timer_mode == "short_break" else "long"
                
                # Add different messaging depending on task status
                if st.session_state.linked_task:
                    st.markdown(f"""
                    <h3 style='color: #00BFFF;'>⏱️ {break_type.capitalize()} Break Completed!</h3>
                    <p style='color: #00BFFF;'>Your break following work on <strong>{st.session_state.linked_task}</strong> is over.</p>
                    <p>Ready to continue your focus sessions?</p>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <h3 style='color: #00BFFF;'>⏱️ {break_type.capitalize()} Break Completed!</h3>
                    <p style='color: #00BFFF;'>Your break is over.</p>
                    <p>Ready to continue with your focus sessions?</p>
                    """, unsafe_allow_html=True)
                
                # Create a grid of action buttons with clear options
                action_cols = st.columns([1, 1])
                with action_cols[0]:
                    st.markdown("<div style='text-align: center;'><strong>Continue with:</strong></div>", unsafe_allow_html=True)
                    
                    # Button to start a new focus session with same task
                    if st.session_state.linked_task:
                        # Show task name in the button
                        if st.button(f"🚀 Focus on: {st.session_state.linked_task}", key="continue_with_task", use_container_width=True):
                            # Reset awaiting action
                            st.session_state.awaiting_user_action = False
                            # Change mode to pomodoro
                            set_timer_mode("pomodoro")
                            # Update flow state
                            st.session_state.focus_flow_state = 'ready'
                            # Auto-start timer
                            current_time = time.time()
                            st.session_state.timer_running = True
                            st.session_state.timer_paused = False
                            st.session_state.last_update_time = current_time
                            st.session_state.target_end_time = current_time + st.session_state.time_remaining
                            st.rerun()
                    else:
                        # Generic start button
                        if st.button("🚀 Start New Focus Session", key="start_new_pomodoro", use_container_width=True):
                            # Reset awaiting action
                            st.session_state.awaiting_user_action = False
                            # Change mode to pomodoro
                            set_timer_mode("pomodoro")
                            # Update flow state
                            st.session_state.focus_flow_state = 'ready'
                            # Auto-start timer
                            current_time = time.time()
                            st.session_state.timer_running = True
                            st.session_state.timer_paused = False
                            st.session_state.last_update_time = current_time
                            st.session_state.target_end_time = current_time + st.session_state.time_remaining
                            st.rerun()
                    
                    # Option to extend break
                    if st.button("⏱️ Extend Break by 5 Minutes", key="extend_break", use_container_width=True):
                        # Reset awaiting action
                        st.session_state.awaiting_user_action = False
                        # Use same break mode
                        current_mode = st.session_state.timer_mode
                        # Set time to 5 minutes
                        st.session_state.time_remaining = 5 * 60
                        # Update flow state
                        st.session_state.focus_flow_state = 'break'
                        # Auto-start timer
                        current_time = time.time()
                        st.session_state.timer_running = True
                        st.session_state.timer_paused = False
                        st.session_state.last_update_time = current_time
                        st.session_state.target_end_time = current_time + st.session_state.time_remaining
                        st.rerun()
                
                with action_cols[1]:
                    st.markdown("<div style='text-align: center;'><strong>Other options:</strong></div>", unsafe_allow_html=True)
                    
                    if st.button("📋 Switch Task", key="switch_task", use_container_width=True):
                        # Redirect to tasks page to select a new task
                        st.session_state.awaiting_user_action = False
                        st.session_state.current_page = "tasks"
                        st.rerun()
                    
                    if st.button("❌ End Focus Mode", key="end_focus_mode", use_container_width=True):
                        # Reset all session states
                        st.session_state.awaiting_user_action = False
                        st.session_state.timer_running = False
                        st.session_state.timer_paused = False
                        st.session_state.target_end_time = None
                        st.session_state.focus_flow_state = 'ready'
                        # Don't reset linked task - preserve it
                        st.rerun()
    
    # Stats Cards
    total_minutes = st.session_state[f'{user_prefix}total_focus_time'] // 60
    total_hours = total_minutes // 60
    remaining_minutes = total_minutes % 60
    time_display = f"{total_hours}h {remaining_minutes}m" if total_hours > 0 else f"{total_minutes}m"
    
    # Create a header for the statistics section
    st.markdown(f"""
    <h3 style="color: #00BFFF; font-size: 1.9rem; font-weight: 700; margin: 1.5rem 0; padding: 0.5rem; text-align: center;">
    📊 Your Statistics
    </h3>
    """, unsafe_allow_html=True)
    
    # Create columns for the statistics cards
    stats_cols = st.columns(2)
    
    with stats_cols[0]:
        # Use a custom div with inline styles for the first card
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; border-radius: 10px; background-color: {colors['primary_color']}; box-shadow: 0 8px 16px rgba(0,0,0,0.15);">
            <h3 style="font-size: 2.2rem; color: white; font-weight: 700;">{time_display}</h3>
            <p style="margin-top: 5px; color: white; font-weight: 500;">Total Focus Time</p>
            </div>
        """, unsafe_allow_html=True)
    
    with stats_cols[1]:
        # Use a custom div with inline styles for the second card
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; border-radius: 10px; background-color: {colors['primary_color']}; box-shadow: 0 8px 16px rgba(0,0,0,0.15);">
            <h3 style="font-size: 2.2rem; color: white; font-weight: 700;">{st.session_state[f'{user_prefix}sessions_completed']}</h3>
            <p style="margin-top: 5px; color: white; font-weight: 500;">Sessions Completed</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Add Reset Stats button if user is logged in
    if hasattr(st.session_state, 'user_id') and st.session_state.user_id:
        reset_stats_cols = st.columns([3, 1, 3])
        with reset_stats_cols[1]:
            if st.button("Reset Stats", key="reset_focus_stats"):
                # Reset stats in the database
                if reset_focus_stats(st.session_state.user_id):
                    # Reset session state variables
                    st.session_state[f'{user_prefix}total_focus_time'] = 0
                    st.session_state[f'{user_prefix}sessions_completed'] = 0
                    st.session_state[f'{user_prefix}total_break_time'] = 0
                    st.session_state[f'{user_prefix}breaks_completed'] = 0
                    st.session_state[f'{user_prefix}daily_task_sessions'] = {}
                    st.toast("Focus statistics have been reset!", icon="🔄")
                    st.rerun()
                else:
                    st.error("Failed to reset focus statistics. Please try again.")
    
    # Advanced Analytics Section
    if hasattr(st.session_state, 'user_id') and st.session_state.user_id:
        with st.expander("🔍 Advanced Analytics", expanded=False):
            analytics_tabs = st.tabs(["Lists & Categories", "Task Performance", "Unlinked Sessions"])
            
            with analytics_tabs[0]:
                st.markdown(f"""
                <h4 style="color: {colors['primary_color']}; font-size: 1.4rem; font-weight: 600; margin: 1rem 0;">
                Focus Time by List
                </h4>
                """, unsafe_allow_html=True)
                
                # Get list-specific focus stats
                list_stats = get_focus_stats_by_list(st.session_state.user_id)
                
                if list_stats:
                    # Prepare data for chart
                    list_names = [stat['list_name'] for stat in list_stats]
                    list_focus_times = [stat['total_focus_time'] // 60 for stat in list_stats]  # Convert to minutes
                    
                    # Create a bar chart
                    chart_data = {
                        "List": list_names,
                        "Minutes": list_focus_times
                    }
                    
                    import pandas as pd
                    chart_df = pd.DataFrame(chart_data)
                    
                    # Display the chart
                    st.bar_chart(chart_df, x="List", y="Minutes")
                    
                    # Display data in a table
                    st.markdown(f"""
                    <h5 style="color: {colors['text_color']}; font-size: 1.1rem; font-weight: 600; margin: 1rem 0;">
                    Detailed Focus Stats by List
                    </h5>
                    """, unsafe_allow_html=True)
                    
                    data_rows = []
                    for stat in list_stats:
                        focus_minutes = stat['total_focus_time'] // 60
                        focus_hours = focus_minutes // 60
                        focus_remaining_minutes = focus_minutes % 60
                        formatted_time = f"{focus_hours}h {focus_remaining_minutes}m" if focus_hours > 0 else f"{focus_minutes}m"
                        
                        data_rows.append({
                            "List": stat['list_name'],
                            "Total Focus Time": formatted_time,
                            "Sessions": stat['total_sessions']
                        })
                    
                    st.dataframe(data_rows, use_container_width=True)
                else:
                    st.info("No focus data by list available yet. Complete some focused sessions with tasks to see analytics.")
            
            with analytics_tabs[1]:
                st.markdown(f"""
                <h4 style="color: {colors['primary_color']}; font-size: 1.4rem; font-weight: 600; margin: 1rem 0;">
                Top Tasks by Focus Time
                </h4>
                """, unsafe_allow_html=True)
                
                # Get task-specific focus stats
                task_stats = get_task_focus_stats_for_user(st.session_state.user_id)
                
                if task_stats:
                    # Prepare data for display
                    data_rows = []
                    for stat in task_stats:
                        focus_minutes = stat['focus_time_seconds'] // 60
                        focus_hours = focus_minutes // 60
                        focus_remaining_minutes = focus_minutes % 60
                        formatted_time = f"{focus_hours}h {focus_remaining_minutes}m" if focus_hours > 0 else f"{focus_minutes}m"
                        
                        data_rows.append({
                            "Task": stat['task_name'],
                            "List": stat['list_name'],
                            "Focus Time": formatted_time,
                            "Sessions": stat['sessions_completed']
                        })
                    
                    st.dataframe(data_rows, use_container_width=True)
                else:
                    st.info("No task-specific focus data available yet. Link tasks to your focus sessions to see analytics.")
            
            with analytics_tabs[2]:
                st.markdown(f"""
                <h4 style="color: {colors['primary_color']}; font-size: 1.4rem; font-weight: 600; margin: 1rem 0;">
                Unlinked Sessions
                </h4>
                """, unsafe_allow_html=True)
                
                # Get unlinked focus stats
                unlinked_stats = get_unlinked_focus_stats(st.session_state.user_id)
                
                if unlinked_stats:
                    focus_minutes = unlinked_stats['unlinked_focus_time'] // 60
                    focus_hours = focus_minutes // 60
                    focus_remaining_minutes = focus_minutes % 60
                    formatted_time = f"{focus_hours}h {focus_remaining_minutes}m" if focus_hours > 0 else f"{focus_minutes}m"
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Unlinked Focus Time", formatted_time)
                    
                    with col2:
                        st.metric("Unlinked Sessions", unlinked_stats['unlinked_sessions'])
                    
                    # Calculate percentage of total time that is unlinked
                    if st.session_state[f'{user_prefix}total_focus_time'] > 0:
                        unlinked_percentage = (unlinked_stats['unlinked_focus_time'] / st.session_state[f'{user_prefix}total_focus_time']) * 100
                        
                        st.markdown(f"""
                        <div style="margin-top: 20px;">
                            <p style="font-size: 1.1rem; color: {colors['text_color']};">
                                <strong>{unlinked_percentage:.1f}%</strong> of your total focus time is not linked to specific tasks.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add a suggestion based on the percentage
                        if unlinked_percentage > 70:
                            st.warning("Consider linking more of your focus sessions to specific tasks to better track your productivity.")
                        elif unlinked_percentage < 30:
                            st.success("Great job! Most of your focus time is linked to specific tasks, which helps track your productivity.")
                else:
                    st.info("No unlinked focus sessions data available.")
    
    # Timer logic - update time remaining if timer is running
    if st.session_state.timer_running and not st.session_state.timer_paused:
        current_time = time.time()
        
        if st.session_state.last_update_time:
            # Calculate time remaining based on target end time
            if st.session_state.target_end_time is not None:
                st.session_state.time_remaining = max(0, int(st.session_state.target_end_time - current_time))
        
        # Update the last update time
        st.session_state.last_update_time = current_time
        
        # Check if timer has finished
        if st.session_state.time_remaining <= 0:
            # Timer completed
            if st.session_state.timer_mode == 'pomodoro':
                # Log completed pomodoro
                st.session_state[f'{user_prefix}sessions_completed'] += 1
                focus_time_seconds = st.session_state.pomodoro_duration * 60
                st.session_state[f'{user_prefix}total_focus_time'] += focus_time_seconds
                
                # Update focus flow state
                st.session_state.focus_flow_state = 'completed'
                
                # Track daily sessions for this task if linked
                if st.session_state.linked_task and st.session_state.linked_task_id:
                    task_key = f"{st.session_state.linked_task_id}"
                    
                    # Initialize daily task tracking if needed
                    if task_key not in st.session_state[f'{user_prefix}daily_task_sessions']:
                        st.session_state[f'{user_prefix}daily_task_sessions'][task_key] = {
                            'task_name': st.session_state.linked_task,
                            'sessions': 0,
                            'total_time': 0
                        }
                    
                    # Update the task's daily tracking
                    st.session_state[f'{user_prefix}daily_task_sessions'][task_key]['sessions'] += 1
                    st.session_state[f'{user_prefix}daily_task_sessions'][task_key]['total_time'] += focus_time_seconds
                
                # Save the session to the database for the logged-in user
                if hasattr(st.session_state, 'user_id') and st.session_state.user_id:
                    # Update overall focus stats
                    update_focus_stats(st.session_state.user_id, st.session_state[f'{user_prefix}total_focus_time'], st.session_state[f'{user_prefix}sessions_completed'])
                    
                    # Save the session to history
                    session_id = save_focus_session(
                        st.session_state.user_id, 
                        st.session_state.linked_task_id, 
                        'pomodoro', 
                        focus_time_seconds
                    )
                    
                    # Check for rewards/badges
                    if session_id:
                        # Check for badge rewards when session is completed
                        from models.focus_session import FocusSession
                        success, newly_earned = FocusSession.complete_session(session_id, st.session_state.user_id)
                        
                        # If any badges were earned, set redirect flag
                        if success and newly_earned:
                            st.session_state.redirect_to_rewards = True
                    
                    # Update the focus flow state in the database
                    update_focus_flow_state(
                        st.session_state.user_id,
                        'completed',
                        'pomodoro',
                        0,
                        st.session_state.linked_task_id,
                        None
                    )
                    
                    # If a task is linked, update task-specific focus stats
                    if st.session_state.linked_task_id is not None:
                        # We can use the task ID directly without lookup
                        task_id = st.session_state.linked_task_id
                        
                        # Update task-specific focus stats (adding the current session)
                        success = update_task_focus_stats(task_id, st.session_state.user_id, focus_time_seconds, 1)
                        if success:
                            task_name = st.session_state.linked_task
                            st.toast(f"Focus time recorded for task: {task_name}", icon="📊")
                            
                            # Do NOT reset the linked task after completion - maintain task continuity
                            # We only want to reset if the user explicitly chooses to unlink
                        elif st.session_state.linked_task:
                            # Fallback to name lookup for backward compatibility
                            task_id = get_task_id_by_name(st.session_state.user_id, st.session_state.linked_task)
                            
                            if task_id:
                                # Update task-specific focus stats (adding the current session)
                                success = update_task_focus_stats(task_id, st.session_state.user_id, focus_time_seconds, 1)
                                if success:
                                    task_name = st.session_state.linked_task
                                    st.toast(f"Focus time recorded for task: {task_name}", icon="📊")
                                    
                                    # Do NOT reset the linked task after completion
                                else:
                                    st.error(f"Failed to update focus stats for task: {st.session_state.linked_task}")
                            else:
                                st.error(f"Could not find task ID for '{st.session_state.linked_task}'")
                
                # Show completion message
                st.toast("Pomodoro complete! Great job! 🎉", icon="🎉")
                
                # Set awaiting_user_action flag
                if "awaiting_user_action" not in st.session_state:
                    st.session_state.awaiting_user_action = False
                st.session_state.awaiting_user_action = True
                
                # Save current mode for transition
                st.session_state.completed_mode = "pomodoro"
            
            elif st.session_state.timer_mode == 'short_break' or st.session_state.timer_mode == 'long_break':
                # Break completed
                st.toast("Break time over! Ready to focus?", icon="⏱️")
                
                # Update break statistics
                if st.session_state.timer_mode == 'short_break':
                    break_time_seconds = st.session_state.short_break_duration * 60
                else:  # long_break
                    break_time_seconds = st.session_state.long_break_duration * 60
                
                # Update break counters
                st.session_state[f'{user_prefix}total_break_time'] += break_time_seconds
                st.session_state[f'{user_prefix}breaks_completed'] += 1
                
                # Update focus flow state
                st.session_state.focus_flow_state = 'completed'
                
                # Save stats if logged in
                if hasattr(st.session_state, 'user_id') and st.session_state.user_id:
                    # Save the break session to history
                    break_type = 'short_break' if st.session_state.timer_mode == 'short_break' else 'long_break'
                    save_focus_session(
                        st.session_state.user_id, 
                        st.session_state.linked_task_id, 
                        break_type, 
                        break_time_seconds
                    )
                    
                    # Update the focus flow state in the database
                    update_focus_flow_state(
                        st.session_state.user_id,
                        'completed',
                        break_type,
                        0,
                        st.session_state.linked_task_id,
                        None
                    )
                
                # Set awaiting_user_action flag
                if "awaiting_user_action" not in st.session_state:
                    st.session_state.awaiting_user_action = False
                st.session_state.awaiting_user_action = True
                
                # Save current mode for transition
                st.session_state.completed_mode = "break"
            
            # Reset timer for all timer modes (pomodoro, short_break, long_break)
            st.session_state.timer_running = False
            st.session_state.timer_paused = False
            st.session_state.target_end_time = None
            
            # Force a rerun to show the transition prompt
            time.sleep(0.1)  # Small delay to reduce CPU usage
            st.rerun()
        else:
            # Timer is still running
            # Rerun to update the timer display
            time.sleep(0.1)  # Small delay to reduce CPU usage
            st.rerun()
    elif st.session_state.timer_running and st.session_state.last_update_time is None:
        # Initialize timer that was just started
        current_time = time.time()
        st.session_state.last_update_time = current_time
        
        # Calculate total duration
        if st.session_state.timer_mode == 'pomodoro':
            total_duration = st.session_state.pomodoro_duration * 60
        elif st.session_state.timer_mode == 'short_break':
            total_duration = st.session_state.short_break_duration * 60
        else:  # long_break
            total_duration = st.session_state.long_break_duration * 60
        
        st.session_state.target_end_time = current_time + st.session_state.time_remaining
        
        # Rerun to update the timer display
        time.sleep(0.1)  # Small delay to reduce CPU usage
        st.rerun()
    
    # Display the current mode status based on timer_mode
    if st.session_state.timer_running and (st.session_state.timer_mode == 'short_break' or st.session_state.timer_mode == 'long_break'):
        break_type = "Short" if st.session_state.timer_mode == 'short_break' else "Long"
        
        with stylable_container(
            key="break_status_container",
            css_styles=f"""
            {{
                background-color: {colors['accent_color']}20;
                border-radius: 8px;
                padding: 12px;
                margin: 10px 0;
                border: 1px solid {colors['accent_color']}50;
            }}
            """
        ):
            if st.session_state.linked_task:
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 1.1rem; font-weight: 500; margin-bottom: 5px;">
                        <span style="color: {colors['accent_color']};">⏱️ {break_type} Break in Progress</span>
                    </div>
                    <div style="font-size: 0.9rem;">
                        Following your work on: <strong>{st.session_state.linked_task}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 1.1rem; font-weight: 500;">
                        <span style="color: {colors['accent_color']};">⏱️ {break_type} Break in Progress</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Display focused state if in pomodoro mode and timer is running
    elif st.session_state.timer_running and st.session_state.timer_mode == 'pomodoro':
        with stylable_container(
            key="focus_status_container",
            css_styles=f"""
            {{
                background-color: {colors['primary_color']}20;
                border-radius: 8px;
                padding: 12px;
                margin: 10px 0;
                border: 1px solid {colors['primary_color']}50;
            }}
            """
        ):
            if st.session_state.linked_task:
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 1.1rem; font-weight: 500; margin-bottom: 5px;">
                        <span style="color: {colors['primary_color']};">🎯 Focus Session in Progress</span>
                    </div>
                    <div style="font-size: 0.9rem;">
                        You are focusing on: <strong>{st.session_state.linked_task}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 1.1rem; font-weight: 500;">
                        <span style="color: {colors['primary_color']};">🎯 Focus Session in Progress</span>
                    </div>
                    <div style="font-size: 0.9rem;">
                        General focus session (not linked to any task)
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Close the main container div
    st.markdown('</div>', unsafe_allow_html=True)
