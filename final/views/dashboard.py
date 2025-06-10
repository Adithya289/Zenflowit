import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.db import get_task_statistics, get_upcoming_tasks, get_db_connection
from utils.theme import apply_theme_aware_styles
from utils.auth import verify_password, hash_password

def format_date(date_str):
    """Format date string or timestamp to MM/DD/YYYY format"""
    if not date_str:
        return "No deadline"
    
    try:
        # First try to handle if it's a Unix timestamp (in milliseconds)
        if isinstance(date_str, (int, float)) or str(date_str).isdigit():
            # Convert milliseconds to seconds by dividing by 1000
            timestamp = float(date_str) / 1000
            date_obj = datetime.fromtimestamp(timestamp)
            return date_obj.strftime("%m/%d/%Y")
        
        # If not a timestamp, try parsing as datetime string
        date_obj = datetime.strptime(str(date_str), "%Y-%m-%d %H:%M:%S")
        return date_obj.strftime("%m/%d/%Y")
    except Exception as e:
        # If all parsing fails, return original string
        return str(date_str)

def show_change_password():
    """Show change password form in a modal-like container"""
    st.markdown("### Change Password")
    
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        submit = st.form_submit_button("Update Password")
        
        if submit:
            if not current_password or not new_password or not confirm_password:
                st.error("Please fill in all fields")
                return
            
            if new_password != confirm_password:
                st.error("New passwords do not match")
                return
            
            try:
                # Get current user's password hash
                conn = get_db_connection()
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT password_hash FROM users WHERE id = %s",
                        (st.session_state.user_id,)
                    )
                    result = cursor.fetchone()
                    
                    if result and verify_password(current_password, result['password_hash']):
                        # Update password
                        new_password_hash = hash_password(new_password)
                        cursor.execute(
                            "UPDATE users SET password_hash = %s WHERE id = %s",
                            (new_password_hash, st.session_state.user_id)
                        )
                        conn.commit()
                        st.success("Password updated successfully!")
                        
                        # Clear the form
                        st.session_state.show_change_password = False
                        st.rerun()
                    else:
                        st.error("Current password is incorrect")
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            finally:
                if conn:
                    conn.close()

def show_delete_account():
    """Show delete account confirmation form"""
    st.markdown("### Delete Account")
    st.warning("⚠️ Warning: This action cannot be undone!")
    st.error("""
    If you delete your account:
    - Your account and all associated data will be permanently deleted
    - This action is immediate and cannot be reversed
    - You will need to create a new account if you want to use ZenFlowIt again
    """)
    
    with st.form("delete_account_form"):
        password = st.text_input("Enter your password to confirm deletion", type="password")
        confirm = st.checkbox("I understand that my account will be permanently deleted")
        
        submit = st.form_submit_button("Delete Account Permanently", type="primary")
        
        if submit:
            if not password or not confirm:
                st.error("Please enter your password and confirm your understanding")
                return
            
            try:
                # Verify password
                conn = get_db_connection()
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT password_hash FROM users WHERE id = %s",
                        (st.session_state.user_id,)
                    )
                    result = cursor.fetchone()
                    
                    if result and verify_password(password, result['password_hash']):
                        # Delete related records first
                        cursor.execute("""
                            -- Delete password reset tokens
                            DELETE FROM password_reset_tokens WHERE user_id = %s;
                            
                            -- Delete focus-related records
                            DELETE FROM focus_session_history WHERE user_id = %s;
                            DELETE FROM focus_flow_state WHERE user_id = %s;
                            DELETE FROM focus_stats WHERE user_id = %s;
                            DELETE FROM task_focus_stats WHERE user_id = %s;
                            DELETE FROM timer_settings WHERE user_id = %s;
                            
                            -- Delete vision board related records
                            DELETE FROM vision_board_tiles WHERE user_id = %s;
                            DELETE FROM vision_board_customizations WHERE user_id = %s;
                            
                            -- Delete tasks and lists (this will cascade to subtasks)
                            DELETE FROM tasks WHERE user_id = %s;
                            DELETE FROM lists WHERE user_id = %s;
                            
                            -- Finally delete the user
                            DELETE FROM users WHERE id = %s;
                        """, [st.session_state.user_id] * 11)  # Pass user_id 11 times for each statement
                        
                        conn.commit()
                        st.success("Your account has been permanently deleted.")
                        
                        # Clear session and redirect to login
                        st.session_state.clear()
                        st.rerun()
                    else:
                        st.error("Incorrect password")
                
            except Exception as e:
                conn.rollback()
                st.error(f"An error occurred: {str(e)}")
            finally:
                if conn:
                    conn.close()

