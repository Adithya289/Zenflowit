import psycopg2
import os
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
import datetime

# Load environment variables
print("Loading environment variables...")
load_dotenv()

def get_db_connection():
    """Create and return a PostgreSQL connection"""
    try:
        # Debug: Print all environment variables related to database
        print("\nDatabase Connection Debug Info:")
        db_url = os.getenv("DATABASE_URL")
        print("DATABASE_URL:", db_url)
        
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "zenflow")
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD")
        
        print("Individual connection parameters:")
        print(f"DB_HOST: {db_host}")
        print(f"DB_PORT: {db_port}")
        print(f"DB_NAME: {db_name}")
        print(f"DB_USER: {db_user}")
        print(f"DB_PASSWORD: {'*' * len(db_password) if db_password else 'Not set'}")
        
        if db_url:
            print("\nAttempting connection using DATABASE_URL...")
            conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
            print("Successfully connected using DATABASE_URL")
        else:
            print("\nAttempting connection using individual parameters...")
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                dbname=db_name,
                user=db_user,
                password=db_password,
                cursor_factory=RealDictCursor
            )
            print("Successfully connected using individual parameters")
        
        return conn
    except psycopg2.Error as e:
        print("\nDatabase connection error:")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print(f"Error Details: {e.diag.message_detail if hasattr(e, 'diag') else 'No additional details'}")
        raise

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            vision_board_theme VARCHAR(100) DEFAULT 'default',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # Lists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lists (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # Tasks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            list_id INTEGER NOT NULL REFERENCES lists(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            deadline TIMESTAMP,
            reminder TIMESTAMP,
            repeat TEXT,
            completed BOOLEAN DEFAULT FALSE,
            completed_at TIMESTAMP,
            action_plan TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # Subtasks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subtasks (
            id SERIAL PRIMARY KEY,
            task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            deadline TIMESTAMP,
            reminder TIMESTAMP,
            completed BOOLEAN DEFAULT FALSE,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # Focus Stats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS focus_stats (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            total_focus_time INTEGER DEFAULT 0,
            pomodoros_completed INTEGER DEFAULT 0,
            last_session_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id)
        );
    ''')

    # Task Focus Stats table to track focus time per task
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_focus_stats (
            id SERIAL PRIMARY KEY,
            task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            focus_time_seconds INTEGER DEFAULT 0,
            sessions_completed INTEGER DEFAULT 0,
            last_session_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(task_id)
        );
    ''')

    # Focus Session History table to track individual focus sessions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS focus_session_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
            session_type VARCHAR(20) NOT NULL, -- 'pomodoro', 'short_break', 'long_break'
            duration_seconds INTEGER NOT NULL,
            completed BOOLEAN DEFAULT TRUE,
            session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        );
    ''')

    # Focus Flow State table to track ongoing focus flows
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS focus_flow_state (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            current_task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
            flow_state VARCHAR(20) NOT NULL, -- 'ready', 'focusing', 'break', 'completed'
            current_mode VARCHAR(20) NOT NULL, -- 'pomodoro', 'short_break', 'long_break'
            time_remaining_seconds INTEGER,
            current_session_start TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id)
        );
    ''')

    # Timer Settings table to store user timer preferences
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS timer_settings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            pomodoro_duration INTEGER DEFAULT 25,
            short_break_duration INTEGER DEFAULT 5,
            long_break_duration INTEGER DEFAULT 15,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id)
        );
    ''')

    # Vision Board Categories
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vision_board_categories (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        );
    ''')

    # Vision Board Tiles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vision_board_tiles (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            description TEXT,
            image_path TEXT,
            image_url TEXT,
            is_affirmation BOOLEAN DEFAULT FALSE,
            category_id INTEGER REFERENCES vision_board_categories(id) ON DELETE SET NULL,
            position INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # Default Lists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS default_lists (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        );
    ''')

    # Populate defaults (optional)
    cursor.execute("SELECT COUNT(*) FROM default_lists;")
    if cursor.fetchone()['count'] == 0:
        for name in ["Work", "Health", "Errands", "Miscellaneous"]:
            cursor.execute("INSERT INTO default_lists (name) VALUES (%s);", (name,))

    cursor.execute("SELECT COUNT(*) FROM vision_board_categories;")
    if cursor.fetchone()['count'] == 0:
        for cat in ["Health", "Career", "Travel", "Finance", "Relationships", "Personal Growth", "Other"]:
            cursor.execute("INSERT INTO vision_board_categories (name) VALUES (%s);", (cat,))

    # Add vision board customizations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vision_board_customizations (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            category_key TEXT NOT NULL,
            theme TEXT,
            frame TEXT,
            description TEXT,
            bg_image TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, category_key)
        );
    ''')

    conn.commit()
    conn.close()

