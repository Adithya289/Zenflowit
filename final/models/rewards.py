import psycopg2
from utils.db import get_db_connection
import streamlit as st

class Reward:
    """Reward model for handling user rewards and achievements"""
    
    @staticmethod
    def init_db():
        """Initialize the rewards and user_rewards tables"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Rewards table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rewards (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                badge_image_path TEXT NOT NULL,
                condition_type TEXT NOT NULL,
                condition_value INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        # User Rewards table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_rewards (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                reward_id INTEGER NOT NULL REFERENCES rewards(id) ON DELETE CASCADE,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, reward_id)
            );
        ''')
        
        # Insert default rewards if they don't exist
        cursor.execute("SELECT COUNT(*) FROM rewards")
        if cursor.fetchone()['count'] == 0:
            rewards = [
                {
                    "name": "First Task",
                    "description": "Completed your first task",
                    "badge_image_path": "attached_assets/BADGE1.png",
                    "condition_type": "task_completion",
                    "condition_value": 1
                },
                {
                    "name": "Focus Master",
                    "description": "Completed a 25-minute focus session",
                    "badge_image_path": "attached_assets/BADGE2.png",
                    "condition_type": "focus_session",
                    "condition_value": 1
                },
                {
                    "name": "Consistency Champion",
                    "description": "Used the app for 3 consecutive days",
                    "badge_image_path": "attached_assets/BADGE3.png",
                    "condition_type": "consecutive_days",
                    "condition_value": 3
                },
                {
                    "name": "Focus Pro",
                    "description": "Completed 5 focus sessions",
                    "badge_image_path": "attached_assets/BADGE4.png",
                    "condition_type": "focus_sessions_total",
                    "condition_value": 5
                },
                {
                    "name": "Task Master",
                    "description": "Completed 3 tasks in a row",
                    "badge_image_path": "attached_assets/BADGE5.png",
                    "condition_type": "consecutive_tasks",
                    "condition_value": 3
                },
                {
                    "name": "Vision Creator",
                    "description": "Created your first vision board",
                    "badge_image_path": "attached_assets/BADGE6.png",
                    "condition_type": "vision_board_created",
                    "condition_value": 1
                },
                {
                    "name": "Focus Legend",
                    "description": "Completed 10 focus sessions",
                    "badge_image_path": "attached_assets/BADGE7.png",
                    "condition_type": "focus_sessions_total",
                    "condition_value": 10
                },
                {
                    "name": "Task Legend",
                    "description": "Completed 10 tasks",
                    "badge_image_path": "attached_assets/BADGE8.png",
                    "condition_type": "tasks_total",
                    "condition_value": 10
                }
            ]
            
            for reward in rewards:
                cursor.execute('''
                    INSERT INTO rewards (name, description, badge_image_path, condition_type, condition_value)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (
                    reward["name"],
                    reward["description"],
                    reward["badge_image_path"],
                    reward["condition_type"],
                    reward["condition_value"]
                ))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_user_rewards(user_id):
        """Get all rewards earned by a user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.id, r.name, r.description, r.badge_image_path, ur.earned_at
            FROM rewards r
            JOIN user_rewards ur ON r.id = ur.reward_id
            WHERE ur.user_id = %s
            ORDER BY ur.earned_at DESC
        ''', (user_id,))
        
        rewards = cursor.fetchall()
        conn.close()
        
        return rewards
    
    @staticmethod
    def check_and_award_reward(user_id, condition_type, current_value):
        """Check if a user qualifies for a reward and award it if they do"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get all rewards of the specified type
            cursor.execute('''
                SELECT id, name, description, badge_image_path, condition_value
                FROM rewards
                WHERE condition_type = %s
            ''', (condition_type,))
            
            rewards = cursor.fetchall()
            newly_earned = []
            
            for reward in rewards:
                # Check if user has already earned this reward
                cursor.execute('''
                    SELECT id FROM user_rewards
                    WHERE user_id = %s AND reward_id = %s
                ''', (user_id, reward['id']))
                
                if not cursor.fetchone() and current_value >= reward['condition_value']:
                    # Award the reward
                    cursor.execute('''
                        INSERT INTO user_rewards (user_id, reward_id)
                        VALUES (%s, %s)
                    ''', (user_id, reward['id']))
                    newly_earned.append(reward)
            
            conn.commit()
            conn.close()
            
            # If badges were earned, set the redirect flag and save badge info
            if newly_earned:
                # Set redirect flag to rewards page
                st.session_state.redirect_to_rewards = True
                
                # Store newly earned rewards in session state for notification
                if 'new_rewards' not in st.session_state:
                    st.session_state.new_rewards = []
                
                # Store reward info including user_id to ensure it's user-specific
                for reward in newly_earned:
                    reward_info = dict(reward)
                    reward_info['user_id'] = user_id  # Add user_id to track ownership
                    st.session_state.new_rewards.append(reward_info)
                
                # Set flag to show celebration on rewards page
                st.session_state.just_completed_task = True
                
                # Return True to indicate badges were earned
                return True, newly_earned
            
            return True, []
        except psycopg2.Error as e:
            print(f"Error in check_and_award_reward: {e}")
            conn.rollback()
            conn.close()
            return False, []
    
    @staticmethod
    def get_reward_progress(user_id):
        """Get progress towards all rewards for a user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # First get all rewards
            cursor.execute('''
                SELECT r.id, r.name, r.description, r.badge_image_path, r.condition_type, r.condition_value,
                       CASE WHEN ur.id IS NOT NULL THEN TRUE ELSE FALSE END as earned
                FROM rewards r
                LEFT JOIN user_rewards ur ON r.id = ur.reward_id AND ur.user_id = %s
                ORDER BY r.id
            ''', (user_id,))
            
            rewards = cursor.fetchall()
            
            # For each reward, get the current progress value based on condition_type
            for reward in rewards:
                if reward['condition_type'] == 'task_completion':
                    cursor.execute('''
                        SELECT COUNT(*) as count FROM tasks 
                        WHERE user_id = %s AND status = 'completed'
                    ''', (user_id,))
                    result = cursor.fetchone()
                    reward['current_value'] = result['count'] if result else 0
                
                elif reward['condition_type'] == 'focus_session':
                    cursor.execute('''
                        SELECT COUNT(*) as count FROM focus_sessions 
                        WHERE user_id = %s AND status = 'completed'
                    ''', (user_id,))
                    result = cursor.fetchone()
                    reward['current_value'] = result['count'] if result else 0
                
                elif reward['condition_type'] == 'consecutive_days':
                    cursor.execute('''
                        SELECT COUNT(DISTINCT DATE(completed_at)) as count 
                        FROM tasks 
                        WHERE user_id = %s 
                        AND completed_at >= CURRENT_DATE - INTERVAL '3 days'
                    ''', (user_id,))
                    result = cursor.fetchone()
                    reward['current_value'] = result['count'] if result else 0
                
                elif reward['condition_type'] == 'focus_sessions_total':
                    cursor.execute('''
                        SELECT COUNT(*) as count FROM focus_sessions 
                        WHERE user_id = %s AND status = 'completed'
                    ''', (user_id,))
                    result = cursor.fetchone()
                    reward['current_value'] = result['count'] if result else 0
                
                elif reward['condition_type'] == 'consecutive_tasks':
                    cursor.execute('''
                        SELECT COUNT(*) as count FROM tasks 
                        WHERE user_id = %s 
                        AND status = 'completed'
                        AND completed_at >= CURRENT_TIMESTAMP - INTERVAL '1 day'
                    ''', (user_id,))
                    result = cursor.fetchone()
                    reward['current_value'] = result['count'] if result else 0
                
                elif reward['condition_type'] == 'vision_board_created':
                    cursor.execute('''
                        SELECT COUNT(*) as count FROM vision_board_tiles 
                        WHERE user_id = %s
                    ''', (user_id,))
                    result = cursor.fetchone()
                    reward['current_value'] = result['count'] if result else 0
                
                elif reward['condition_type'] == 'tasks_total':
                    cursor.execute('''
                        SELECT COUNT(*) as count FROM tasks 
                        WHERE user_id = %s AND status = 'completed'
                    ''', (user_id,))
                    result = cursor.fetchone()
                    reward['current_value'] = result['count'] if result else 0
                
                else:
                    reward['current_value'] = 0
            
            conn.close()
            return rewards
            
        except psycopg2.Error:
            conn.close()
            return []
    
    @staticmethod
    def get_all_rewards():
        """Get all available rewards (badges) from the database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, description, badge_image_path, condition_type, condition_value
            FROM rewards
            ORDER BY id
        ''')
        rewards = cursor.fetchall()
        conn.close()
        return rewards 