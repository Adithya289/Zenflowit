import streamlit as st
from datetime import datetime, timedelta, time as datetime_time
import pandas as pd
import time
from utils.db import (
    get_all_lists_for_user, 
    get_list_id_by_name, 
    add_new_list, 
    get_tasks_for_list,
    add_new_task,
    update_task,
    delete_task,
    get_subtasks_for_task,
    add_subtasks_for_task,
    update_subtask,
    get_task_focus_stats
)
from utils.ai import generate_subtasks, generate_action_plan, initialize_gemini
from models.task import Task
from utils.theme import apply_theme_aware_styles

def format_date(date_str):
    """Format date string for display"""
    if not date_str:
        return "No deadline"
    
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return date_obj.strftime("%b %d, %Y at %I:%M %p")
    except:
        return date_str
        
# Helper functions to handle different UI components without nesting violations
def show_delete_confirmation(task_id, task_name):
    """Show delete confirmation buttons with safe nesting"""
    st.warning(f"Delete '{task_name}'?")
    
    # Create two separate containers for the buttons to avoid nesting issues
    yes_container = st.empty()
    no_container = st.empty()
    
    # Place the buttons in separate containers
    if yes_container.button("✓ Yes", key=f"confirm_delete_{task_id}"):
        if delete_task(task_id):
            st.session_state.success = "Task deleted successfully"
        else:
            st.session_state.error = "Failed to delete task"
        st.session_state[f"delete_confirm_{task_id}"] = False
        st.rerun()
        
    if no_container.button("✗ No", key=f"cancel_delete_{task_id}"):
        st.session_state.pop(f"delete_confirm_{task_id}", None)
        st.rerun()

def show_inline_task_edit(task):
    """Show inline task editing with safe containment to avoid nesting issues"""
    task_id = task['id']
    
    # Create a container for the entire editing form to avoid nesting issues
    edit_container = st.container()
    
    with edit_container:
        # Show the edit form with simple entry fields
        st.subheader(f"Edit Task")
        
        # Task name field
        task_name = st.text_input(
            "Task Name", 
            value=task['name'],
            key=f"inline_edit_task_name_{task_id}"
        )
        
        # Parse existing deadline if available
        if task['deadline']:
            try:
                deadline_dt = datetime.strptime(task['deadline'], "%Y-%m-%d %H:%M:%S")
                initial_date = deadline_dt.date()
                initial_time = deadline_dt.time()
            except:
                initial_date = None
                initial_time = datetime.now().time()
        else:
            initial_date = None
            initial_time = None
        
        # Deadline date and time fields in separate containers instead of columns
        date_container = st.container()
        time_container = st.container()
        
        deadline_date = date_container.date_input(
            "Deadline Date", 
            value=initial_date,
            key=f"inline_edit_deadline_date_{task_id}"
        )
        
        deadline_time = time_container.time_input(
            "Deadline Time", 
            value=initial_time,
            key=f"inline_edit_deadline_time_{task_id}"
        )
        
        # Combine date and time into deadline
        if deadline_date:
            if deadline_time is None:
                deadline_time = datetime_time(0, 0, 0)
            deadline = datetime.combine(deadline_date, deadline_time)
        else:
            deadline = None
            
        # Remove reminder and repeat options
        reminder = None
        repeat_value = None
        
        # Action buttons in separate containers
        save_container = st.empty()
        cancel_container = st.empty()
        
        if save_container.button("Save", key=f"inline_save_task_{task_id}"):
            if not task_name:
                st.error("Task name is required")
            else:
                deadline_str = deadline.strftime("%Y-%m-%d %H:%M:%S") if deadline else None
                
                success = update_task(
                    task_id,
                    name=task_name,
                    deadline=deadline_str,
                    reminder=None,
                    repeat=None
                )
                
                if success:
                    st.session_state.editing_task_id = None
                    st.session_state.success = "Task updated successfully"
                    st.rerun()
                else:
                    st.error("Failed to update task. Please try again.")
        
        if cancel_container.button("Cancel", key=f"inline_cancel_edit_task_{task_id}"):
            st.session_state.editing_task_id = None
            st.rerun()