def create_default_lists_for_user(user_id):
    """Create default lists for a new user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get default list names
    cursor.execute("SELECT name FROM default_lists")
    default_lists = cursor.fetchall()
    
    # Create each default list for the user
    for list_row in default_lists:
        cursor.execute(
            "INSERT INTO lists (user_id, name) VALUES (%s, %s)",
            (user_id, list_row["name"])
        )
    
    conn.commit()
    conn.close()

def get_all_lists_for_user(user_id):
    """Get all lists for a specific user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, name FROM lists WHERE user_id = %s ORDER BY name",
        (user_id,)
    )
    
    lists = cursor.fetchall()
    conn.close()
    
    return lists

def get_list_id_by_name(user_id, list_name):
    """Get list ID by name for a specific user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id FROM lists WHERE user_id = %s AND name = %s",
        (user_id, list_name)
    )
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result["id"]
    return None

def add_new_list(user_id, list_name):
    """Add a new list for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO lists (user_id, name) VALUES (%s, %s)",
            (user_id, list_name)
        )
        conn.commit()
        result = True
    except psycopg2.Error:
        conn.rollback()
        result = False
    
    conn.close()
    return result

def get_tasks_for_list(list_id, user_id):
    """Get all tasks for a specific list"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query now returns all tasks, including completed ones
    cursor.execute('''
    SELECT id, name, deadline, reminder, repeat, completed, completed_at, action_plan
    FROM tasks 
    WHERE list_id = %s AND user_id = %s
    ORDER BY completed, deadline IS NULL, deadline, created_at
    ''', (list_id, user_id))
    
    tasks = cursor.fetchall()
    conn.close()
    
    return tasks

def add_new_task(list_id, user_id, name, deadline=None, reminder=None, repeat=None):
    """Add a new task to a list"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO tasks (list_id, user_id, name, deadline, reminder, repeat) 
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        ''', (list_id, user_id, name, deadline, reminder, repeat))
        
        task_id = cursor.fetchone()['id']
        conn.commit()
        conn.close()
        return task_id
    except psycopg2.Error:
        conn.rollback()
        conn.close()
        return None

def update_task(task_id, name=None, deadline=None, reminder=None, repeat=None, completed=None, action_plan=None):
    """Update an existing task"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build the update query dynamically based on provided parameters
    update_fields = []
    params = []
    
    if name is not None:
        update_fields.append("name = %s")
        params.append(name)
    
    if deadline is not None:
        update_fields.append("deadline = %s")
        params.append(deadline)
    
    if reminder is not None:
        update_fields.append("reminder = %s")
        params.append(reminder)
    
    if repeat is not None:
        update_fields.append("repeat = %s")
        params.append(repeat)
    
    if completed is not None:
        update_fields.append("completed = %s")
        params.append(completed)
        
        if completed:
            update_fields.append("completed_at = CURRENT_TIMESTAMP")
        else:
            update_fields.append("completed_at = NULL")
    
    if action_plan is not None:
        update_fields.append("action_plan = %s")
        params.append(action_plan)
    
    if not update_fields:
        conn.close()
        return False
    
    # Build the final query
    query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = %s"
    params.append(task_id)
    
    try:
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        return True
    except psycopg2.Error:
        conn.rollback()
        conn.close()
        return False

def delete_task(task_id):
    """Delete a task and its subtasks"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Subtasks will be deleted automatically due to CASCADE constraint
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        conn.commit()
        conn.close()
        return True
    except psycopg2.Error:
        conn.rollback()
        conn.close()
        return False

def get_subtasks_for_task(task_id):
    """Get all subtasks for a specific task"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id, name, deadline, reminder, completed, completed_at
    FROM subtasks 
    WHERE task_id = %s
    ORDER BY id
    ''', (task_id,))
    
    subtasks = cursor.fetchall()
    conn.close()
    
    return subtasks

