import psycopg2
from passlib.hash import pbkdf2_sha256
from utils.db import get_db_connection, create_default_lists_for_user
from datetime import datetime

def hash_password(password):
    """Hash password using PBKDF2 with SHA-256"""
    return pbkdf2_sha256.hash(password)

def verify_password(plain_password, hashed_password):
    """Verify password against hash"""
    return pbkdf2_sha256.verify(plain_password, hashed_password)

def register_user(first_name, last_name, email, password):
    """Register a new user and create default lists"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            conn.close()
            return None, "Email already registered. Please login instead."
        
        # Hash the password
        password_hash = hash_password(password)
        
        # Insert the new user
        cursor.execute(
            "INSERT INTO users (first_name, last_name, email, password_hash) VALUES (%s, %s, %s, %s) RETURNING id",
            (first_name, last_name, email, password_hash)
        )
        
        # Get the user_id using RETURNING clause
        user_id = cursor.fetchone()['id']
        conn.commit()
        conn.close()
        
        # Create default lists for the new user
        create_default_lists_for_user(user_id)
        
        return user_id, None
    except psycopg2.Error as e:
        conn.rollback()
        conn.close()
        return None, f"Database error: {str(e)}"


def login_user(email, password):
    """Authenticate a user with email and password"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, password_hash 
            FROM users 
            WHERE email = %s
        """, (email,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return None, "User not found. Please sign up."
        
        if verify_password(password, user["password_hash"]):
            return user["id"], None
        else:
            return None, "Incorrect password. Please try again."
    except psycopg2.Error as e:
        conn.close()
        return None, f"Database error: {str(e)}"

def reactivate_account(email, password):
    """Reactivate a soft-deleted account"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # First verify the account exists and is deleted
        cursor.execute("""
            SELECT id, password_hash, is_deleted, deletion_date 
            FROM users 
            WHERE email = %s
        """, (email,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return False, "Account not found."
        
        if not user["is_deleted"]:
            conn.close()
            return False, "Account is already active."
        
        if user["deletion_date"] and (datetime.now() - user["deletion_date"]).days > 7:
            conn.close()
            return False, "This account has been permanently deleted and cannot be reactivated."
        
        # Verify password
        if verify_password(password, user["password_hash"]):
            # Reactivate the account
            cursor.execute("""
                UPDATE users 
                SET is_deleted = FALSE, 
                    deletion_date = NULL 
                WHERE id = %s 
                RETURNING id
            """, (user["id"],))
            
            reactivated = cursor.fetchone()
            if reactivated:
                conn.commit()
                conn.close()
                return True, "Account reactivated successfully!"
            else:
                conn.rollback()
                conn.close()
                return False, "Failed to reactivate account. Please try again."
        else:
            conn.close()
            return False, "Incorrect password."
            
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
            conn.close()
        return False, f"Database error: {str(e)}"

def get_user_by_email(email):
    """
    Retrieve user information by email
    Returns None if user not found
    """
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Query to get user information
            cursor.execute(
                "SELECT id, first_name, last_name, email, password_hash FROM users WHERE email = %s",
                (email,)
            )
            
            user = cursor.fetchone()
            
            if user:
                # Since we're using DictCursor, we can access by column names
                return {
                    'id': user['id'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'email': user['email'],
                    'password_hash': user['password_hash']
                }
            return None
            
    except Exception as e:
        print(f"Error in get_user_by_email: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()