def show_dashboard():
    """Display the dashboard page"""
    try:
        st.title("Dashboard")
        
        # Apply theme-aware styling
        is_dark_theme = apply_theme_aware_styles()
        
        # Get task statistics with error handling
        try:
            stats = get_task_statistics(st.session_state.user_id)
        except Exception as e:
            st.error("Unable to fetch task statistics. Please try refreshing the page.")
            stats = {
                "total_tasks": 0,
                "completed_tasks": 0,
                "total_subtasks": 0,
                "completed_subtasks": 0
            }
        
        # Display task statistics in columns
        with st.container():
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(label="Total Tasks", value=stats["total_tasks"])
            
            with col2:
                st.metric(label="Completed Tasks", value=stats["completed_tasks"])
            
            with col3:
                st.metric(label="Total Subtasks", value=stats["total_subtasks"])
            
            with col4:
                st.metric(label="Completed Subtasks", value=stats["completed_subtasks"])
        
        # Calculate completion percentages safely
        task_completion_rate = (stats["completed_tasks"] / stats["total_tasks"] * 100) if stats["total_tasks"] > 0 else 0
        subtask_completion_rate = (stats["completed_subtasks"] / stats["total_subtasks"] * 100) if stats["total_subtasks"] > 0 else 0
        
        # Display progress bars in a container
        with st.container():
            st.subheader("Task Completion Progress")
            
            # Ensure progress values are between 0 and 1
            st.progress(min(max(task_completion_rate / 100, 0), 1))
            st.caption(f"Task completion rate: {task_completion_rate:.1f}%")
            
            st.progress(min(max(subtask_completion_rate / 100, 0), 1))
            st.caption(f"Subtask completion rate: {subtask_completion_rate:.1f}%")
        
        # Display upcoming tasks with error handling
        st.subheader("Upcoming Tasks")
        
        try:
            upcoming_tasks = get_upcoming_tasks(st.session_state.user_id)
            
            if not upcoming_tasks:
                st.info("No upcoming tasks with deadlines. Add tasks with deadlines to see them here.")
            else:
                # Convert to DataFrame for better display
                tasks_data = []
                for task in upcoming_tasks:
                    tasks_data.append({
                        "Task": task["name"],
                        "Deadline": format_date(task["deadline"]),
                        "List": task["list_name"]
                    })
                
                df = pd.DataFrame(tasks_data)
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Task": st.column_config.TextColumn("Task", width="medium"),
                        "Deadline": st.column_config.TextColumn("Deadline", width="medium"),
                        "List": st.column_config.TextColumn("List", width="small")
                    }
                )
        except Exception as e:
            st.error("Unable to fetch upcoming tasks. Please try refreshing the page.")
        
        # Add a button to navigate to tasks page
        st.write("Ready to manage your tasks?")
        if st.button("Go to Tasks", use_container_width=True):
            st.session_state.current_page = "tasks"
            st.rerun()
            
        # Add settings button in the sidebar
        with st.sidebar:
            st.markdown("### Settings")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Change Password"):
                    st.session_state.show_change_password = True
            with col2:
                if st.button("Delete Account"):
                    st.session_state.show_delete_account = True
        
        # Show change password form if requested
        if st.session_state.get('show_change_password', False):
            with st.container():
                st.markdown("---")
                show_change_password()
                if st.button("Cancel"):
                    st.session_state.show_change_password = False
                    st.rerun()
                st.markdown("---")
        
        # Show delete account form if requested
        if st.session_state.get('show_delete_account', False):
            with st.container():
                st.markdown("---")
                show_delete_account()
                if st.button("Cancel"):
                    st.session_state.show_delete_account = False
                    st.rerun()
                st.markdown("---")
            
    except Exception as e:
        st.error("An error occurred while loading the dashboard. Please try refreshing the page.")
        st.write("If the problem persists, please contact support.")