def add_subtasks_for_task(task_id, subtasks):
    """Add multiple subtasks for a task, replacing any existing ones"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # First delete any existing subtasks
        cursor.execute("DELETE FROM subtasks WHERE task_id = %s", (task_id,))
        
        # Then add the new subtasks
        for subtask in subtasks:
            cursor.execute('''
            INSERT INTO subtasks (task_id, name) 
            VALUES (%s, %s)
            ''', (task_id, subtask))
        
        conn.commit()
        conn.close()
        return True
    except psycopg2.Error:
        conn.rollback()
        conn.close()
        return False

def update_subtask(subtask_id, name=None, deadline=None, reminder=None, completed=None):
    """Update an existing subtask"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build the update query dynamically based on provided parameters
    update_fields = []
    params = []
    
    if name is not None:
        update_fields.append("name = %s")
        params.append(name)
    
    if deadline is not None:
        update_fields.append("deadline = %s")
        params.append(deadline)
    
    if reminder is not None:
        update_fields.append("reminder = %s")
        params.append(reminder)
    
    if completed is not None:
        update_fields.append("completed = %s")
        params.append(completed)
        
        if completed:
            update_fields.append("completed_at = CURRENT_TIMESTAMP")
        else:
            update_fields.append("completed_at = NULL")
    
    if not update_fields:
        conn.close()
        return False
    
    # Build the final query
    query = f"UPDATE subtasks SET {', '.join(update_fields)} WHERE id = %s"
    params.append(subtask_id)
    
    try:
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        return True
    except psycopg2.Error:
        conn.rollback()
        conn.close()
        return False

