import psycopg2
from utils.db import get_db_connection

class User:
    """User model for handling user-related database operations"""
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, first_name, last_name, email FROM users WHERE id = %s",
            (user_id,)
        )
        
        user = cursor.fetchone()
        conn.close()
        
        return dict(user) if user else None
    
    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, first_name, last_name, email FROM users WHERE email = %s",
            (email,)
        )
        
        user = cursor.fetchone()
        conn.close()
        
        return dict(user) if user else None
    
    @staticmethod
    def update(user_id, first_name=None, last_name=None, email=None):
        """Update user information"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build the update query dynamically based on provided parameters
        update_fields = []
        params = []
        
        if first_name is not None:
            update_fields.append("first_name = %s")
            params.append(first_name)
        
        if last_name is not None:
            update_fields.append("last_name = %s")
            params.append(last_name)
        
        if email is not None:
            update_fields.append("email = %s")
            params.append(email)
        
        if not update_fields:
            conn.close()
            return False
        
        # Build the final query
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
        params.append(user_id)
        
        try:
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return True
        except psycopg2.Error:
            conn.rollback()
            conn.close()
            return False