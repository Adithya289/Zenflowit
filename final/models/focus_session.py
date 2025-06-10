import psycopg2
from database.db_connection import get_db_connection
from models.rewards import Reward

class FocusSession:
    @staticmethod
    def complete_session(session_id, user_id):
        """Mark a focus session as completed"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Update session status
            cursor.execute('''
                UPDATE focus_sessions
                SET status = 'completed',
                    completed_at = CURRENT_TIMESTAMP
                WHERE id = %s AND user_id = %s
                RETURNING id
            ''', (session_id, user_id))
            
            if cursor.fetchone():
                # Get total completed sessions count
                cursor.execute('''
                    SELECT COUNT(*) as count
                    FROM focus_sessions
                    WHERE user_id = %s AND status = 'completed'
                ''', (user_id,))
                total_completed = cursor.fetchone()['count']
                
                # Get total focus time
                cursor.execute('''
                    SELECT SUM(duration) as total_time
                    FROM focus_sessions
                    WHERE user_id = %s AND status = 'completed'
                ''', (user_id,))
                total_time = cursor.fetchone()['total_time'] or 0
                
                # Track earned rewards
                newly_earned_rewards = []
                
                # Check for focus session achievements
                success1, rewards1 = Reward.check_and_award_reward(user_id, 'focus_completion', 1)  # First focus session
                if success1 and rewards1:
                    newly_earned_rewards.extend(rewards1)
                    
                success2, rewards2 = Reward.check_and_award_reward(user_id, 'focus_total', total_completed)  # Total sessions
                if success2 and rewards2:
                    newly_earned_rewards.extend(rewards2)
                    
                success3, rewards3 = Reward.check_and_award_reward(user_id, 'focus_time', total_time)  # Total focus time
                if success3 and rewards3:
                    newly_earned_rewards.extend(rewards3)
                
                # Check for consecutive sessions
                cursor.execute('''
                    SELECT COUNT(*) as count
                    FROM focus_sessions
                    WHERE user_id = %s AND status = 'completed'
                    AND completed_at >= CURRENT_TIMESTAMP - INTERVAL '1 day'
                ''', (user_id,))
                consecutive_sessions = cursor.fetchone()['count']
                success4, rewards4 = Reward.check_and_award_reward(user_id, 'consecutive_focus', consecutive_sessions)
                if success4 and rewards4:
                    newly_earned_rewards.extend(rewards4)
                
                conn.commit()
                return True, newly_earned_rewards
            return False, []
        except psycopg2.Error as e:
            print(f"Error completing focus session: {e}")
            conn.rollback()
            return False, []
        finally:
            conn.close() 