def get_task_statistics(user_id):
    """Get task statistics for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get total tasks and completed tasks
    cursor.execute('''
    SELECT 
        COUNT(*) as total_tasks,
        SUM(CASE WHEN completed = TRUE THEN 1 ELSE 0 END) as completed_tasks
    FROM tasks 
    WHERE user_id = %s
    ''', (user_id,))
    
    task_stats = cursor.fetchone()
    
    # Get total subtasks and completed subtasks
    cursor.execute('''
    SELECT 
        COUNT(*) as total_subtasks,
        SUM(CASE WHEN subtasks.completed = TRUE THEN 1 ELSE 0 END) as completed_subtasks
    FROM subtasks
    JOIN tasks ON subtasks.task_id = tasks.id
    WHERE tasks.user_id = %s
    ''', (user_id,))
    
    subtask_stats = cursor.fetchone()
    
    conn.close()
    
    return {
        "total_tasks": task_stats["total_tasks"] if task_stats["total_tasks"] else 0,
        "completed_tasks": task_stats["completed_tasks"] if task_stats["completed_tasks"] else 0,
        "total_subtasks": subtask_stats["total_subtasks"] if subtask_stats["total_subtasks"] else 0,
        "completed_subtasks": subtask_stats["completed_subtasks"] if subtask_stats["completed_subtasks"] else 0
    }

def get_upcoming_tasks(user_id, limit=5):
    """Get upcoming tasks for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT tasks.id, tasks.name, tasks.deadline, lists.name as list_name
    FROM tasks
    JOIN lists ON tasks.list_id = lists.id
    WHERE tasks.user_id = %s AND tasks.completed = FALSE AND tasks.deadline IS NOT NULL
    ORDER BY tasks.deadline ASC
    LIMIT %s
    ''', (user_id, limit))
    
    upcoming_tasks = cursor.fetchall()
    conn.close()
    
    return upcoming_tasks

# Vision Board functions

def get_vision_board_categories():
    """Get all vision board categories"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name FROM vision_board_categories ORDER BY name")
    
    categories = cursor.fetchall()
    conn.close()
    
    return categories

def get_user_vision_board_theme(user_id):
    """Get a user's vision board theme"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT vision_board_theme FROM users WHERE id = %s", (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result["vision_board_theme"]
    return "default"

def update_vision_board_theme(user_id, theme):
    """Update a user's vision board theme"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE users SET vision_board_theme = %s WHERE id = %s",
            (theme, user_id)
        )
        conn.commit()
        result = True
    except psycopg2.Error:
        conn.rollback()
        result = False
    
    conn.close()
    return result

def get_vision_board_tiles(user_id, category_id=None):
    """Get all vision board tiles for a user, optionally filtered by category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT t.id, t.title, t.description, t.image_path, t.image_url, 
           t.is_affirmation, t.category_id, t.position, c.name as category_name
    FROM vision_board_tiles t
    LEFT JOIN vision_board_categories c ON t.category_id = c.id
    WHERE t.user_id = %s
    """
    
    params = [user_id]
    
    if category_id:
        query += " AND t.category_id = %s"
        params.append(category_id)
    
    query += " ORDER BY t.position"
    
    cursor.execute(query, params)
    
    tiles = cursor.fetchall()
    conn.close()
    
    return tiles

def add_vision_board_tile(user_id, title, description=None, image_path=None, 
                          image_url=None, is_affirmation=False, category_id=None):
    """Add a new vision board tile"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get the highest position value to place the new tile at the end
        cursor.execute(
            "SELECT COALESCE(MAX(position), 0) as max_pos FROM vision_board_tiles WHERE user_id = %s",
            (user_id,)
        )
        result = cursor.fetchone()
        next_position = result["max_pos"] + 1 if result else 1
        
        cursor.execute('''
        INSERT INTO vision_board_tiles 
        (user_id, title, description, image_path, image_url, is_affirmation, category_id, position) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        ''', (user_id, title, description, image_path, image_url, 
              is_affirmation, category_id, next_position))
        
        tile_id = cursor.fetchone()['id']
        conn.commit()
        conn.close()
        return tile_id
    except psycopg2.Error:
        conn.rollback()
        conn.close()
        return None

def update_vision_board_tile(tile_id, user_id, title=None, description=None, 
                             image_path=None, image_url=None, is_affirmation=None, category_id=None):
    """Update an existing vision board tile"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build the update query dynamically based on provided parameters
    update_fields = []
    params = []
    
    if title is not None:
        update_fields.append("title = %s")
        params.append(title)
    
    if description is not None:
        update_fields.append("description = %s")
        params.append(description)
    
    if image_path is not None:
        update_fields.append("image_path = %s")
        params.append(image_path)
    
    if image_url is not None:
        update_fields.append("image_url = %s")
        params.append(image_url)
    
    if is_affirmation is not None:
        update_fields.append("is_affirmation = %s")
        params.append(is_affirmation)
    
    if category_id is not None:
        update_fields.append("category_id = %s")
        params.append(category_id)
    
    if not update_fields:
        conn.close()
        return False
    
    # Build the final query
    query = f"UPDATE vision_board_tiles SET {', '.join(update_fields)} WHERE id = %s AND user_id = %s"
    params.append(tile_id)
    params.append(user_id)
    
    try:
        cursor.execute(query, params)
        conn.commit()
        result = cursor.rowcount > 0
        conn.close()
        return result
    except psycopg2.Error:
        conn.rollback()
        conn.close()
        return False

def delete_vision_board_tile(tile_id, user_id):
    """Delete a vision board tile"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "DELETE FROM vision_board_tiles WHERE id = %s AND user_id = %s", 
            (tile_id, user_id)
        )
        conn.commit()
        result = cursor.rowcount > 0
        
        # Reorder positions to close gaps
        if result:
            cursor.execute(
                "SELECT id FROM vision_board_tiles WHERE user_id = %s ORDER BY position", 
                (user_id,)
            )
            tiles = cursor.fetchall()
            
            for i, tile in enumerate(tiles, 1):
                cursor.execute(
                    "UPDATE vision_board_tiles SET position = %s WHERE id = %s",
                    (i, tile["id"])
                )
            
            conn.commit()
        
        conn.close()
        return result
    except psycopg2.Error:
        conn.rollback()
        conn.close()
        return False

def update_tile_positions(positions_dict, user_id):
    """Update tile positions in the vision board"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for tile_id, position in positions_dict.items():
            # Only update if the tile belongs to the user
            cursor.execute(
                """
                UPDATE vision_board_tiles 
                SET position = %s 
                WHERE id = %s AND user_id = %s
                """,
                (position, tile_id, user_id)
            )
        
        conn.commit()
        conn.close()
        
        return True
    except psycopg2.Error as e:
        conn.rollback()
        conn.close()
        print(f"Error updating tile positions: {e}")
        return False

def get_focus_stats(user_id):
    """Get focus statistics for a user from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Try to get existing stats
    cursor.execute("""
        SELECT total_focus_time, pomodoros_completed, last_session_date 
        FROM focus_stats 
        WHERE user_id = %s
    """, (user_id,))
    
    stats = cursor.fetchone()
    conn.close()
    
    if stats:
        return stats
    else:
        # Return default values if no stats exist
        return {
            "total_focus_time": 0,
            "pomodoros_completed": 0,
            "last_session_date": None
        }

def update_focus_stats(user_id, total_focus_time, pomodoros_completed):
    """Update focus statistics for a user in the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if record exists
        cursor.execute("SELECT id FROM focus_stats WHERE user_id = %s", (user_id,))
        exists = cursor.fetchone()
        
        if exists:
            # Update existing record
            cursor.execute("""
                UPDATE focus_stats 
                SET total_focus_time = %s, 
                    pomodoros_completed = %s, 
                    last_session_date = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
            """, (total_focus_time, pomodoros_completed, user_id))
        else:
            # Insert new record
            cursor.execute("""
                INSERT INTO focus_stats 
                (user_id, total_focus_time, pomodoros_completed, last_session_date) 
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            """, (user_id, total_focus_time, pomodoros_completed))
        
        conn.commit()
        conn.close()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        conn.close()
        print(f"Error updating focus stats: {e}")
        return False

def reset_focus_stats(user_id):
    """Reset focus statistics for a user in the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE focus_stats 
            SET total_focus_time = 0, 
                pomodoros_completed = 0, 
                last_session_date = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
        """, (user_id,))
        
        # If no record exists yet, create one
        if cursor.rowcount == 0:
            cursor.execute("""
                INSERT INTO focus_stats 
                (user_id, total_focus_time, pomodoros_completed, last_session_date) 
                VALUES (%s, 0, 0, CURRENT_TIMESTAMP)
            """, (user_id,))
        
        conn.commit()
        conn.close()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        conn.close()
        print(f"Error resetting focus stats: {e}")
        return False

def get_tasks(user_id):
    """Get all tasks for a user (for focus page task selection)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        SELECT tasks.id, tasks.name as title
        FROM tasks
        WHERE tasks.user_id = %s AND tasks.completed = FALSE
        ORDER BY tasks.deadline IS NULL, tasks.deadline, tasks.created_at
        ''', (user_id,))
        
        tasks = cursor.fetchall()
        conn.close()
        return tasks
    except psycopg2.Error as e:
        conn.close()
        print(f"Error getting tasks: {e}")
        return []

