import psycopg2
from utils.db import get_db_connection
from models.rewards import Reward

class Task:
    """Task model for handling task-related database operations"""
    
    @staticmethod
    def get_by_id(task_id):
        """Get task by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, list_id, user_id, name, deadline, reminder, repeat, 
                   completed, completed_at, action_plan, created_at
            FROM tasks WHERE id = %s
            """,
            (task_id,)
        )
        
        task = cursor.fetchone()
        conn.close()
        
        return dict(task) if task else None
    
    @staticmethod
    def get_subtask_count(task_id):
        """Get counts of total and completed subtasks for a task"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN completed = TRUE THEN 1 ELSE 0 END) as completed
            FROM subtasks 
            WHERE task_id = %s
            """,
            (task_id,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "total": result["total"],
                "completed": result["completed"] if result["completed"] else 0
            }
        else:
            return {"total": 0, "completed": 0}
    
    @staticmethod
    def get_subtasks(task_id):
        """Get all subtasks for a task"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, name, deadline, reminder, completed, completed_at
            FROM subtasks
            WHERE task_id = %s
            ORDER BY id
            """,
            (task_id,)
        )
        
        subtasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return subtasks

    @staticmethod
    def complete_task(task_id, user_id):
        """Mark a task as completed"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Update task status
            cursor.execute('''
                UPDATE tasks
                SET completed = TRUE,
                    completed_at = CURRENT_TIMESTAMP
                WHERE id = %s AND user_id = %s
                RETURNING id
            ''', (task_id, user_id))
            
            if cursor.fetchone():
                # Get total completed tasks count
                cursor.execute('''
                    SELECT COUNT(*) as count
                    FROM tasks
                    WHERE user_id = %s AND completed = TRUE
                ''', (user_id,))
                total_completed = cursor.fetchone()['count']
                
                # Track all newly earned rewards
                newly_earned_rewards = []
                
                # Check for task-related achievements
                success_first, first_rewards = Reward.check_and_award_reward(user_id, 'task_completion', 1)  # First task
                if success_first and first_rewards:
                    newly_earned_rewards.extend(first_rewards)
                    
                success_total, total_rewards = Reward.check_and_award_reward(user_id, 'tasks_total', total_completed)  # Total tasks
                if success_total and total_rewards:
                    newly_earned_rewards.extend(total_rewards)
                
                # Check for consecutive tasks
                cursor.execute('''
                    SELECT COUNT(*) as count
                    FROM tasks
                    WHERE user_id = %s AND completed = TRUE
                    AND completed_at >= CURRENT_TIMESTAMP - INTERVAL '1 day'
                ''', (user_id,))
                consecutive_tasks = cursor.fetchone()['count']
                success_consec, consec_rewards = Reward.check_and_award_reward(user_id, 'consecutive_tasks', consecutive_tasks)
                if success_consec and consec_rewards:
                    newly_earned_rewards.extend(consec_rewards)
                
                conn.commit()
                return True, newly_earned_rewards
            return False, []
        except psycopg2.Error as e:
            print(f"Error completing task: {e}")
            conn.rollback()
            return False, []
        finally:
            conn.close()
