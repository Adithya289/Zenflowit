import os
import pathlib
import re

def validate_app_password(password):
    """Validate the Gmail App Password format"""
    # Remove any extra spaces at start/end
    password = password.strip()
    
    # Check if it matches the pattern: 4 chars + space + 4 chars + space + 4 chars + space + 4 chars
    pattern = r'^[a-z]{4}\s[a-z]{4}\s[a-z]{4}\s[a-z]{4}$'
    if not re.match(pattern, password):
        return False, """Invalid password format. The Gmail App Password should:
- Be 16 characters long
- Have spaces between each group of 4 characters
- Look like this: 'xxxx xxxx xxxx xxxx'
- Contain only lowercase letters
Example format: 'usfi zwxk jvar yqzu'"""
    return True, None

def verify_and_fix_env():
    """Verify and fix the .env file"""
    # Get the root directory
    root_dir = pathlib.Path(__file__).parent.parent
    env_path = os.path.join(root_dir, '.env')
    
    print(f"Checking .env file at: {env_path}")
    
    # Check if .env exists
    if not os.path.exists(env_path):
        print(".env file not found. Creating new one...")
        create_new = True
    else:
        print(".env file found. Checking content...")
        create_new = False
        
        # Read current content
        with open(env_path, 'r') as f:
            content = f.read()
            print("\nCurrent .env content:")
            # Hide password in output
            display_content = content
            if 'EMAIL_PASSWORD=' in content:
                password_line = [line for line in content.split('\n') if 'EMAIL_PASSWORD=' in line][0]
                password = password_line.split('=')[1]
                display_content = content.replace(password, '[PASSWORD]')
            print(display_content)
            
            # Validate existing password format
            if 'EMAIL_PASSWORD=' in content:
                password = [line.split('=')[1].strip() for line in content.split('\n') if 'EMAIL_PASSWORD=' in line][0]
                is_valid, error_msg = validate_app_password(password)
                if not is_valid:
                    print("\nWarning: Current password format is invalid!")
                    print(error_msg)
                    create_new = True
    
    if create_new or input("\nWould you like to update the .env file? (y/n): ").lower() == 'y':
        # Get email settings
        email_id = input("\nEnter the email ID (press Enter to use zenflowitapp@gmail.com): ").strip()
        if not email_id:
            email_id = "zenflowitapp@gmail.com"
        
        print("\nEnter the 16-character Gmail App Password.")
        print("Format: 'xxxx xxxx xxxx xxxx' (4 groups of 4 characters with spaces)")
        print("Example: 'usfi zwxk jvar yqzu'")
        email_password = input("Password: ").strip()
        
        # Validate input
        if not email_password:
            print("Error: Password cannot be empty")
            return
        
        # Validate password format
        is_valid, error_msg = validate_app_password(email_password)
        if not is_valid:
            print("\nError: Invalid password format")
            print(error_msg)
            return
        
        # Remove any quotes but keep the spaces
        email_id = email_id.strip("'").strip('"')
        email_password = email_password.strip("'").strip('"')
        
        # Create content
        content = f"""EMAIL_ID={email_id}
EMAIL_PASSWORD={email_password}"""
        
        # Write to file
        with open(env_path, 'w') as f:
            f.write(content)
        
        print("\n.env file has been updated successfully!")
        print(f"Location: {env_path}")
        print("\nContent (password hidden):")
        print(f"EMAIL_ID={email_id}")
        print("EMAIL_PASSWORD=[PASSWORD]")
    
    # Verify the file was created and is readable
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r') as f:
                content = f.read()
                if 'EMAIL_ID=' in content and 'EMAIL_PASSWORD=' in content:
                    # Validate password format again
                    password = [line.split('=')[1].strip() for line in content.split('\n') if 'EMAIL_PASSWORD=' in line][0]
                    is_valid, error_msg = validate_app_password(password)
                    if is_valid:
                        print("\nVerification: .env file is properly formatted and contains required variables.")
                        print("Password format is correct.")
                    else:
                        print("\nWarning: Password format is invalid!")
                        print(error_msg)
                else:
                    print("\nWarning: .env file may be missing required variables.")
        except Exception as e:
            print(f"\nError reading .env file: {str(e)}")
    else:
        print("\nError: .env file was not created successfully.")

if __name__ == "__main__":
    verify_and_fix_env() 