def get_task_focus_stats(task_id):
    """Get focus statistics for a specific task from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print(f"DEBUG DB: Getting focus stats for task_id={task_id}")
    
    # Try to get existing stats
    cursor.execute("""
        SELECT task_id, focus_time_seconds, sessions_completed, last_session_date 
        FROM task_focus_stats 
        WHERE task_id = %s
    """, (task_id,))
    
    stats = cursor.fetchone()
    conn.close()
    
    if stats:
        print(f"DEBUG DB: Found stats for task_id={task_id}: time={stats['focus_time_seconds']}s, sessions={stats['sessions_completed']}")
        return stats
    else:
        print(f"DEBUG DB: No stats found for task_id={task_id}")
        # Return default values if no stats exist
        return {
            "task_id": task_id,
            "focus_time_seconds": 0,
            "sessions_completed": 0,
            "last_session_date": None
        }

def update_task_focus_stats(task_id, user_id, focus_time_seconds, sessions_completed):
    """Update focus statistics for a specific task in the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print(f"DEBUG DB: Updating task focus stats: task_id={task_id}, user_id={user_id}, seconds={focus_time_seconds}, sessions={sessions_completed}")
    
    try:
        # First get the list ID for this task for more comprehensive analytics
        cursor.execute("SELECT list_id FROM tasks WHERE id = %s", (task_id,))
        task_info = cursor.fetchone()
        list_id = task_info['list_id'] if task_info else None
        
        # Check if record exists
        cursor.execute("SELECT id FROM task_focus_stats WHERE task_id = %s", (task_id,))
        exists = cursor.fetchone()
        
        if exists:
            print(f"DEBUG DB: Updating existing record for task_id={task_id}")
            # Update existing record
            cursor.execute("""
                UPDATE task_focus_stats 
                SET focus_time_seconds = focus_time_seconds + %s, 
                    sessions_completed = sessions_completed + %s, 
                    last_session_date = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE task_id = %s
            """, (focus_time_seconds, sessions_completed, task_id))
        else:
            print(f"DEBUG DB: Creating new record for task_id={task_id}")
            # Insert new record
            cursor.execute("""
                INSERT INTO task_focus_stats 
                (task_id, user_id, focus_time_seconds, sessions_completed, last_session_date) 
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (task_id, user_id, focus_time_seconds, sessions_completed))
        
        conn.commit()
        conn.close()
        print(f"DEBUG DB: Successfully updated task focus stats for task_id={task_id}")
        return True
    except psycopg2.Error as e:
        conn.rollback()
        conn.close()
        print(f"DEBUG DB ERROR: Error updating task focus stats: {e}")
        return False

def get_task_id_by_name(user_id, task_name):
    """Get task ID by name for a specific user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print(f"DEBUG DB: Looking up task ID for name/title: '{task_name}', user_id: {user_id}")
    
    # First try by name field
    cursor.execute("""
        SELECT id FROM tasks 
        WHERE user_id = %s AND name = %s 
        ORDER BY created_at DESC 
        LIMIT 1
    """, (user_id, task_name))
    
    result = cursor.fetchone()
    
    if not result:
        # If not found by name, try by title (which is the name column in the get_tasks function)
        print(f"DEBUG DB: Not found by name, trying direct title match")
        cursor.execute("""
            SELECT id FROM tasks 
            WHERE user_id = %s AND name = %s 
            ORDER BY created_at DESC 
            LIMIT 1
        """, (user_id, task_name))
        
        result = cursor.fetchone()
    
    if not result:
        # If still not found, try with LIKE for partial or fuzzy matches
        print(f"DEBUG DB: No exact matches, trying fuzzy search")
        cursor.execute("""
            SELECT id FROM tasks 
            WHERE user_id = %s AND name LIKE %s 
            ORDER BY created_at DESC 
            LIMIT 1
        """, (user_id, f"%{task_name}%"))
        
        result = cursor.fetchone()
    
    conn.close()
    
    if result:
        print(f"DEBUG DB: Found task ID: {result['id']}")
        return result["id"]
    else:
        print(f"DEBUG DB: No task found with name/title: '{task_name}'")
        # For debugging, let's also list all tasks for this user
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM tasks WHERE user_id = %s", (user_id,))
        all_tasks = cursor.fetchall()
        print(f"DEBUG DB: All tasks for user {user_id}:")
        for t in all_tasks:
            print(f"  - ID: {t['id']}, Name: '{t['name']}'")
        conn.close()
        return None

def get_timer_settings(user_id):
    """Get timer settings for a user from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Try to get existing settings
    cursor.execute("""
        SELECT pomodoro_duration, short_break_duration, long_break_duration 
        FROM timer_settings 
        WHERE user_id = %s
    """, (user_id,))
    
    settings = cursor.fetchone()
    conn.close()
    
    if settings:
        return settings
    else:
        # Return default values if no settings exist
        return {
            "pomodoro_duration": 25,
            "short_break_duration": 5,
            "long_break_duration": 15
        }

def update_timer_settings(user_id, pomodoro_duration, short_break_duration, long_break_duration):
    """Update timer settings for a user in the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if record exists
        cursor.execute("SELECT id FROM timer_settings WHERE user_id = %s", (user_id,))
        exists = cursor.fetchone()
        
        if exists:
            # Update existing record
            cursor.execute("""
                UPDATE timer_settings 
                SET pomodoro_duration = %s, 
                    short_break_duration = %s, 
                    long_break_duration = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
            """, (pomodoro_duration, short_break_duration, long_break_duration, user_id))
        else:
            # Insert new record
            cursor.execute("""
                INSERT INTO timer_settings 
                (user_id, pomodoro_duration, short_break_duration, long_break_duration) 
                VALUES (%s, %s, %s, %s)
            """, (user_id, pomodoro_duration, short_break_duration, long_break_duration))
        
        conn.commit()
        conn.close()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        conn.close()
        print(f"Error updating timer settings: {e}")
        return False

def get_focus_stats_by_list(user_id):
    """Get focus time statistics organized by list for a specific user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query to get focus stats grouped by list
    cursor.execute("""
        SELECT l.name as list_name, 
               COALESCE(SUM(tfs.focus_time_seconds), 0) as total_focus_time,
               COALESCE(SUM(tfs.sessions_completed), 0) as total_sessions
        FROM lists l
        LEFT JOIN tasks t ON l.id = t.list_id
        LEFT JOIN task_focus_stats tfs ON t.id = tfs.task_id
        WHERE l.user_id = %s
        GROUP BY l.name
        ORDER BY total_focus_time DESC
    """, (user_id,))
    
    list_stats = cursor.fetchall()
    conn.close()
    
    return list_stats

def get_unlinked_focus_stats(user_id):
    """Get total focus time for sessions that weren't linked to any task"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # First get total focus time
    cursor.execute("""
        SELECT total_focus_time, pomodoros_completed 
        FROM focus_stats 
        WHERE user_id = %s
    """, (user_id,))
    
    overall_stats = cursor.fetchone()
    
    if not overall_stats:
        conn.close()
        return {"unlinked_focus_time": 0, "unlinked_sessions": 0}
    
    # Get sum of task-specific focus time
    cursor.execute("""
        SELECT COALESCE(SUM(focus_time_seconds), 0) as linked_focus_time,
               COALESCE(SUM(sessions_completed), 0) as linked_sessions
        FROM task_focus_stats
        WHERE user_id = %s
    """, (user_id,))
    
    linked_stats = cursor.fetchone()
    
    conn.close()
    
    # Calculate unlinked time by subtracting linked time from total
    unlinked_focus_time = overall_stats['total_focus_time'] - (linked_stats['linked_focus_time'] if linked_stats else 0)
    unlinked_sessions = overall_stats['pomodoros_completed'] - (linked_stats['linked_sessions'] if linked_stats else 0)
    
    # Ensure we don't have negative values (shouldn't happen, but just in case)
    unlinked_focus_time = max(0, unlinked_focus_time)
    unlinked_sessions = max(0, unlinked_sessions)
    
    return {
        "unlinked_focus_time": unlinked_focus_time, 
        "unlinked_sessions": unlinked_sessions
    }

def get_task_focus_stats_for_user(user_id):
    """Get focus time statistics for all tasks of a specific user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query to get focus stats for all tasks
    cursor.execute("""
        SELECT t.name as task_name, 
               l.name as list_name,
               tfs.focus_time_seconds,
               tfs.sessions_completed
        FROM tasks t
        JOIN lists l ON t.list_id = l.id
        JOIN task_focus_stats tfs ON t.id = tfs.task_id
        WHERE t.user_id = %s
        ORDER BY tfs.focus_time_seconds DESC
        LIMIT 10
    """, (user_id,))
    
    task_stats = cursor.fetchall()
    conn.close()
    
    return task_stats

# New functions for enhanced focus flow

def save_focus_session(user_id, task_id, session_type, duration_seconds, completed=True, notes=None):
    """Save a completed focus session to history"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO focus_session_history 
            (user_id, task_id, session_type, duration_seconds, completed, notes) 
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (user_id, task_id, session_type, duration_seconds, completed, notes))
        
        result = cursor.fetchone()
        session_id = result['id'] if result else None
        conn.commit()
        conn.close()
        return session_id
    except psycopg2.Error as e:
        conn.rollback()
        conn.close()
        print(f"Error saving focus session: {e}")
        return None

