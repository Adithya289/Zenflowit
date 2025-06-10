"""
Restart Streamlit app and clear cache.
Run this script when you encounter cache or duplicate element issues.
"""
import os
import time
import signal
import subprocess
import shutil
import platform

def restart_streamlit():
    """Restart the Streamlit app and clear cache directories"""
    print("✅ Cleaning up Streamlit cache...")
    
    # Get the user's home directory
    home_dir = os.path.expanduser("~")
    
    # Clean the streamlit cache directory
    if platform.system() == "Darwin":  # macOS
        cache_dir = os.path.join(home_dir, ".streamlit/cache")
    elif platform.system() == "Windows":
        cache_dir = os.path.join(home_dir, ".streamlit\\cache")
    else:  # Linux and others
        cache_dir = os.path.join(home_dir, ".streamlit/cache")
    
    if os.path.exists(cache_dir):
        try:
            shutil.rmtree(cache_dir)
            print(f"✅ Removed cache directory: {cache_dir}")
        except Exception as e:
            print(f"❌ Error removing cache directory: {str(e)}")
    else:
        print("✅ No cache directory found.")
    
    # Try to kill any running Streamlit processes
    print("🔄 Stopping any running Streamlit instances...")
    try:
        if platform.system() == "Windows":
            os.system("taskkill /f /im streamlit.exe")
        else:
            # Find streamlit processes and kill them
            ps = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE)
            output = ps.communicate()[0].decode('utf-8')
            for line in output.split('\n'):
                if 'streamlit run' in line:
                    pid = int(line.split()[1])
                    try:
                        os.kill(pid, signal.SIGTERM)
                        print(f"✅ Killed Streamlit process: {pid}")
                    except Exception as e:
                        print(f"❌ Error killing process {pid}: {str(e)}")
    except Exception as e:
        print(f"❌ Error stopping Streamlit: {str(e)}")
    
    # Wait a moment for processes to terminate
    time.sleep(2)
    
    # Start Streamlit app in a new process
    print("🚀 Starting Streamlit app...")
    try:
        subprocess.Popen(["streamlit", "run", "app.py"], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
        print("✅ Streamlit app started successfully!")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {str(e)}")
        print("Please run 'streamlit run app.py' manually.")

if __name__ == "__main__":
    restart_streamlit() 