def show_tasks():
    """Display the tasks page"""
    st.title("Tasks")
    
    # Apply theme-aware styling
    is_dark_theme = apply_theme_aware_styles()
    
    # Add task-specific styling
    st.markdown("""
    <style>
    /* Task-specific styling */
    .task-container {
        border-radius: 0.5rem;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .subtask-row {
        padding: 0.3rem;
        border-radius: 0.3rem;
        margin-bottom: 0.2rem;
    }
    
    .strikethrough {
        text-decoration: line-through;
        opacity: 0.7;
    }
    
    .focus-stats-box {
        margin: 8px 0;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Apply theme-specific colors
    if is_dark_theme:
        st.markdown("""
        <style>
        .task-container {
            background-color: #1E1E1E;
            border: 1px solid #333333;
        }
        
        .subtask-row {
            background-color: #1E1E1E;
            border-left: 3px solid #BB86FC;
        }
        
        .strikethrough {
            color: #BBBBBB;
        }
        
        .focus-stats-box {
            background-color: rgba(187, 134, 252, 0.1);
            border-left: 3px solid #BB86FC;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .task-container {
            background-color: #FFFFFF;
            border: 1px solid #E6E6E6;
        }
        
        .subtask-row {
            background-color: #FFFFFF;
            border-left: 3px solid #6200EA;
        }
        
        .strikethrough {
            color: #666666;
        }
        
        .focus-stats-box {
            background-color: rgba(98, 0, 234, 0.05);
            border-left: 3px solid #6200EA;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Check if Gemini API is initialized
    gemini_available = initialize_gemini()
    
    # Create a two-column layout
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Lists")
        
        # Get all lists for the user
        lists = get_all_lists_for_user(st.session_state.user_id)
        
        # Display lists as buttons
        for list_item in lists:
            list_name = list_item["name"]
            is_active = st.session_state.active_list == list_name
            
            if st.button(
                list_name, 
                key=f"list_{list_item['id']}", 
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.active_list = list_name
                st.rerun()
        
        # Form to add a new list
        with st.expander("Add New List"):
            new_list_name = st.text_input("List Name", key="new_list_name")
            if st.button("Add List", key="add_list_button"):
                if not new_list_name:
                    st.error("Please enter a list name")
                else:
                    success = add_new_list(st.session_state.user_id, new_list_name)
                    if success:
                        st.session_state.active_list = new_list_name
                        st.rerun()
                    else:
                        st.error("Failed to add list. Please try again.")
    
    with col2:
        # Get tasks for the active list
        active_list_id = get_list_id_by_name(st.session_state.user_id, st.session_state.active_list)
        
        if not active_list_id:
            st.warning(f"List '{st.session_state.active_list}' not found. Please select another list.")
        else:
            st.subheader(f"{st.session_state.active_list} Tasks")
            
            # Add task button
            if st.button("➕ Add Task", key="add_task_button", use_container_width=True):
                st.session_state.adding_task = True
            
            # Task addition form
            if st.session_state.get("adding_task", False):
                with st.form("add_task_form"):
                    st.subheader("Add New Task")
                    task_name = st.text_input("Task Name", key="new_task_name")
                    
                    # Deadline options - blank by default
                    col1, col2 = st.columns(2)
                    with col1:
                        # Default to None (user needs to click to select a date)
                        deadline_date = st.date_input(
                            "Deadline Date", 
                            value=None,
                            key="deadline_date",
                            label_visibility="visible"
                        )
                    with col2:
                        # Set time to None so it's blank by default
                        deadline_time = st.time_input(
                            "Deadline Time", 
                            value=None,
                            key="deadline_time",
                            label_visibility="visible"
                        )
                    
                    # Combine date and time into a deadline (only if date was selected)
                    if deadline_date:
                        if deadline_time is None:
                            # If time is None, use midnight (00:00:00)
                            deadline_time = datetime_time(0, 0, 0)
                        deadline = datetime.combine(deadline_date, deadline_time)
                    else:
                        deadline = None
                    
                    # Remove all reminder and repeat code
                    # Initialize to None since we're removing these fields
                    reminder = None
                    repeat_value = None
                    
                    submitted = st.form_submit_button("Save Task")
                    
                    if submitted:
                        if not task_name:
                            st.error("Task name is required")
                        else:
                            deadline_str = deadline.strftime("%Y-%m-%d %H:%M:%S") if deadline else None
                            # Pass None for reminder and repeat
                            task_id = add_new_task(
                                active_list_id,
                                st.session_state.user_id,
                                task_name,
                                deadline_str,
                                None,  # Remove reminder
                                None   # Remove repeat
                            )
                
                            if task_id:
                                st.session_state.adding_task = False
                                st.rerun()
                            else:
                                st.error("Failed to add task. Please try again.")
                
                # Create a dedicated container for the cancel button to ensure proper placement
                cancel_container = st.container()
                with cancel_container:
                    if st.button("❌ Cancel", key="cancel_add_task", use_container_width=True, type="secondary"):
                        st.session_state.adding_task = False
                        st.rerun()
            
            # Display tasks
            tasks = get_tasks_for_list(active_list_id, st.session_state.user_id)
            
            if not tasks:
                st.info(f"No tasks in {st.session_state.active_list}. Add your first task!")
            else:
                for task in tasks:
                    # Get subtask information
                    subtasks = get_subtasks_for_task(task['id'])
                    subtask_count = Task.get_subtask_count(task['id'])
                    all_subtasks_completed = subtask_count['total'] > 0 and subtask_count['completed'] == subtask_count['total']
                    
                    # Create a horizontal layout for checkbox and task name
                    container = st.container()
                    checkbox_col, name_col = container.columns([0.05, 0.95])
                    
                    # Remove the can_complete restriction - allow completing task regardless of subtask status
                    
                    # Place the checkbox in first column
                    with checkbox_col:
                        task_completed = st.checkbox(
                            "", 
                            value=task['completed'],
                            key=f"task_checkbox_{task['id']}"
                        )
                        
                        if task_completed != task['completed']:
                            # Update the task completion status
                            update_task(task['id'], completed=task_completed)
                            
                            # If marking task as completed, check for rewards
                            if task_completed:
                                # Get task info to pass to reward system
                                task_info = Task.get_by_id(task['id'])
                                if task_info:
                                    # Check for rewards and get any newly earned rewards
                                    success, newly_earned = Task.complete_task(task['id'], st.session_state.user_id)
                                    
                                    # Mark for redirection to rewards page if any badges were earned
                                    if success and newly_earned:
                                        st.session_state.redirect_to_rewards = True
                                    
                                # If marking task as completed, automatically mark all subtasks as completed
                                if subtasks:
                                    for subtask in subtasks:
                                        if not subtask['completed']:
                                            update_subtask(subtask['id'], completed=True)
                                
                                # Store the completed task ID in session state
                                st.session_state.just_completed_task = True
                                st.session_state.just_completed_task_id = task['id']
                            
                            st.rerun()
                    
                    # Place the expander in second column with strikethrough for completed tasks
                    with name_col:
                        # Get focus stats to display alongside the task name
                        task_stats = get_task_focus_stats(task['id'])
                        has_focus_stats = task_stats and (task_stats['focus_time_seconds'] > 0 or task_stats['sessions_completed'] > 0)
                        
                        # Format task name with focus stats if available
                        if task['completed']:
                            task_display_name = f"~~{task['name']}~~"
                        else:
                            task_display_name = task['name']
                        
                        # Include focus stats directly in the task title if available
                        if has_focus_stats:
                            # Format time
                            total_minutes = task_stats['focus_time_seconds'] // 60
                            # Create a compact display for focus stats
                            focus_stats_display = f" ⏱️ {total_minutes}m • 🔄 {task_stats['sessions_completed']} session{'s' if task_stats['sessions_completed'] != 1 else ''}"
                            task_display_name = f"{task_display_name} {focus_stats_display}"
                        
                        expander = st.expander(task_display_name, expanded=False)
                    
                    # Use the expander context for the task details
                    with expander:
                        # Task details section                        
                        st.write(f"**Deadline:** {format_date(task['deadline'])}")
                        
                        # Remove debugging information
                        
                        # Add task focus stats if available with more details
                        if task_stats and (task_stats['focus_time_seconds'] > 0 or task_stats['sessions_completed'] > 0):
                            # Format focus time nicely
                            total_minutes = task_stats['focus_time_seconds'] // 60
                            total_hours = total_minutes // 60
                            remaining_minutes = total_minutes % 60
                            
                            if total_hours > 0:
                                time_display = f"{total_hours}h {remaining_minutes}m"
                            else:
                                time_display = f"{total_minutes}m"
                                
                            # Display stats in a clean format
                            st.markdown(f"""
                            <div class="focus-stats-box">
                                <strong>📊 Focus Stats:</strong> {time_display} total time • {task_stats['sessions_completed']} session{'s' if task_stats['sessions_completed'] != 1 else ''} completed
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.info("No focus sessions recorded for this task yet. Click the FOCUS button to start tracking.")
                        
                        # Task action buttons - avoid nesting columns
                        if st.session_state.get("editing_task_id") == task['id']:
                            # Show inline editing form
                            show_inline_task_edit(task)
                        else:
                            # Add buttons in a row - without using nested columns
                            edit_btn_container = st.container()
                            if edit_btn_container.button("✏️ Edit", key=f"edit_{task['id']}"):
                                st.session_state.editing_task_id = task['id']
                                st.rerun()
                            
                            # Add FOCUS button
                            focus_btn_container = st.container()
                            if focus_btn_container.button("🎯 FOCUS", key=f"focus_{task['id']}"):
                                # Save the task information to session state
                                st.session_state.focus_task_name = task['name']
                                st.session_state.focus_task_id = task['id']  # Store the task ID
                                # Set flag to start a Pomodoro session
                                st.session_state.start_pomodoro = True
                                # Navigate to the focus page
                                st.session_state.current_page = "focus"
                                st.rerun()
                                
                            # Handle inline delete confirmation 
                            delete_btn_container = st.container()
                            if f"delete_confirm_{task['id']}" in st.session_state and st.session_state[f"delete_confirm_{task['id']}"]:
                                # Use the helper function to avoid nesting issues
                                show_delete_confirmation(task['id'], task['name'])
                            else:
                                if delete_btn_container.button("🗑️ Delete", key=f"delete_{task['id']}"):
                                    # Set confirmation state for this specific task
                                    st.session_state[f"delete_confirm_{task['id']}"] = True
                                    st.rerun()
                        
                        # Show warning if task can't be completed
                        if subtask_count['total'] > 0 and not all_subtasks_completed:
                            st.info(f"Marking this task complete will automatically complete all {subtask_count['total']} subtasks ({subtask_count['completed']} already completed)")
                        
                        # Display subtasks
                        st.write("---")
                        st.subheader("Subtasks")
                        
                        subtasks = get_subtasks_for_task(task['id'])
                        subtask_count = Task.get_subtask_count(task['id'])
                        
                        if subtasks:
                            st.write(f"{subtask_count['completed']}/{subtask_count['total']} completed")
                            
                            for subtask in subtasks:
                                # Use a container for each subtask row
                                subtask_container = st.container()
                                
                                # Check if this subtask is being edited
                                if st.session_state.get("editing_subtask_id") == subtask['id']:
                                    # Create a new container for editing outside the normal nested structure
                                    edit_container = st.empty()
                                    
                                    # Use a new form for editing to avoid nesting issues
                                    with edit_container.container():
                                        st.subheader(f"Edit Subtask")
                                        
                                        # Edit name field
                                        edited_name = st.text_input(
                                            "Name",
                                            value=subtask['name'],
                                            key=f"edit_subtask_name_{subtask['id']}"
                                        )
                                        
                                        # Process deadline information
                                        if subtask['deadline']:
                                            try:
                                                deadline_dt = datetime.strptime(subtask['deadline'], "%Y-%m-%d %H:%M:%S")
                                                initial_date = deadline_dt.date()
                                                initial_time = deadline_dt.time()
                                            except:
                                                initial_date = None
                                                initial_time = datetime.now().time()
                                        else:
                                            initial_date = None
                                            initial_time = datetime.now().time()
                                        
                                        # Deadline date input
                                        deadline_date = st.date_input(
                                            "Deadline Date", 
                                            value=initial_date,
                                            key=f"edit_subtask_date_{subtask['id']}"
                                        )
                                        
                                        # Deadline time input
                                        deadline_time = st.time_input(
                                            "Deadline Time", 
                                            value=None if not subtask['deadline'] else initial_time,
                                            key=f"edit_subtask_time_{subtask['id']}"
                                        )
                                        
                                        # Combine date and time
                                        if deadline_date:
                                            if deadline_time is None:
                                                # If time is None, use midnight (00:00:00)
                                                deadline_time = datetime_time(0, 0, 0)
                                            deadline = datetime.combine(deadline_date, deadline_time)
                                        else:
                                            deadline = None
                                        
                                        # Remove reminder options
                                        reminder = None
                                        
                                        # Save button
                                        if st.button("Save", key=f"save_subtask_{subtask['id']}"):
                                            deadline_str = deadline.strftime("%Y-%m-%d %H:%M:%S") if deadline else None
                                            
                                            success = update_subtask(
                                                subtask['id'],
                                                name=edited_name,
                                                deadline=deadline_str,
                                                reminder=None
                                            )
                                            
                                            if success:
                                                st.session_state.editing_subtask_id = None
                                                st.session_state.success = "Subtask updated"
                                                st.rerun()
                                            else:
                                                st.error("Failed to update subtask")
                                        
                                        # Cancel button
                                        if st.button("Cancel", key=f"cancel_subtask_{subtask['id']}"):
                                            st.session_state.editing_subtask_id = None
                                            st.rerun()
                                else:
                                    # Add theme-aware container - this is handled in the conditional styling above
                                    # st.markdown('<div class="subtask-row">', unsafe_allow_html=True)
                                    
                                    # Store the original completion state before user interaction
                                    prev_subtask_completed = subtask['completed']

                                    # Create the subtask label with strikethrough for completed tasks
                                    if subtask['completed']:
                                        subtask_label = subtask['name']
                                        # Apply strikethrough class to the container instead
                                        st.markdown('<div class="subtask-row strikethrough">', unsafe_allow_html=True)
                                    else:
                                        subtask_label = subtask['name']
                                        st.markdown('<div class="subtask-row">', unsafe_allow_html=True)

                                    # Create a horizontal layout using containers to avoid nesting issues
                                    # First row: checkbox and edit button
                                    # Place checkbox with completion status - use plain text for label
                                    subtask_completed = st.checkbox(
                                        subtask_label,
                                        value=subtask['completed'],
                                        key=f"subtask_{subtask['id']}",
                                        help="Mark subtask as complete"
                                    )

                                    # Only update if state has changed, but DON'T trigger rerun
                                    if subtask_completed != prev_subtask_completed:
                                        # Update the database
                                        update_subtask(subtask['id'], completed=subtask_completed)
                                        # Don't rerun immediately, just update the database
                                        # We'll rerun after finishing all subtasks
                                        st.session_state[f"subtask_updated_{task['id']}"] = True
                                    
                                    # Place edit button - without using columns
                                    st.write("")  # Add a small space
                                    if st.button("✏️", key=f"edit_subtask_{subtask['id']}"):
                                        st.session_state.editing_subtask_id = subtask['id']
                                        st.rerun()
                                    
                                    # Second row: details (if any)
                                    if subtask['deadline']:
                                        st.caption(f"📅 Due: {format_date(subtask['deadline'])}")
                                    
                                    # Close the theme-aware container
                                    st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.info("No subtasks yet.")
                        
                        # AI buttons
                        st.write("---")
                        
                        # Check if any subtasks were updated and trigger a rerun at the end
                        if st.session_state.get(f"subtask_updated_{task['id']}", False):
                            # Clear the flag
                            st.session_state.pop(f"subtask_updated_{task['id']}", None)
                            # Schedule a rerun after finishing all subtasks
                            st.rerun()
                        
                        # Add CSS for button container
                        st.markdown("""
                            <style>
                            .stButton > button {
                                width: 100%;
                            }
                            .button-container {
                                display: flex;
                                gap: 10px;
                                margin-bottom: 10px;
                            }
                            .button-container > div {
                                flex: 1;
                            }
                            </style>
                        """, unsafe_allow_html=True)
                        
                        # Create a container for the buttons
                        st.markdown('<div class="button-container">', unsafe_allow_html=True)
                        
                        # Generate Subtasks button
                        if st.button("🤖 Generate Subtasks", key=f"gen_subtasks_{task['id']}"):
                            if not gemini_available:
                                st.error("Gemini API key not configured. Please check your .env file.")
                            elif subtasks:
                                st.session_state.confirming_subtask_replace = task['id']
                                st.rerun()
                            else:
                                st.session_state.generating_subtasks_for = task['id']
                                st.session_state.generating_subtasks_task_name = task['name']
                                st.rerun()
                        
                        # Add Single Subtask button
                        if st.button("➕ Add Subtask", key=f"add_subtask_{task['id']}"):
                            st.session_state.adding_subtask_for = task['id']
                            st.rerun()
                        
                        # Generate Action Plan button
                        if st.button("📋 Generate Action Plan", key=f"gen_plan_{task['id']}"):
                            if not gemini_available:
                                st.error("Gemini API key not configured. Please check your .env file.")
                            else:
                                st.session_state.generating_plan_for = task['id']
                                st.session_state.generating_plan_task_name = task['name']
                                subtask_names = [s['name'] for s in subtasks] if subtasks else []
                                st.session_state.generating_plan_subtasks = subtask_names
                                st.rerun()
                        
                        # Close the button container
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Handle adding a single subtask
                        if st.session_state.get("adding_subtask_for") == task['id']:
                            with st.form(key=f"add_single_subtask_form_{task['id']}"):
                                st.subheader("Add New Subtask")
                                subtask_name = st.text_input("Subtask Name", key=f"new_subtask_name_{task['id']}")
                                
                                # Add deadline inputs sequentially instead of in columns
                                deadline_date = st.date_input(
                                    "Deadline Date",
                                    value=None,
                                    key=f"new_subtask_date_{task['id']}"
                                )
                                
                                deadline_time = st.time_input(
                                    "Deadline Time",
                                    value=None,
                                    key=f"new_subtask_time_{task['id']}"
                                )
                                
                                # Add form submit buttons side by side using custom CSS
                                st.markdown("""
                                    <style>
                                    div[data-testid="stHorizontalBlock"] {
                                        gap: 10px;
                                    }
                                    </style>
                                """, unsafe_allow_html=True)
                                
                                submitted = st.form_submit_button("Add Subtask", type="primary")
                                cancelled = st.form_submit_button("Cancel", type="secondary")
                                
                                if submitted:
                                    if not subtask_name:
                                        st.error("Please enter a subtask name")
                                    else:
                                        # Combine date and time if provided
                                        deadline = None
                                        if deadline_date:
                                            if deadline_time is None:
                                                deadline_time = datetime_time(0, 0, 0)
                                            deadline = datetime.combine(deadline_date, deadline_time)
                                            deadline = deadline.strftime("%Y-%m-%d %H:%M:%S")
                                        
                                        # Get existing subtasks
                                        existing_subtasks = get_subtasks_for_task(task['id'])
                                        existing_subtask_names = [subtask['name'] for subtask in existing_subtasks]
                                        
                                        # Add the new subtask to the list
                                        all_subtasks = existing_subtask_names + [subtask_name]
                                        
                                        # Add all subtasks (existing + new)
                                        success = add_subtasks_for_task(task['id'], all_subtasks)
                                        
                                        if success:
                                            st.session_state.success = "Subtask added successfully"
                                            st.session_state.adding_subtask_for = None
                                            st.rerun()
                                        else:
                                            st.error("Failed to add subtask")
                                
                                if cancelled:
                                    st.session_state.adding_subtask_for = None
                                    st.rerun()
                        
                        # Display action plan if exists
                        if task['action_plan']:
                            st.write("---")
                            st.subheader("Action Plan")
                            st.markdown(task['action_plan'])
            
            # Handle task editing (old delete confirmation code removed)
            
            # Note: Task editing is now handled inline within each task's expander
            # using the show_inline_task_edit helper function
            
            # The editing of subtasks is now handled in-place within the task display section
            
            # Handle confirming subtask replacement
            if st.session_state.get("confirming_subtask_replace"):
                task_id = st.session_state.confirming_subtask_replace
                
                st.warning("This task already has subtasks. Generating new subtasks will replace the existing ones.")
                
                # Use empty containers instead of columns to avoid nesting issues
                proceed_container = st.empty()
                cancel_container = st.empty()
                
                # Place buttons in separate containers
                if proceed_container.button("Proceed", key="confirm_replace_subtasks"):
                    task = Task.get_by_id(task_id)
                    if task:
                        st.session_state.generating_subtasks_for = task_id
                        st.session_state.generating_subtasks_task_name = task["name"]
                        st.session_state.confirming_subtask_replace = None
                        st.rerun()
                    else:
                        st.error("Task not found. Please try again.")
                        st.session_state.confirming_subtask_replace = None
                        st.rerun()
                
                if cancel_container.button("Cancel", key="cancel_replace_subtasks"):
                    st.session_state.confirming_subtask_replace = None
                    st.rerun()
            
            # Handle generating subtasks
            if st.session_state.get("generating_subtasks_for"):
                task_id = st.session_state.generating_subtasks_for
                task_name = st.session_state.generating_subtasks_task_name
                
                st.info(f"Generating subtasks for '{task_name}'...")
                
                # Show a spinner while generating
                with st.spinner("AI is breaking down this task..."):
                    subtasks, error = generate_subtasks(task_name)
                
                if error:
                    st.error(error)
                elif subtasks:
                    # Add the subtasks to the database
                    success = add_subtasks_for_task(task_id, subtasks)
                    
                    if success:
                        st.session_state.success = f"Generated {len(subtasks)} subtasks"
                    else:
                        st.session_state.error = "Failed to save generated subtasks"
                else:
                    st.session_state.error = "No subtasks were generated"
                
                st.session_state.generating_subtasks_for = None
                st.session_state.generating_subtasks_task_name = None
                st.rerun()
            
            # Handle generating action plan
            if st.session_state.get("generating_plan_for"):
                task_id = st.session_state.generating_plan_for
                task_name = st.session_state.generating_plan_task_name
                subtasks = st.session_state.generating_plan_subtasks
                
                st.info(f"Generating action plan for '{task_name}'...")
                
                # Show a spinner while generating
                with st.spinner("AI is creating a detailed action plan..."):
                    action_plan, error = generate_action_plan(task_name, subtasks=subtasks)
                
                if error:
                    st.error(error)
                elif action_plan:
                    # Update the task with the action plan
                    success = update_task(task_id, action_plan=action_plan)
                    
                    if success:
                        st.session_state.success = "Generated action plan successfully"
                    else:
                        st.session_state.error = "Failed to save generated action plan"
                else:
                    st.session_state.error = "No action plan was generated"
                
                st.session_state.generating_plan_for = None
                st.session_state.generating_plan_task_name = None
                st.session_state.generating_plan_subtasks = None
                st.rerun()
