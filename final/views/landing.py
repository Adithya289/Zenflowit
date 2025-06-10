import streamlit as st
import os
from utils.theme import apply_theme_aware_styles, get_theme_colors
import pathlib
import base64

# Define base path
base_path = pathlib.Path(__file__).parent.parent

def get_image_as_base64(image_path):
    """Convert an image to base64 string"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def show_landing_page():
    """Display the landing page with branding elements, testimonials, and login/signup buttons."""
    # Add top anchor
    st.markdown('<div id="top"></div>', unsafe_allow_html=True)
    
    # Apply theme-aware styling
    is_dark_theme = apply_theme_aware_styles()
    colors = get_theme_colors()
    
    # Navigation buttons row with left and right alignment at the very top
    nav_cols = st.columns([1, 1, 2, 2, 1, 1])
    
    # Left side buttons
    with nav_cols[0]:
        st.markdown("""
        <a href="#about" style="background: linear-gradient(135deg, #4169E1 0%, #8A2BE2 100%); color: white; padding: 0.6rem 1.5rem; border-radius: 0.5rem; text-decoration: none; font-weight: 600; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); transition: transform 0.2s ease; display: block; text-align: center; font-size: 0.9rem;">About Us</a>
        """, unsafe_allow_html=True)
    
    with nav_cols[1]:
        st.markdown("""
        <a href="#contact" style="background: linear-gradient(135deg, #4169E1 0%, #8A2BE2 100%); color: white; padding: 0.6rem 1.5rem; border-radius: 0.5rem; text-decoration: none; font-weight: 600; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); transition: transform 0.2s ease; display: block; text-align: center; font-size: 0.9rem;">Contact</a>
        """, unsafe_allow_html=True)
    
    # Right side buttons
    with nav_cols[4]:
        login_clicked = st.button("Login", key="btn_login", type="primary", use_container_width=True)
        if login_clicked:
            st.session_state.auth_mode = "login"
            st.session_state.current_page = "auth"
            st.rerun()
            
    with nav_cols[5]:
        signup_clicked = st.button("Sign Up", key="btn_signup", type="secondary", use_container_width=True)
        if signup_clicked:
            st.session_state.auth_mode = "signup"
            st.session_state.current_page = "auth"
            st.rerun()
    
    # Get the logo path
    logo_path = str(base_path / "static" / "ZenFlowIt_Logo.png")
    logo_base64 = get_image_as_base64(logo_path)
    
    # Display the logo centered
    st.markdown(f"""
        <div style="display: flex; justify-content: center; margin: 2rem auto 1rem;">
            <img src="data:image/png;base64,{logo_base64}" 
                 style="width: 200px; height: auto;"
                 alt="ZenFlow Logo">
        </div>
    """, unsafe_allow_html=True)
    
    # Main header and tagline
    st.markdown('<h1 class="main-header" style="margin-top: 0;">ZenFlowIt</h1>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">Focus Flow Freedom</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle"><span class="highlight">AI-powered super app</span> to streamline your productivity</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Overcome procrastination, Build unstoppable momentum & Accomplish your goals without stress</p>', unsafe_allow_html=True)
    
    # Custom CSS for landing page styling with theme-specific colors
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,700&display=swap');
    
    /* Set the main background color for the entire app */
    .stApp {{
        background: linear-gradient(135deg, #f0f8ff 0%, #fff0f5 100%) !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", Helvetica, Arial, sans-serif !important;
    }}
    
    /* Ensure all sections have the same background */
    div[data-testid="block-container"] {{
        background: linear-gradient(135deg, #f0f8ff 0%, #fff0f5 100%) !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", Helvetica, Arial, sans-serif !important;
    }}
    
    /* Target the main content area */
    .main .block-container {{
        background: linear-gradient(135deg, #f0f8ff 0%, #fff0f5 100%) !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", Helvetica, Arial, sans-serif !important;
    }}
    
    /* Target individual sections */
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column"] {{
        background: linear-gradient(135deg, #f0f8ff 0%, #fff0f5 100%) !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", Helvetica, Arial, sans-serif !important;
    }}
    
    /* Ensure no white backgrounds override our gradient */
    div[data-testid="stVerticalBlock"] > div[style*="background-color: white"] {{
        background: linear-gradient(135deg, #f0f8ff 0%, #fff0f5 100%) !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", Helvetica, Arial, sans-serif !important;
    }}
    
    .main-header {{
        text-align: center;
        font-size: 3.5rem !important;
        font-weight: 700;
        color: {colors["primary_color"]};
        margin-bottom: 0;
        padding-bottom: 0;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", Helvetica, Arial, sans-serif !important;
    }}
    .tagline {{
        text-align: center;
        font-size: 3.5rem !important;
        font-weight: 700;
        color: {colors["accent_color"]};
        margin-top: 0.5rem;
        margin-bottom: 1.5rem;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", Helvetica, Arial, sans-serif !important;
    }}
    .tagline-sub {{
        text-align: center;
        font-size: 1.8rem !important;
        font-weight: 500;
        color: {colors["accent_color"]};
        margin-top: 0;
        margin-bottom: 1.5rem;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif !important;
    }}
    .subtitle {{
        text-align: center;
        font-size: 1.2rem !important;
        color: {colors["highlight_color"]};
        margin-bottom: 1rem;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif !important;
    }}
    .highlight {{
        background: linear-gradient(120deg, {colors["accent_color"]} 0%, {colors["primary_color"]} 100%);
        padding: 0.2rem 0.5rem;
        border-radius: 0.5rem;
        color: {colors["bg_color"]};
        font-weight: 600;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif !important;
    }}
    .feature-card {{
        background: linear-gradient(135deg, {colors["accent_color"]} 0%, {colors["primary_color"]} 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        transition: transform 0.2s ease;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif !important;
        height: 250px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }}
    .feature-card:hover {{
        transform: translateY(-5px);
    }}
    .feature-title {{
        font-size: 1.3rem !important;
        font-weight: 600;
        margin-bottom: 1rem;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", Helvetica, Arial, sans-serif !important;
    }}
    .feature-text {{
        font-size: 1rem !important;
        line-height: 1.5;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif !important;
    }}
    .testimonial {{
        background: linear-gradient(135deg, #ffe4e1 0%, #ffb6c1 100%);
        color: #2c3e50;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        height: 100%;
        transition: transform 0.2s ease;
        border: 1px solid rgba(255, 255, 255, 0.3);
        display: flex;
        flex-direction: column;
        align-items: center;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif !important;
    }}
    .testimonial:hover {{
        transform: translateY(-5px);
        box-shadow: 0 15px 20px -3px rgba(0, 0, 0, 0.2);
    }}
    .testimonial-image {{
        width: 120px;
        height: 120px;
        border-radius: 50%;
        object-fit: cover;
        margin-bottom: 1.5rem;
        border: 3px solid white;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }}
    .testimonial-text {{
        font-size: 1.2rem !important;
        font-style: italic;
        margin-bottom: 1.5rem;
        color: #2c3e50;
        line-height: 1.8;
        text-align: center;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif !important;
    }}
    .testimonial-author {{
        font-size: 1rem !important;
        font-weight: 600;
        text-align: center;
        color: #c71585;
        padding-top: 0.5rem;
        border-top: 1px solid rgba(199, 21, 133, 0.2);
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", Helvetica, Arial, sans-serif !important;
    }}
    .carousel-nav {{
        width: 40px;
        height: 40px;
        background-color: #3a1f5d;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        cursor: pointer;
        margin: 0 auto;
        text-decoration: none;
        transition: background-color 0.2s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}
    .carousel-nav:hover {{
        background-color: #1a0f3c;
    }}
    
    /* Indicator dots for the testimonial carousel */
    .indicator {{
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin: 0 5px;
        display: inline-block;
        transition: all 0.2s ease;
        border: 2px solid #c71585;
    }}
    .indicator.active {{
        background-color: #c71585;
        transform: scale(1.2);
    }}
    .indicator.inactive {{
        background-color: transparent;
    }}
    /* Fix for the logo to be visible in all themes */
    .logo-container img {{
        background-color: white;
        border-radius: 10px;
        padding: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}
    
    /* Specifically target the logo image container */
    [data-testid="column"] > div:first-child > div > [data-testid="image"] > img {{
        vertical-align: middle;
        margin-bottom: 0 !important;
        margin-top: 0 !important;
        padding: 0 !important;
    }}
    /* Carousel navigation buttons - improved visibility */
    .carousel-button {{
        display: block !important;
        width: 100% !important;
        margin: 0 auto !important;
    }}
    
    /* Target header area with more specific selectors */
    div[data-testid="block-container"] > div > div:first-of-type div[data-testid="column"] {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    
    /* Improve image container alignment */
    [data-testid="column"]:first-child [data-testid="image"] {{
        margin: 0 auto !important;
        padding: 0 !important;
    }}
    
    /* Target image directly */
    [data-testid="image"] > img {{
        vertical-align: middle !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    
    /* Improve button alignment */
    .stButton {{
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    
    /* Fix button height to match image height */
    .stButton > button {{
        height: 38px !important;
    }}
    
    /* Feature box styles */
    .feature-box-container {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 2rem;
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 1rem;
    }}
    
    .feature-box {{
        background: white;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(0, 0, 0, 0.1);
        transition: all 0.4s ease;
        height: 280px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        width: 100%;
    }}
    
    .feature-box:hover {{
        background: linear-gradient(135deg, #FFF5E6 0%, #FFE4E1 100%);
        transform: translateY(-15px);
        box-shadow: 0 20px 30px rgba(0, 0, 0, 0.2);
    }}
    
    .feature-icon {{
        font-size: 2.5rem;
        color: {colors['primary_color']};
        margin-bottom: 1rem;
        text-align: center;
        flex: 0 0 auto;
    }}
    
    .feature-title {{
        color: {colors['primary_color']};
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-align: center;
        flex: 0 0 auto;
    }}
    
    .feature-subtitle {{
        color: {colors['text_color']};
        font-style: italic;
        margin-bottom: 0.5rem;
        text-align: center;
        flex: 0 0 auto;
    }}
    
    .feature-description {{
        color: {colors['text_color']};
        line-height: 1.6;
        text-align: center;
        flex: 1 1 auto;
        display: flex;
        align-items: center;
    }}
    
    @media (max-width: 992px) {{
        .feature-box-container {{
            grid-template-columns: repeat(2, 1fr);
        }}
        .feature-box {{
            height: 300px; /* Slightly taller on medium screens */
        }}
    }}
    
    @media (max-width: 768px) {{
        .feature-box-container {{
            grid-template-columns: 1fr;
        }}
        .feature-box {{
            height: auto; /* Auto height on mobile for better responsiveness */
            min-height: 280px;
        }}
    }}
    
    /* Add hover effect styles */
    div[data-testid="column"] > div > div {{
        transition: all 0.4s ease;
    }}
    
    div[data-testid="column"] > div > div:hover {{
        background: linear-gradient(135deg, #FFF5E6 0%, #FFE4E1 100%) !important;
        transform: translateY(-15px);
        box-shadow: 0 20px 30px rgba(0, 0, 0, 0.2);
    }}
    
    /* Add this to the CSS section */
    .nav-button-container {{
        position: relative;
        width: 100%;
        height: 100%;
    }}
    .nav-button-container button {{
        opacity: 0 !important;
        width: 100% !important;
        height: 100% !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        z-index: 2 !important;
        cursor: pointer !important;
    }}
    .nav-icon {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 1;
        pointer-events: none;
    }}
    </style>

    <!-- Add Confetti.js -->
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    
    <!-- JavaScript for Learn More button -->
    <script>
        // Function to trigger confetti
        function triggerConfetti() {{
            confetti({{
                particleCount: 100,
                spread: 70,
                origin: {{ y: 0.6 }},
                colors: ['#FF69B4', '#FFB6C1', '#FFC0CB']
            }});
        }}

        // Function to scroll to features
        function scrollToFeatures() {{
            // First trigger confetti
            triggerConfetti();
            
            // Then scroll to features section
            const featuresSection = document.getElementById('zenflow-features');
            if (featuresSection) {{
                featuresSection.scrollIntoView({{
                    behavior: 'smooth',
                    block: 'start'
                }});
            }}
        }}

        // Add event listener when the page loads
        document.addEventListener('DOMContentLoaded', function() {{
            const learnMoreBtn = document.querySelector('button[onclick="scrollToFeatures()"]');
            if (learnMoreBtn) {{
                learnMoreBtn.addEventListener('click', function(e) {{
                    e.preventDefault();
                    scrollToFeatures();
                }});
            }}
        }});
    </script>
    """, unsafe_allow_html=True)
    
    # Feature cards with icons
    st.markdown(f'<p class="subtitle" style="font-size: 1.5rem !important; font-weight: 600; color: {colors["primary_color"]}; margin-top: 2rem;">Unlock your potential with ZenFlowIt - a beautifully designed workspace for optimal focus</p>', unsafe_allow_html=True)
    
    feat_col1, feat_col2, feat_col3 = st.columns(3)
    
    with feat_col1:
        st.markdown(f"""
        <div class="feature-card">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🎯</div>
            <div class="feature-title" style="color: white;">Smart Task Breakdown</div>
            <div class="feature-text">Our AI automatically breaks down complex tasks into manageable subtasks, helping you stay organized and focused</div>
        </div>
        """, unsafe_allow_html=True)
    
    with feat_col2:
        st.markdown(f"""
        <div class="feature-card">
            <div style="font-size: 2rem; margin-bottom: 1rem;">⏰</div>
            <div class="feature-title" style="color: white;">Intelligent Scheduling</div>
            <div class="feature-text">Optimize your day with AI-powered scheduling that works with your natural energy flow and preferences</div>
        </div>
        """, unsafe_allow_html=True)
    
    with feat_col3:
        st.markdown(f"""
        <div class="feature-card">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🧘</div>
            <div class="feature-title" style="color: white;">Focus Enhancers</div>
            <div class="feature-text">Powerful tools to eliminate distractions and keep you in deep focus states for maximum productivity</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Call to Action Section
    st.markdown(f"""
    <div style="text-align: center; margin: 3rem 0; padding: 2rem; background: linear-gradient(135deg, #E6E6FA 0%, #B0C4DE 100%); border-radius: 1rem;">
        <h2 style="color: #4169E1; margin-bottom: 1rem;">Ready to Transform Your Productivity?</h2>
        <p style="color: #4169E1; font-size: 1.2rem; margin-bottom: 1.5rem;">Join to discover the power of ZenFlowIt</p>
        <div style="display: flex; justify-content: center; gap: 1rem; margin-top: 1rem;">
            <a href="#zenflow-features" style="background-color: white; color: #4169E1; border: 2px solid #4169E1; outline: none; padding: 0.8rem 2rem; border-radius: 0.5rem; font-weight: 600; cursor: pointer; text-decoration: none; display: inline-block; min-width: 150px; transition: all 0.3s ease; box-shadow: 0 2px 4px rgba(65, 105, 225, 0.1); text-align: center; position: relative; overflow: hidden;">
                <span style="position: relative; z-index: 1;">Learn More</span>
                <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; border: 2px solid #4169E1; border-radius: 0.5rem; pointer-events: none;"></div>
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Add some spacing before the features section
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Is Procrastination Holding you back? Section
    st.markdown(f"""
    <div style="text-align: center; margin: 3rem 0; padding: 2rem; background: linear-gradient(135deg, #B22222 0%, #8A2BE2 100%); border-radius: 1rem;">
        <h2 style="color: white; margin-bottom: 1rem;">Is Procrastination Holding you back?</h2>
        <p style="color: white; font-size: 1.2rem; margin-bottom: 1.5rem;">Hey, no worries! ZenFlowIt is packed with tools to help you thrive. Go ahead, Sign Up!</p>
    </div>
    """, unsafe_allow_html=True)

    # Create three columns for the procrastination impact boxes
    proc_col1, proc_col2, proc_col3 = st.columns(3)
    
    with proc_col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #B22222 0%, #8A2BE2 100%); padding: 2rem; border-radius: 50px; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1); border: 1px solid rgba(0, 0, 0, 0.1); margin: 1rem; transition: all 0.3s ease; height: 400px; display: flex; flex-direction: column; align-items: center;">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <img src="data:image/png;base64,{get_image_as_base64(str(base_path / "attached_assets/missed_deadlines.png"))}" style="width: 120px; height: 120px; object-fit: contain;">
            </div>
            <h3 style="color: #FFE4E1; font-size: 1.8rem; font-weight: 700; text-align: center; margin-bottom: 1rem;">Missed Deadlines</h3>
            <p style="color: #FFE4E1; line-height: 1.6; text-align: center; font-size: 1.4rem;">Are you constantly struggling to meet deadlines and feeling overwhelmed by unfinished tasks?</p>
        </div>
        """, unsafe_allow_html=True)
    
    with proc_col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #B22222 0%, #8A2BE2 100%); padding: 2rem; border-radius: 50px; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1); border: 1px solid rgba(0, 0, 0, 0.1); margin: 1rem; transition: all 0.3s ease; height: 400px; display: flex; flex-direction: column; align-items: center;">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <img src="data:image/png;base64,{get_image_as_base64(str(base_path / "attached_assets/missed_opportunity.png"))}" style="width: 120px; height: 120px; object-fit: contain;">
            </div>
            <h3 style="color: #FFE4E1; font-size: 1.8rem; font-weight: 700; text-align: center; margin-bottom: 1rem;">Lost Opportunities</h3>
            <p style="color: #FFE4E1; line-height: 1.6; text-align: center; font-size: 1.4rem;">Is Procrastination leads to missed opportunities and hinders professional growth?</p>
        </div>
        """, unsafe_allow_html=True)
    
    with proc_col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #B22222 0%, #8A2BE2 100%); padding: 2rem; border-radius: 50px; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1); border: 1px solid rgba(0, 0, 0, 0.1); margin: 1rem; transition: all 0.3s ease; height: 400px; display: flex; flex-direction: column; align-items: center;">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <img src="data:image/png;base64,{get_image_as_base64(str(base_path / "attached_assets/increased_stress.png"))}" style="width: 120px; height: 120px; object-fit: contain;">
            </div>
            <h3 style="color: #FFE4E1; font-size: 1.8rem; font-weight: 700; text-align: center; margin-bottom: 1rem;">Increased Stress</h3>
            <p style="color: #FFE4E1; line-height: 1.6; text-align: center; font-size: 1.4rem;">Does the constant pressure of delaying tasks significantly increases the stress and anxiety levels?</p>
        </div>
        """, unsafe_allow_html=True)

    # ZenFlow Features Section with ID
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    """, unsafe_allow_html=True)

    # Create a container for the features section with ID
    features_container = st.container()
    
    # Add the section title with ID and scroll margin
    features_container.markdown(f"""
        <div id="zenflow-features" style="margin-top: 2rem; padding-top: 2rem; scroll-margin-top: 2rem;">
            <h2 style="text-align: center; color: {colors['primary_color']}; margin-bottom: 3rem; font-size: 2.5rem;">ZenFlowIt makes your life easier with...</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Create columns for feature boxes in four rows
    row1_col1, row1_col2, row1_col3 = features_container.columns(3)
    
    # First row - Images
    with row1_col1:
        st.markdown(f"""
            <div style="margin: 1rem;">
                <img src="data:image/svg+xml;base64,{get_image_as_base64(str(base_path / "attached_assets/undraw_calendar_8r6s.svg"))}" style="width: 100%; max-width: 350px; height: auto; margin: 0 auto; display: block;">
            </div>
        """, unsafe_allow_html=True)
    
    with row1_col2:
        st.markdown(f"""
            <div class="feature-box" style="width: 100%; background: white; padding: 2rem; border-radius: 1rem; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1); border: 1px solid rgba(0, 0, 0, 0.1); margin: 1rem;">
                <div style="font-size: 2.5rem; color: {colors['primary_color']}; text-align: center; margin-bottom: 1rem;">
                    <i class="fas fa-robot"></i>
                </div>
                <h3 style="color: {colors['primary_color']}; font-size: 1.5rem; font-weight: 700; text-align: center; margin-bottom: 1rem;">AI-Powered Assistant</h3>
                <p style="color: {colors['text_color']}; line-height: 1.6; text-align: center; font-size: 1.2rem;">Get personalized productivity help with an AI assistant.</p>
            </div>
        """, unsafe_allow_html=True)
    
    with row1_col3:
        st.markdown(f"""
            <div style="margin: 1rem;">
                <img src="data:image/png;base64,{get_image_as_base64(str(base_path / "attached_assets/undraw_tracker_man.png"))}" style="width: 100%; max-width: 350px; height: auto; margin: 0 auto; display: block;">
            </div>
        """, unsafe_allow_html=True)

    # Second row
    row2_col1, row2_col2, row2_col3 = features_container.columns(3)
    
    with row2_col1:
        st.markdown(f"""
            <div class="feature-box" style="width: 100%; background: white; padding: 2rem; border-radius: 1rem; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1); border: 1px solid rgba(0, 0, 0, 0.1); margin: 1rem;">
                <div style="font-size: 2.5rem; color: {colors['primary_color']}; text-align: center; margin-bottom: 1rem;">
                    <i class="fas fa-list-check"></i>
                </div>
                <h3 style="color: {colors['primary_color']}; font-size: 1.5rem; font-weight: 700; text-align: center; margin-bottom: 1rem;">Easy Task Breakdown</h3>
                <p style="color: {colors['text_color']}; line-height: 1.6; text-align: center; font-size: 1.2rem;">Break down tasks to create, organize, and prioritize easily.</p>
            </div>
        """, unsafe_allow_html=True)
    
    with row2_col2:
        st.markdown(f"""
            <div style="margin: 1rem;">
                <img src="data:image/png;base64,{get_image_as_base64(str(base_path / "attached_assets/undraw_man.png"))}" style="width: 100%; max-width: 350px; height: auto; margin: 0 auto; display: block;">
            </div>
        """, unsafe_allow_html=True)
    
    with row2_col3:
        st.markdown(f"""
            <div class="feature-box" style="width: 100%; background: white; padding: 2rem; border-radius: 1rem; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1); border: 1px solid rgba(0, 0, 0, 0.1); margin: 1rem;">
                <div style="font-size: 2.5rem; color: {colors['primary_color']}; text-align: center; margin-bottom: 1rem;">
                    <i class="fas fa-chart-line"></i>
                </div>
                <h3 style="color: {colors['primary_color']}; font-size: 1.5rem; font-weight: 700; text-align: center; margin-bottom: 1rem;">Progress Tracking</h3>
                <p style="color: {colors['text_color']}; line-height: 1.6; text-align: center; font-size: 1.2rem;">Track your goals and celebrate every win on the way.</p>
            </div>
        """, unsafe_allow_html=True)

    # Third row
    row3_col1, row3_col2, row3_col3 = features_container.columns(3)
    
    with row3_col1:
        st.markdown(f"""
            <div class="feature-box" style="width: 100%; background: white; padding: 2rem; border-radius: 1rem; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1); border: 1px solid rgba(0, 0, 0, 0.1); margin: 1rem;">
                <div style="font-size: 2.5rem; color: {colors['primary_color']}; text-align: center; margin-bottom: 1rem;">
                    <i class="fas fa-stopwatch"></i>
                </div>
                <h3 style="color: {colors['primary_color']}; font-size: 1.5rem; font-weight: 700; text-align: center; margin-bottom: 1rem;">Focus Sprints</h3>
                <p style="color: {colors['text_color']}; line-height: 1.6; text-align: center; font-size: 1.2rem;">Stay committed and focused using timed task sessions.</p>
            </div>
        """, unsafe_allow_html=True)
    
    with row3_col2:
        st.markdown(f"""
            <div style="margin: 1rem;">
                <img src="data:image/png;base64,{get_image_as_base64(str(base_path / "attached_assets/undraw-task_focused.png"))}" style="width: 100%; max-width: 350px; height: auto; margin: 0 auto; display: block;">
            </div>
        """, unsafe_allow_html=True)
    
    with row3_col3:
        st.markdown(f"""
            <div class="feature-box" style="width: 100%; background: white; padding: 2rem; border-radius: 1rem; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1); border: 1px solid rgba(0, 0, 0, 0.1); margin: 1rem;">
                <div style="font-size: 2.5rem; color: {colors['primary_color']}; text-align: center; margin-bottom: 1rem;">
                    <i class="fas fa-medal"></i>
                </div>
                <h3 style="color: {colors['primary_color']}; font-size: 1.5rem; font-weight: 700; text-align: center; margin-bottom: 1rem;">Earn Rewards</h3>
                <p style="color: {colors['text_color']}; line-height: 1.6; text-align: center; font-size: 1.2rem;">Stick to routines and earn badges after task accomplishments.</p>
            </div>
        """, unsafe_allow_html=True)

    # Fourth row
    row4_col1, row4_col2, row4_col3 = features_container.columns(3)
    
    with row4_col1:
        st.markdown(f"""
            <div style="margin: 1rem; background: transparent;">
                <img src="data:image/png;base64,{get_image_as_base64(str(base_path / "attached_assets/undraw_task_plan.png"))}" style="width: 100%; max-width: 350px; height: auto; margin: 0 auto; display: block; background: transparent;">
            </div>
        """, unsafe_allow_html=True)
    
    with row4_col2:
        st.markdown(f"""
            <div class="feature-box" style="width: 100%; background: white; padding: 2rem; border-radius: 1rem; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1); border: 1px solid rgba(0, 0, 0, 0.1); margin: 1rem;">
                <div style="font-size: 2.5rem; color: {colors['primary_color']}; text-align: center; margin-bottom: 1rem;">
                    <i class="fas fa-images"></i>
                </div>
                <h3 style="color: {colors['primary_color']}; font-size: 1.5rem; font-weight: 700; text-align: center; margin-bottom: 1rem;">Create Vision Board</h3>
                <p style="color: {colors['text_color']}; line-height: 1.6; text-align: center; font-size: 1.2rem;">Frame your achievements and visualize them through vision board tiles.</p>
            </div>
        """, unsafe_allow_html=True)
    
    with row4_col3:
        st.markdown(f"""
            <div style="margin: 1rem;">
                <img src="data:image/png;base64,{get_image_as_base64(str(base_path / "attached_assets/rewards.png"))}" style="width: 100%; max-width: 350px; height: auto; margin: 0 auto; display: block;">
            </div>
        """, unsafe_allow_html=True)

    # Add Start Free Trial button after features -(changed to Join Us)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f'<p style="text-align: center; color: {colors["primary_color"]}; font-weight: bold; font-size: 1.2rem; margin-bottom: 1.5rem;">Break free from procrastination and unlock your full potential with ZenFlowIt</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        start_trial_clicked = st.button("Join Us", key="btn_start_trial", type="primary", use_container_width=True)
        if start_trial_clicked:
            st.session_state.auth_mode = "signup"
            st.session_state.current_page = "auth"
            st.rerun()

    # About Us Section
    st.markdown(f"""
    <div id="about" style="margin: 4rem 0;">
        <h2 style="text-align: center; color: {colors['primary_color']}; margin-bottom: 2rem; font-size: 2.5rem;">About Us</h2>
        <div style="max-width: 800px; margin: 0 auto; color: #4169E1; text-align: left;">
            <p style="font-size: 1.8rem; line-height: 1.6; margin-bottom: 1.5rem; font-weight: 600;">
                A simple app with a meaningful mission — built by people just like you
            </p>
            <p style="line-height: 1.8; margin-bottom: 1.5rem; font-size: 1.2rem;">
                We're a team of <span style="font-weight: 700;">five passionate individuals</span> with backgrounds in 
                <span style="font-weight: 700;">data science</span>, combining the strengths of 
                <span style="font-weight: 700;">working professionals</span> and 
                <span style="font-weight: 700;">current Master's students</span>. Together, we bring a unique blend of 
                industry experience, academic insight, and a shared curiosity for building meaningful, impactful solutions.
            </p>
            <p style="line-height: 1.8; margin-bottom: 1.5rem; font-size: 1.2rem;">
                Across different stages of our lives — from intense university deadlines to high-pressure work environments — we've all faced the 
                mental block that is <span style="font-weight: 700;">procrastination</span>. We've seen firsthand how it 
                quietly drains time, delays goals, and chips away at motivation.
            </p>
            <p style="line-height: 1.8; margin-bottom: 1.5rem; font-size: 1.2rem;">
                That's why we built <span style="font-weight: 700;">ZenFlowIt</span> to help people overcome procrastination 
                and make the most of their time through <span style="font-weight: 700;">calm, clarity, and intention</span>.
            </p>
            <p style="line-height: 1.8; margin-bottom: 1.5rem; font-size: 1.2rem;">
                With lived experience and a data-driven mindset, <span style="font-weight: 700;">our mission</span> is 
                simple — <span style="font-weight: 700;">To support students, professionals, and everyday go-getters in building focus, creating momentum, and achieving fulfillment</span> — 
                <span style="font-weight: 700;">one small, manageable step at a time</span>.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Team Members Section
    st.markdown(f"""
    <div style="margin: 2rem 0;">
        <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 2rem; max-width: 1200px; margin: 0 auto; padding: 0 1rem;">
            <div style="text-align: center; display: flex; flex-direction: column; align-items: center; height: 100%;">
                <img src="data:image/jpeg;base64,{get_image_as_base64(str(base_path / "static/images/team/Aiswarya_Raghavadesikan.jpeg"))}" 
                    style="width: 200px; height: 200px; border-radius: 50%; object-fit: cover; margin-bottom: 1rem; border: 3px solid #4169E1; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                <h3 style="color: #4169E1; margin-bottom: 0.5rem; font-size: 1.5rem;">Aiswarya<br>Raghavadesikan</h3>
                <p style="color: #666; font-size: 0.9rem; line-height: 1.4; margin-bottom: 1rem;">MS Applied Data Science<br>San Jose State University</p>
                <a href="https://www.linkedin.com/in/aiswarya-raghavadesikan/" target="_blank" 
                    style="display: inline-flex; align-items: center; padding: 0.5rem 1.2rem; background: #4169E1; color: white; 
                    border-radius: 2rem; text-decoration: none; transition: all 0.3s ease; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: auto;">
                    <i class="fab fa-linkedin" style="margin-right: 0.5rem;"></i>LinkedIn
                </a>
            </div>
            <div style="text-align: center; display: flex; flex-direction: column; align-items: center; height: 100%;">
                <img src="data:image/jpeg;base64,{get_image_as_base64(str(base_path / "static/images/team/Siddharth_Bookinkere.jpeg"))}" 
                    style="width: 200px; height: 200px; border-radius: 50%; object-fit: cover; margin-bottom: 1rem; border: 3px solid #4169E1; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                <h3 style="color: #4169E1; margin-bottom: 0.5rem; font-size: 1.5rem;">Siddharth<br>Bookinkere</h3>
                <p style="color: #666; font-size: 0.9rem; line-height: 1.4; margin-bottom: 1rem;">Business Analyst<br>MS Business Analytics<br>Boston University</p>
                <a href="https://www.linkedin.com/in/siddharth-bookinkere/" target="_blank" 
                    style="display: inline-flex; align-items: center; padding: 0.5rem 1.2rem; background: #4169E1; color: white; 
                    border-radius: 2rem; text-decoration: none; transition: all 0.3s ease; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: auto;">
                    <i class="fab fa-linkedin" style="margin-right: 0.5rem;"></i>LinkedIn
                </a>
            </div>
            <div style="text-align: center; display: flex; flex-direction: column; align-items: center; height: 100%;">
                <img src="data:image/jpeg;base64,{get_image_as_base64(str(base_path / "static/images/team/Prathyusha_Pateel.jpg"))}" 
                    style="width: 200px; height: 200px; border-radius: 50%; object-fit: cover; margin-bottom: 1rem; border: 3px solid #4169E1; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                <h3 style="color: #4169E1; margin-bottom: 0.5rem; font-size: 1.5rem;">Prathyusha<br>Pateel</h3>
                <p style="color: #666; font-size: 0.9rem; line-height: 1.4; margin-bottom: 1rem;">Data Scientist<br>MS Analytics<br>Georgia Tech</p>
                <a href="https://www.linkedin.com/in/prathyusha-pateel/" target="_blank" 
                    style="display: inline-flex; align-items: center; padding: 0.5rem 1.2rem; background: #4169E1; color: white; 
                    border-radius: 2rem; text-decoration: none; transition: all 0.3s ease; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: auto;">
                    <i class="fab fa-linkedin" style="margin-right: 0.5rem;"></i>LinkedIn
                </a>
            </div>
            <div style="text-align: center; display: flex; flex-direction: column; align-items: center; height: 100%;">
                <img src="data:image/jpeg;base64,{get_image_as_base64(str(base_path / "static/images/team/Seyed_Shahab_Ashrafzadeh.jpeg"))}" 
                    style="width: 200px; height: 200px; border-radius: 50%; object-fit: cover; margin-bottom: 1rem; border: 3px solid #4169E1; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                <h3 style="color: #4169E1; margin-bottom: 0.5rem; font-size: 1.5rem;">Seyed Shahab<br>Ashrafzadeh</h3>
                <p style="color: #666; font-size: 0.9rem; line-height: 1.4; margin-bottom: 1rem;">MS DS University of Leeds<br>Data Scientist, Central Bank</p>
                <a href="https://www.linkedin.com/in/shahab63/" target="_blank" 
                    style="display: inline-flex; align-items: center; padding: 0.5rem 1.2rem; background: #4169E1; color: white; 
                    border-radius: 2rem; text-decoration: none; transition: all 0.3s ease; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: auto;">
                    <i class="fab fa-linkedin" style="margin-right: 0.5rem;"></i>LinkedIn
                </a>
            </div>
            <div style="text-align: center; display: flex; flex-direction: column; align-items: center; height: 100%;">
                <img src="data:image/jpeg;base64,{get_image_as_base64(str(base_path / "static/images/team/Adithyan_Manoharan.jpeg"))}" 
                    style="width: 200px; height: 200px; border-radius: 50%; object-fit: cover; margin-bottom: 1rem; border: 3px solid #4169E1; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                <h3 style="color: #4169E1; margin-bottom: 0.5rem; font-size: 1.5rem;">Adithyan<br>Manoharan</h3>
                <p style="color: #666; font-size: 0.9rem; line-height: 1.4; margin-bottom: 1rem;">MBA in Data Analytics &<br>Supply Chain Management<br>Northern Kentucky University</p>
                <a href="https://www.linkedin.com/in/adithyan-manoharan" target="_blank" 
                    style="display: inline-flex; align-items: center; padding: 0.5rem 1.2rem; background: #4169E1; color: white; 
                    border-radius: 2rem; text-decoration: none; transition: all 0.3s ease; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: auto;">
                    <i class="fab fa-linkedin" style="margin-right: 0.5rem;"></i>LinkedIn
                </a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Testimonials heading
    st.markdown(f'<h2 style="text-align: center; color: {colors["primary_color"]}; margin-bottom: 20px;">Yah! Amazing People sharing their expectations from our product</h2>', unsafe_allow_html=True)
    
    # Define testimonials with image paths
    testimonials = [
        {
            "text": "Finally, an AI app that actually gets my procrastination habits! It feels like having a personal coach who doesn't judge — just helps.",
            "author": "Graduate Student",
            "image": "1_n_graduate.png"
        },
        {
            "text": "If this can stop my doom-scrolling and keep me in flow — I'm sold. This tool might just be the productivity breakthrough I've needed.",
            "author": "Freelance Designer",
            "image": "2_n_freelancerdesigner.png"
        },
        {
            "text": "This app is the productivity buddy I never knew I needed. I usually end the day frustrated, but this could turn things around!",
            "author": "Working Professional",
            "image": "3_n_workingprofessional.png"
        },
        {
            "text": "Reels and Instagram eat my hours. If your tool can nudge me just enough to stay mindful and focused — count me in!",
            "author": "Master's Student",
            "image": "4_n_graduatestudent.png"
        },
        {
            "text": "I love how this app feels supportive instead of pushy. A gentle nudge, smart feedback — finally, tech that actually helps!",
            "author": "UX Research Intern",
            "image": "5_n_uxreseachintern.png"
        },
        {
            "text": "This is a game changer! I lose focus halfway through the day, and your app sounds like the perfect balance of accountability and motivation.",
            "author": "Recent Graduate (Job Seeker)",
            "image": "6_n_recentgraduate.png"
        }
    ]
    
    # Initialize testimonial index in session state
    if "testimonial_index" not in st.session_state:
        st.session_state.testimonial_index = 0
    
    # Create testimonial carousel
    t_col1, t_col2, t_col3 = st.columns([1, 6, 1])
    
    # Previous testimonial button
    with t_col1:
        prev_clicked = st.button("Previous", key="prev_testimonial", type="primary", use_container_width=True)
        if prev_clicked:
            st.session_state.testimonial_index = (st.session_state.testimonial_index - 1) % len(testimonials)
            st.rerun()
            
    # Current testimonial
    with t_col2:
        current = testimonials[st.session_state.testimonial_index]
        image_style = ""
        # Add specific styling for 3rd and 4th testimonial images
        if current["image"] in ["3_n_workingprofessional.png", "4_n_graduatestudent.png"]:
            image_style = "object-position: center 20%;"
        
        st.markdown(f"""
        <div class="testimonial">
            <img src="data:image/png;base64,{get_image_as_base64(str(base_path / "attached_assets" / current["image"]))}" 
                class="testimonial-image" 
                style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; margin-bottom: 1.5rem; border: 3px solid white; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); {image_style}">
            <div class="testimonial-text">"{current["text"]}"</div>
            <div class="testimonial-author">— {current["author"]}</div>
        </div>
        """, unsafe_allow_html=True)
        
    # Next testimonial button
    with t_col3:
        next_clicked = st.button("Next", key="next_testimonial", type="primary", use_container_width=True)
        if next_clicked:
            st.session_state.testimonial_index = (st.session_state.testimonial_index + 1) % len(testimonials)
            st.rerun()
    
    # Display the indicators (dots)
    indicators = '<div style="display: flex; justify-content: center; margin-top: 1rem;">'
    for i in range(len(testimonials)):
        if i == st.session_state.testimonial_index:
            indicators += f'<div class="indicator active"></div>'
        else:
            indicators += f'<div class="indicator inactive"></div>'
    indicators += '</div>'
    
    st.markdown(indicators, unsafe_allow_html=True)

    # Contact Section
    st.markdown(f"""
    <div id="contact" style="margin: 4rem 0; background: rgba(46, 64, 83, 0.05); padding: 3rem; border-radius: 1rem;">
        <h2 style="text-align: center; color: {colors['primary_color']}; margin-bottom: 2rem; font-size: 2.5rem;">Contact</h2>
        <div style="max-width: 800px; margin: 0 auto; padding: 0 1rem; text-align: center; color: #4169E1;">
            <p style="line-height: 1.8; margin-bottom: 1.5rem; font-size: 1.2rem;">
                We'd love to hear from you! Whether you have questions, feedback, or just want to share your productivity journey, we're here to listen and help.
            </p>
            <div style="background: white; padding: 2rem; border-radius: 1rem; margin: 2rem 0; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                <p style="line-height: 1.8; margin-bottom: 1rem; font-size: 1.4rem; font-weight: 600; color: #4169E1;">
                    📧 Get in Touch
                </p>
                <p style="line-height: 1.8; margin-bottom: 1rem; font-size: 1.2rem;">
                    Email us at: <a href="mailto:zenflowitapp@gmail.com" style="color: #4169E1; text-decoration: none; font-weight: 600;">zenflowitapp@gmail.com</a>
                </p>
                <p style="line-height: 1.8; font-size: 1.1rem; color: #666;">
                    We aim to respond within 24 hours during business days.
                </p>
            </div>
            <p style="line-height: 1.8; margin-bottom: 2rem; font-size: 1.2rem; font-weight: 600;">
                Help us make ZenFlowIt even better — take our quick survey!
            </p>
            <div style="display: flex; justify-content: center; gap: 1rem; margin-top: 2rem;">
                <a href="#top" style="background-color: {colors['primary_color']}; color: white; border: none; padding: 0.8rem 2rem; border-radius: 0.5rem; font-weight: 600; cursor: pointer; text-decoration: none; display: inline-block; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); scroll-behavior: smooth;">Jump to Top</a>
                <a href="https://docs.google.com/forms/d/e/1FAIpQLSdo2j3oSnZXTLrjbALQXrX9jGXmqZ7sWhnkuz6_ormCKfypSQ/viewform" target="_blank" style="background-color: {colors['primary_color']}; color: white; border: none; padding: 0.8rem 2rem; border-radius: 0.5rem; font-weight: 600; cursor: pointer; text-decoration: none; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">Submit the Survey</a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)