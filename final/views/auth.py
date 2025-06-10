import streamlit as st
import re
import os
import pathlib
from utils.auth import register_user, login_user, get_user_by_email, hash_password, reactivate_account
from utils.theme import apply_theme_aware_styles
from utils.email_service import send_welcome_email, send_password_reminder_email
import uuid
from datetime import datetime, timedelta
from utils.db import get_db_connection

def validate_email(email):
    """Validate email format and perform additional checks"""
    if not email:
        return False, "Email is required"
    
    # Handle potential whitespace from autofill
    email = email.strip()
    
    # Basic format validation
    basic_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(basic_pattern, email):
        return False, "Invalid email format"
    
    # Length check
    if len(email) > 320:  # Max email length according to RFC 5321
        return False, "Email is too long"
    
    # Domain validation (ensure it has a valid TLD)
    try:
        domain_parts = email.split('@')[1].split('.')
        if len(domain_parts) < 2 or len(domain_parts[-1]) < 2:
            return False, "Invalid email domain"
    except (IndexError, AttributeError):
        # Catch any issues with parsing the email
        return False, "Invalid email format"
    
    # Common typos in domain names
    try:
        domain = email.split('@')[1].lower()
        
        common_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com']
        
        for valid_domain in common_domains:
            # Check for small typos (one character difference)
            if domain != valid_domain and domain.replace('.', '') == valid_domain.replace('.', ''):
                return False, f"Did you mean {valid_domain}?"
            
            # Check for common typos
            if valid_domain == 'gmail.com' and domain in ['gamil.com', 'gmial.com', 'gmai.com', 'gmal.com']:
                return False, "Did you mean gmail.com?"
            if valid_domain == 'hotmail.com' and domain in ['homtail.com', 'hotmai.com', 'hotmial.com']:
                return False, "Did you mean hotmail.com?"
            if valid_domain == 'yahoo.com' and domain in ['yaho.com', 'yahooo.com', 'yhaoo.com']:
                return False, "Did you mean yahoo.com?"
            if valid_domain == 'outlook.com' and domain in ['outlok.com', 'outook.com', 'outlokk.com']:
                return False, "Did you mean outlook.com?"
    except (IndexError, AttributeError):
        # If there are any parsing issues, let's simply pass through this check
        pass
    
    return True, None

def validate_password(password):
    """Validate password strength with multiple requirements"""
    if not password:
        return False, "Password is required"
    
    # Length check
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # Check for uppercase letters
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for lowercase letters
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for digits
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    # Check for special characters
    special_chars = "!@#$%^&*()-_=+[]{}|;:,.<>?/"
    if not any(c in special_chars for c in password):
        return False, "Password must contain at least one special character"
    
    # Check for common passwords (very basic list for example)
    common_passwords = [
        "password", "password123", "123456", "qwerty", 
        "abc123", "letmein", "welcome", "admin"
    ]
    if password.lower() in common_passwords:
        return False, "This password is too common and easily guessed"
    
    return True, None