def get_focus_sessions_for_task(user_id, task_id, limit=10):
    """Get focus session history for a specific task"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, session_type, duration_seconds, completed, session_date, notes
        FROM focus_session_history
        WHERE user_id = %s AND task_id = %s
        ORDER BY session_date DESC
        LIMIT %s
    """, (user_id, task_id, limit))
    
    sessions = cursor.fetchall()
    conn.close()
    
    return sessions

def get_recent_focus_sessions(user_id, limit=20):
    """Get recent focus sessions for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT fsh.id, fsh.session_type, fsh.duration_seconds, 
               fsh.completed, fsh.session_date, fsh.notes,
               t.id as task_id, t.name as task_name
        FROM focus_session_history fsh
        LEFT JOIN tasks t ON fsh.task_id = t.id
        WHERE fsh.user_id = %s
        ORDER BY fsh.session_date DESC
        LIMIT %s
    """, (user_id, limit))
    
    sessions = cursor.fetchall()
    conn.close()
    
    return sessions

def get_focus_flow_state(user_id):
    """Get current focus flow state for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT current_task_id, flow_state, current_mode, 
               time_remaining_seconds, current_session_start, last_updated
        FROM focus_flow_state
        WHERE user_id = %s
    """, (user_id,))
    
    state = cursor.fetchone()
    conn.close()
    
    if state:
        # If there's a linked task, get its name
        if state['current_task_id']:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM tasks WHERE id = %s", (state['current_task_id'],))
            task = cursor.fetchone()
            conn.close()
            
            if task:
                state['task_name'] = task['name']
        
        return state
    else:
        # Return default values if no state exists
        return {
            "current_task_id": None,
            "task_name": None,
            "flow_state": "ready",
            "current_mode": "pomodoro",
            "time_remaining_seconds": None,
            "current_session_start": None,
            "last_updated": None
        }