def show_auth_page():
    """Display authentication page with login and signup forms"""
    # Apply theme-aware styling
    is_dark_theme = apply_theme_aware_styles()
    
    # Apply theme-aware styling
    if is_dark_theme:
        primary_color = "#BB86FC"
        secondary_color = "#03DAC6"
        text_color = "#F1F1F1"
        secondary_text_color = "#64B5F6"  # Light blue instead of gray
    else:
        primary_color = "#6200EA"
        secondary_color = "#018786"
        text_color = "#212529"
        secondary_text_color = "#1976D2"  # Darker blue
    
    # Custom CSS for auth forms - theme-specific
    if is_dark_theme:
        st.markdown(f"""
        <style>
        .auth-container {{
            max-width: 500px;
            margin: 2rem auto;
            padding: 2rem;
            background-color: #1E1E1E;
            border-radius: 1rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
            border: 1px solid #333333;
        }}
        .auth-header {{
            text-align: center;
            font-size: 2.2rem;
            font-weight: 700;
            color: {primary_color};
            margin-bottom: 1.5rem;
        }}
        .auth-subheader {{
            text-align: center;
            font-size: 1.2rem;
            color: {text_color};
            margin-bottom: 2rem;
        }}
        .auth-tabs {{
            display: flex;
            margin-bottom: 2rem;
        }}
        .auth-tab {{
            flex: 1;
            text-align: center;
            padding: 0.75rem;
            cursor: pointer;
            border-bottom: 3px solid #333333;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        .auth-tab.active {{
            border-bottom: 3px solid {primary_color};
            color: {primary_color};
        }}
        div.stButton > button {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            margin: 0;
            line-height: 1.6;
            width: 100%;
        }}
        div.stButton > button[kind="primary"] {{
            background-color: {primary_color};
            color: #1E1E1E;
            border: none;
        }}
        div.stButton > button[kind="secondary"] {{
            background-color: transparent;
            color: {primary_color};
            border: 2px solid {primary_color};
        }}
        /* Fix for logo display in dark mode */
        .logo-container img {{
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            padding: 5px;
        }}
        /* Make form inputs visible in dark mode */
        .stTextInput > div > div > input {{
            background-color: #2D2D2D !important;
            color: #F1F1F1 !important;
            border-color: #444444 !important;
            caret-color: {primary_color} !important;
        }}
        .stTextInput > div > div > input:focus {{
            border: 2px solid {primary_color} !important;
            box-shadow: 0 0 0 1px {primary_color} !important;
        }}
        .stRadio > div {{
            background-color: transparent !important;
        }}
        .stRadio > div > div > label {{
            color: #F1F1F1 !important;
        }}
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
    <style>
        .auth-container {{
        max-width: 500px;
        margin: 2rem auto;
        padding: 2rem;
            background-color: #FFFFFF;
        border-radius: 1rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            border: 1px solid #E6E6E6;
        }}
        .auth-header {{
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
            color: {primary_color};
        margin-bottom: 1.5rem;
        }}
        .auth-subheader {{
        text-align: center;
        font-size: 1.2rem;
            color: {text_color};
            margin-bottom:.5rem;
        }}
        .auth-tabs {{
        display: flex;
        margin-bottom: 2rem;
        }}
        .auth-tab {{
        flex: 1;
        text-align: center;
        padding: 0.75rem;
        cursor: pointer;
            border-bottom: 3px solid #E6E6E6;
        font-weight: 600;
        transition: all 0.3s ease;
        }}
        .auth-tab.active {{
            border-bottom: 3px solid {primary_color};
            color: {primary_color};
        }}
        div.stButton > button {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin: 0;
        line-height: 1.6;
        width: 100%;
        }}
        div.stButton > button[kind="primary"] {{
            background-color: {primary_color};
        color: white;
        border: none;
        }}
        div.stButton > button[kind="secondary"] {{
            background-color: transparent;
            color: {primary_color};
            border: 2px solid {primary_color};
        }}
        /* Fix for logo display in light mode */
        .logo-container img {{
            background-color: white;
            border-radius: 50%;
            padding: 5px;
        }}
        /* Ensure form inputs are properly styled */
        .stTextInput > div > div > input {{
            background-color: #FFFFFF !important;
            color: #212529 !important;
            border-color: #E6E6E6 !important;
            caret-color: {primary_color} !important;
        }}
        .stTextInput > div > div > input:focus {{
            border: 2px solid {primary_color} !important;
            box-shadow: 0 0 0 1px {primary_color} !important;
        }}
        .stRadio > div {{
            background-color: transparent !important;
        }}
        .stRadio > div > div > label {{
            color: #212529 !important;
        }}
        </style>
        """, unsafe_allow_html=True)
    
    # Define additional CSS for centered logo
    st.markdown("""
    <style>
    /* Force center alignment for the logo with !important flags */
    .centered-logo-container {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        margin: 0 auto !important;
        width: 100% !important;
        text-align: center !important;
    }
    
    /* Target Streamlit's column structure directly */
    [data-testid="column"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        flex-direction: column !important;
    }
    
    /* Target the image specifically with highest specificity */
    [data-testid="stImage"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    
    [data-testid="stImage"] > img {
        margin: 0 auto !important;
        display: block !important;
    }
    
    /* Override any potential Streamlit element spacing */
    [data-testid="element-container"] {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with logo
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        # Get the base path and construct the logo path
        base_path = pathlib.Path(__file__).parent.parent
        logo_path = str(base_path / "static/ZenFlowIt_Logo.png")
        
        # Create a direct HTML image tag with inline styling for maximum control
        if os.path.exists(logo_path):
            # Convert the image to base64 for inline embedding
            import base64
            with open(logo_path, "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode()
            
            # Create an HTML img tag with the base64 data
            html = f'''
            <div style="display:flex; justify-content:center; width:100%; text-align:center;">
                <img src="data:image/png;base64,{img_data}" 
                     style="width:150px; margin:0 auto; display:block;" 
                     alt="ZenFlowIt Logo">
            </div>
            '''
            st.markdown(html, unsafe_allow_html=True)
        else:
            # Fallback to standard Streamlit image with our CSS
            st.markdown('<div class="centered-logo-container">', unsafe_allow_html=True)
            try:
                st.image(logo_path, width=150)
            except Exception as e:
                st.error(f"Error loading logo: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)
    
        # Update the welcome message with ZenFlowIt
        st.markdown(f'<h1 class="auth-header">Welcome to ZenFlowIt</h1>', unsafe_allow_html=True)
        st.markdown(f'<p class="auth-subheader" style="color: {secondary_text_color};">Your AI-powered productivity companion</p>', unsafe_allow_html=True)
        
        # Use radio buttons for tab selection
        auth_mode = st.session_state.get('auth_mode', 'login')
        
        # Create radio buttons for tab selection
        new_auth_mode = st.radio(
            "Select",
            ["Login", "Sign Up"],
            index=0 if auth_mode == "login" else 1,
            horizontal=True,
            label_visibility="collapsed"
        )
        
        # Update the session state if the selection changes
        if (new_auth_mode == "Login" and auth_mode != "login") or (new_auth_mode == "Sign Up" and auth_mode != "signup"):
            st.session_state.auth_mode = "login" if new_auth_mode == "Login" else "signup"
            st.rerun()
        
        # Show the appropriate form based on the active tab
        if auth_mode == "login":
            # Login form
            login_email = st.text_input("Email", key="login_email", help="Enter your registered email address")
            login_password = st.text_input("Password", type="password", key="login_password", help="Enter your password")
            
            # Initialize session state for forgot password
            if 'show_forgot_password' not in st.session_state:
                st.session_state.show_forgot_password = False
            
            # Add forgot password button
            forgot_password = st.button("Forgot Password?", key="forgot_password", type="secondary")
            if forgot_password:
                st.session_state.show_forgot_password = True
                st.rerun()
            
            # Show forgot password form
            if st.session_state.show_forgot_password:
                st.markdown("---")
                st.markdown("### Password Recovery")
                reset_email = st.text_input("Enter your email address", key="reset_email")
                
                col1, col2 = st.columns([1,1])
                with col1:
                    if st.button("Send Recovery Email", key="send_recovery"):
                        if not reset_email:
                            st.error("Please enter your email address")
                        else:
                            is_valid_email, email_error = validate_email(reset_email)
                            if not is_valid_email:
                                st.error(email_error)
                            else:
                                user = get_user_by_email(reset_email)
                                if user:
                                    try:
                                        # Generate temporary password
                                        temp_password = str(uuid.uuid4())[:8]
                                        
                                        # Hash the temporary password
                                        temp_password_hash = hash_password(temp_password)
                                        
                                        # Update user's password in database
                                        conn = get_db_connection()
                                        with conn.cursor() as cursor:
                                            cursor.execute(
                                                "UPDATE users SET password_hash = %s WHERE email = %s",
                                                (temp_password_hash, reset_email)
                                            )
                                            conn.commit()
                                        
                                        # Send email with temporary password
                                        success, error = send_password_reminder_email(
                                            reset_email,
                                            user['first_name'],
                                            temp_password
                                        )
                                        
                                        if success:
                                            st.success("A temporary password has been sent to your email. Please check your inbox.")
                                            st.session_state.show_forgot_password = False
                                            st.rerun()
                                        else:
                                            st.error(f"Failed to send email: {error}")
                                    except Exception as e:
                                        st.error(f"An error occurred: {str(e)}")
                                        conn.rollback()
                                    finally:
                                        conn.close()
                                else:
                                    st.error("No account found with this email address")
                
                with col2:
                    if st.button("Cancel", key="cancel_recovery"):
                        st.session_state.show_forgot_password = False
                        st.rerun()
                
                st.markdown("---")
            
            # Only show login button if not showing forgot password form
            if not st.session_state.show_forgot_password:
                if st.button("Login", key="login_submit", type="primary", use_container_width=True):
                    try:
                        # Sanitize inputs
                        login_email = login_email.strip() if login_email else ""
                        
                        # Check for empty required fields
                        empty_fields = []
                        if not login_email: empty_fields.append("Email")
                        if not login_password: empty_fields.append("Password")
                        
                        if empty_fields:
                            st.error(f"Please enter your {' and '.join(empty_fields)}")
                        else:
                            # Use the enhanced email validation
                            is_valid_email, email_error = validate_email(login_email)
                            if not is_valid_email:
                                st.error(email_error)
                            else:
                                user_id, error = login_user(login_email, login_password)
                                
                                if error:
                                    if "marked for deletion" in error:
                                        st.warning(error)
                                        # Show reactivation form in a container
                                        with st.container():
                                            st.info("To reactivate your account, please confirm your password below.")
                                            reactivate_password = st.text_input("Password", type="password", key="reactivate_pwd")
                                            if st.button("Reactivate Account", key="reactivate_btn"):
                                                if not reactivate_password:
                                                    st.error("Please enter your password")
                                                else:
                                                    success, message = reactivate_account(login_email, reactivate_password)
                                                    if success:
                                                        st.success(message)
                                                        # Try to log in immediately after reactivation
                                                        user_id, login_error = login_user(login_email, reactivate_password)
                                                        if user_id:
                                                            st.session_state.user_id = user_id
                                                            st.session_state.authenticated = True
                                                            st.session_state.current_page = "dashboard"
                                                            st.rerun()
                                                        else:
                                                            st.error(f"Failed to log in after reactivation: {login_error}")
                                                    else:
                                                        st.error(message)
                                    else:
                                        st.error(error)
                                else:
                                    st.session_state.user_id = user_id
                                    st.session_state.authenticated = True
                                    st.session_state.current_page = "dashboard"
                                    st.rerun()
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        import traceback
                        st.error(traceback.format_exc())
            
            # Return to landing page button
            if st.button("Back to Home", key="login_back", use_container_width=True):
                st.session_state.current_page = "landing"
                st.rerun()
        
        else:  # signup mode
            # Sign up form
            first_name = st.text_input("First Name", key="signup_first_name")
            last_name = st.text_input("Last Name", key="signup_last_name")
            email = st.text_input("Email", key="signup_email", 
                                help="Enter a valid email address (e.g., user@example.com)")
            password = st.text_input("Password", type="password", key="signup_password",
                                    help="Password must be at least 8 characters with uppercase, lowercase, number, and special character")
            
            # Only show password feedback when there's actually a password entered
            if password:
                is_valid, error_msg = validate_password(password)
                if is_valid:
                    st.success("Strong password! ✓")
                else:
                    st.warning(error_msg)
            
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password",
                                            help="Re-enter your password exactly as above")
            
            if st.button("Create Account", key="signup_submit", type="primary", use_container_width=True):
                try:
                    # Trim whitespace from inputs to handle autofill issues
                    first_name = first_name.strip() if first_name else ""
                    last_name = last_name.strip() if last_name else ""
                    email = email.strip() if email else ""
                    
                    # Check for empty required fields
                    empty_fields = []
                    if not first_name: empty_fields.append("First Name")
                    if not last_name: empty_fields.append("Last Name")
                    if not email: empty_fields.append("Email")
                    if not password: empty_fields.append("Password")
                    if not confirm_password: empty_fields.append("Confirm Password")
                    
                    if empty_fields:
                        st.error(f"Please fill in the following fields: {', '.join(empty_fields)}")
                    elif password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        # Validate email first
                        is_valid_email, email_error = validate_email(email)
                        if not is_valid_email:
                            st.error(email_error)
                        else:
                            # Then validate password
                            is_valid, password_error = validate_password(password)
                            if not is_valid:
                                st.error(password_error)
                            else:
                                user_id, error = register_user(first_name, last_name, email, password)
                                
                                if error:
                                    st.error(error)
                                else:
                                    # Send welcome email
                                    success, email_error = send_welcome_email(email, first_name)
                                    if not success:
                                        st.warning(f"Account created but failed to send welcome email: {email_error}")
                                    
                                    # Log the user in directly after registration
                                    st.session_state.user_id = user_id
                                    st.session_state.authenticated = True
                                    st.session_state.current_page = "dashboard"
                                    st.success("Registration successful! Welcome to ZenFlow.")
                                    st.rerun()
                except Exception as e:
                    st.error(f"An error occurred during signup: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())
            
            # Return to landing page button
            if st.button("Back to Home", key="signup_back", use_container_width=True):
                st.session_state.current_page = "landing"
                st.rerun()