def update_focus_flow_state(user_id, flow_state, current_mode, time_remaining=None, 
                          task_id=None, session_start=None):
    """Update focus flow state for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if record exists
        cursor.execute("SELECT id FROM focus_flow_state WHERE user_id = %s", (user_id,))
        exists = cursor.fetchone()
        
        if exists:
            # Update existing record
            cursor.execute("""
                UPDATE focus_flow_state 
                SET flow_state = %s, 
                    current_mode = %s, 
                    time_remaining_seconds = %s,
                    current_task_id = %s,
                    current_session_start = %s,
                    last_updated = CURRENT_TIMESTAMP
                WHERE user_id = %s
            """, (flow_state, current_mode, time_remaining, task_id, session_start, user_id))
        else:
            # Insert new record
            cursor.execute("""
                INSERT INTO focus_flow_state 
                (user_id, flow_state, current_mode, time_remaining_seconds, 
                 current_task_id, current_session_start) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, flow_state, current_mode, time_remaining, task_id, session_start))
        
        conn.commit()
        conn.close()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        conn.close()
        print(f"Error updating focus flow state: {e}")
        return False

def get_daily_task_focus_summary(user_id, date=None):
    """Get summary of focus sessions for each task for a specific day"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # If no date provided, use today
    if not date:
        date = datetime.date.today()
    
    # Convert date to string in format YYYY-MM-DD
    date_str = date.strftime("%Y-%m-%d")
    
    cursor.execute("""
        SELECT t.id as task_id, t.name as task_name, 
               l.name as list_name,
               COUNT(fsh.id) as session_count,
               SUM(fsh.duration_seconds) as total_duration
        FROM focus_session_history fsh
        JOIN tasks t ON fsh.task_id = t.id
        JOIN lists l ON t.list_id = l.id
        WHERE fsh.user_id = %s 
          AND fsh.session_type = 'pomodoro'
          AND DATE(fsh.session_date) = %s
        GROUP BY t.id, t.name, l.name
        ORDER BY total_duration DESC
    """, (user_id, date_str))
    
    task_summary = cursor.fetchall()
    
    # Get unlinked sessions (if any)
    cursor.execute("""
        SELECT COUNT(*) as session_count,
               SUM(duration_seconds) as total_duration
        FROM focus_session_history
        WHERE user_id = %s 
          AND session_type = 'pomodoro'
          AND task_id IS NULL
          AND DATE(session_date) = %s
    """, (user_id, date_str))
    
    unlinked = cursor.fetchone()
    
    conn.close()
    
    # Prepare result
    result = {
        "date": date_str,
        "tasks": task_summary,
        "unlinked": {
            "session_count": unlinked["session_count"] if unlinked and unlinked["session_count"] else 0,
            "total_duration": unlinked["total_duration"] if unlinked and unlinked["total_duration"] else 0
        }
    }
    
    return result

def get_focus_weekday_stats(user_id, weeks=4):
    """Get focus session statistics by day of the week for recent weeks"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Calculate date range (e.g., last 4 weeks)
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(weeks=weeks)
    
    # Get stats by day of week
    cursor.execute("""
        SELECT 
            EXTRACT(DOW FROM session_date) as day_of_week,
            COUNT(*) as session_count,
            SUM(duration_seconds) as total_duration,
            AVG(duration_seconds) as avg_duration
        FROM focus_session_history
        WHERE user_id = %s 
          AND session_type = 'pomodoro'
          AND session_date BETWEEN %s AND %s
        GROUP BY day_of_week
        ORDER BY day_of_week
    """, (user_id, start_date, end_date))
    
    weekday_stats = cursor.fetchall()
    conn.close()
    
    # Map day numbers to names (0=Sunday, 1=Monday, etc.)
    day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    
    # Format results with day names
    results = []
    for stat in weekday_stats:
        day_num = int(stat['day_of_week'])
        results.append({
            'day': day_names[day_num],
            'day_num': day_num,
            'session_count': stat['session_count'],
            'total_duration': stat['total_duration'],
            'avg_duration': stat['avg_duration']
        })
    
    # Add missing days with zero values
    existing_days = [r['day_num'] for r in results]
    for day_num in range(7):
        if day_num not in existing_days:
            results.append({
                'day': day_names[day_num],
                'day_num': day_num,
                'session_count': 0,
                'total_duration': 0,
                'avg_duration': 0
            })
    
    # Sort by day of week
    results.sort(key=lambda x: x['day_num'])
    
    return results

def save_vision_board_customizations(user_id, customizations):
    """Save vision board customizations for a user"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First delete existing customizations
        cursor.execute(
            "DELETE FROM vision_board_customizations WHERE user_id = %s",
            (user_id,)
        )
        
        # Insert new customizations
        for cat_key, settings in customizations.items():
            cursor.execute("""
                INSERT INTO vision_board_customizations 
                (user_id, category_key, theme, frame, description, bg_image)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                user_id, 
                cat_key,
                settings.get('theme'),
                settings.get('frame'),
                settings.get('description'),
                settings.get('bg_image')
            ))
        
        conn.commit()
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error saving vision board customizations: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def load_vision_board_customizations(user_id):
    """Load vision board customizations for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT category_key, theme, frame, description, bg_image 
            FROM vision_board_customizations 
            WHERE user_id = %s
        """, (user_id,))
        
        customizations = {}
        for row in cursor.fetchall():
            customizations[row['category_key']] = {
                'theme': row['theme'],
                'frame': row['frame'],
                'description': row['description'],
                'bg_image': row['bg_image']
            }
        
        return customizations
    except Exception as e:
        print(f"Error loading vision board customizations: {str(e)}")
        return {}
    finally:
        conn.close()