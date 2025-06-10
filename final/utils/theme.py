import streamlit as st

def get_theme_colors():
    """
    Returns the current theme's color palette.
    This function can be used to access theme colors in other parts of the app.
    """
    # Get the theme from session state or detect from Streamlit's options
    if 'theme' in st.session_state:
        # Use the user-selected theme from session state
        is_dark_theme = st.session_state.theme == 'dark'
    else:
        # Fallback to auto-detection
        try:
            base_theme = st.get_option("theme.base")
            is_dark_theme = base_theme == "dark"
        except:
            # Fallback to session state if Streamlit options aren't available
            is_dark_theme = st.session_state.get('theme', 'light') == 'dark'
    
    # Base palette colors
    primary_color = "#549aff"        # Logo blue
    accent_color = "#6f7bf7"         # Soft indigo
    light_accent = "#d6e4ff"         # Pale blue
    medium_accent = "#a8c9ff"        # Sky blue
    very_light_accent = "#f0f6ff"    # Near-white blue
    
    # Define color palette based on theme
    if is_dark_theme:
        # Dark theme colors
        bg_color = "#010104"           # Deep dark
        card_bg_color = "#0e1525"      # Darker slate blue - almost black for highest contrast with white text
        text_color = "#ffffff"         # Bright white
        light_text = "#e0e0e0"         # Soft white
        
        # Dark theme specific colors
        primary_color = "#0048ad"              # Deep variant of logo blue
        accent_color = "#5a6bff"               # Adjusted soft indigo for contrast
        light_accent = "#7fbaff"               # Lighter blue for dark
        medium_accent = "#549aff"              # Logo blue
        very_light_accent = "#d6e4ff"          # Pale blue
        border_color = "#27385a"               # Muted blue border
        
        # Status colors
        success_color = "#25ce7b"              # Green with visibility
        warning_color = "#ffb74d"              # Light orange
        error_color = "#ff7675"                # Coral red
        
        # Other UI colors
        highlight_color = "#5a6bff"            # Accent for highlights
        button_color = "#0048ad"               # Primary for buttons
        button_hover_color = "#7fbaff"         # Lighter blue for hover
        button_text_color = "#ffffff"          # White text on buttons
        secondary_button_color = "transparent"  # Transparent for secondary buttons
        secondary_button_text = "#549aff"       # Primary color text for secondary buttons
        form_accent_color = "#5a6bff"           # Accent for form controls
    else:
        # Light theme colors
        bg_color = "#ffffff"            # White
        card_bg_color = "#f6f9ff"       # Soft off-white blue
        text_color = "#0a2a5e"          # Dark blue (deep readable)
        light_text = "#666666"          # Secondary gray
        
        # Light theme specific colors
        primary_color = "#549aff"              # Logo blue
        accent_color = "#6f7bf7"               # Soft Indigo
        light_accent = "#d6e4ff"               # Pale blue
        medium_accent = "#a8c9ff"              # Sky blue
        very_light_accent = "#f0f6ff"          # Near-white blue
        border_color = "#a8c9ff"               # Light border
        
        # Status colors
        success_color = "#2ecc71"              # Fresh green
        warning_color = "#f5a623"              # Amber
        error_color = "#e74c3c"                # Red
        
        # Other UI colors
        highlight_color = "#6f7bf7"            # Accent highlight
        button_color = "#549aff"               # Primary
        button_hover_color = "#a8c9ff"         # Lighter blue for hover
        button_text_color = "#ffffff"          # White on buttons
        secondary_button_color = "transparent" # Transparent secondary buttons
        secondary_button_text = "#549aff"      # Primary color text
        form_accent_color = "#6f7bf7"          # Accent for form controls
    
    # Return all colors as a dictionary
    return {
        "is_dark_theme": is_dark_theme,
        "primary_color": primary_color,
        "accent_color": accent_color,
        "light_accent": light_accent,
        "medium_accent": medium_accent,
        "very_light_accent": very_light_accent,
        "bg_color": bg_color,
        "card_bg_color": card_bg_color,
        "text_color": text_color,
        "light_text": light_text,
        "border_color": border_color,
        "success_color": success_color,
        "warning_color": warning_color,
        "error_color": error_color,
        "highlight_color": highlight_color,
        "button_color": button_color,
        "button_hover_color": button_hover_color,
        "button_text_color": button_text_color,
        "secondary_button_color": secondary_button_color,
        "secondary_button_text": secondary_button_text,
        "form_accent_color": form_accent_color
    }

def apply_theme_aware_styles():
    """
    Apply consistent styling that works well with Streamlit's theme system in both light and dark modes.
    Returns whether dark mode is active.
    """
    # Get the theme from session state or detect from Streamlit's options
    if 'theme' in st.session_state:
        # Use the user-selected theme from session state
        is_dark_theme = st.session_state.theme == 'dark'
    else:
        # Fallback to auto-detection
        try:
            base_theme = st.get_option("theme.base")
            is_dark_theme = base_theme == "dark"
        except:
            # Fallback to session state if Streamlit options aren't available
            is_dark_theme = st.session_state.get('theme', 'light') == 'dark'
    
    # Store theme in session state for consistent use across the app
    st.session_state.theme = "dark" if is_dark_theme else "light"
    
    # Get all theme colors
    colors = get_theme_colors()
    
    # Apply consistent styling for both themes
    st.markdown(f"""
    <style>
    /* Base typography and spacing */
    html, body, [data-testid="stAppViewContainer"] {{
        font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
        line-height: 1.6;
    }}
    
    /* Remove all underlines from links and interactive elements throughout the app */
    a, a:hover, a:visited, a:active,
    .stButton, .stDownloadButton,
    [role="button"], [role="link"],
    [data-baseweb="tab"], [data-baseweb="accordion"],
    .streamlit-expanderHeader, .css-ch5dnh {{
        text-decoration: none !important;
        border-bottom: none !important;
    }}
    
    /* Remove underlines from markdown links */
    .element-container a, .element-container a:hover {{
        text-decoration: none !important;
        border-bottom: none !important;
    }}
    
    /* Remove underlines from sidebar links */
    .stSidebar a, .stSidebar a:hover {{
        text-decoration: none !important;
        border-bottom: none !important;
    }}
    
    /* Hide the default streamlit footer links */
    footer {{
        visibility: hidden;
    }}
    
    /* Uncomment to show the main menu
    #MainMenu {{visibility: hidden;}}
    */
    
    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }}
    
    /* Chart color overrides */
    /* Native Streamlit bar charts */
    div[data-testid="stVegaLiteChart"] svg g rect.mark-rect {{
        fill: {colors["primary_color"]} !important;
    }}
    
    /* Fix other Altair chart elements */
    div[data-testid="stVegaLiteChart"] svg .mark-symbol path {{
        fill: {colors["primary_color"]} !important;
        stroke: {colors["primary_color"]} !important;
    }}
    
    div[data-testid="stVegaLiteChart"] svg .mark-line path {{
        stroke: {colors["primary_color"]} !important;
    }}
    
    div[data-testid="stVegaLiteChart"] svg .mark-area path {{
        fill: {colors["light_accent"]}88 !important;
    }}
    
    /* Fix stacked bar charts */
    div[data-testid="stVegaLiteChart"] svg g rect[aria-label*="stack"] {{
        fill: {colors["primary_color"]} !important;
    }}
    
    /* Fix line and area charts */
    div[data-testid="stVegaLiteChart"] svg g path[class*="line"] {{
        stroke: {colors["primary_color"]} !important;
    }}
    
    div[data-testid="stVegaLiteChart"] svg g path[class*="area"] {{
        fill: {colors["light_accent"]}88 !important;
    }}
    
    /* Fixes Plotly charts */
    .js-plotly-plot .plotly .scatter .points path {{
        fill: {colors["accent_color"]} !important;
    }}
    
    /* Bar chart colors */
    .js-plotly-plot .plotly .bars .point path {{
        fill: {colors["primary_color"]} !important;
    }}
    
    /* Line chart colors */
    .js-plotly-plot .plotly .scatter .lines path {{
        stroke: {colors["accent_color"]} !important;
    }}
    
    /* Area chart fill */
    .js-plotly-plot .plotly .scatter .fills path {{
        fill: {colors["light_accent"]}88 !important;
    }}
    
    /* Improved header typography */
    h1, h2, h3, h4, h5, h6 {{
        font-weight: 600;
        margin-bottom: 0.75rem;
        color: {colors["text_color"]};
    }}
    
    h1 {{
        font-size: 2rem;
        font-weight: 700;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }}
    
    h2 {{
        font-size: 1.5rem;
        padding-bottom: 0.25rem;
        margin: 1.5rem 0 1rem 0;
    }}
    
    h3 {{
        font-size: 1.2rem;
        margin: 1.25rem 0 0.75rem 0;
    }}
    
    /* Enhanced sidebar navigation */
    .sidebar .stButton > button {{
        width: 100%;
        border-radius: 6px;
        height: 2.5rem;
        font-weight: 500;
        margin-bottom: 0.75rem;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }}
    
    .sidebar .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}
    
    /* Improved spacing for vertical blocks */
    div[data-testid="stVerticalBlock"] > div {{
        padding-bottom: 0.5rem;
    }}
    
    /* Enhanced styling for cards/containers */
    div.stCard, .card {{
        background-color: {colors["card_bg_color"]};
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid {colors["border_color"]};
    }}
    
    /* Apply proper styling for markdown-rendered cards */
    {".card { background-color: " + colors["card_bg_color"] + "; color: " + colors["text_color"] + "; border: 2px solid " + colors["border_color"] + "; }"}
    
    /* Theme-specific extra card styles */
    .st-emotion-cache-1y4p8pa,
    .st-emotion-cache-1gulkj5 {{ 
        background-color: {colors["card_bg_color"]} !important; 
        border-color: {colors["border_color"]} !important;
    }}
    
    /* Enhanced form controls */
    input, select, textarea, div[data-baseweb="input"], div[data-baseweb="textarea"] {{
        border-radius: 6px !important;
        border: 1px solid {colors["border_color"]} !important;
    }}
    
    input:focus, select:focus, textarea:focus, div[data-baseweb="input"]:focus, div[data-baseweb="textarea"]:focus {{
        border-color: {colors["primary_color"]} !important;
        box-shadow: 0 0 0 2px {colors["primary_color"]}20 !important;
    }}
    
    /* Force all sliders to use our colors */
    [data-testid="stSlider"] {{
        margin-top: 1rem;
        margin-bottom: 1rem;
    }}
    
    [data-testid="stSlider"] > div > div > div > div {{
        background-color: {colors["form_accent_color"]} !important;
    }}
    
    [data-testid="stSlider"] > div > div > div {{
        background-color: {colors["light_accent"]}40 !important;
    }}
    
    /* Fix multiselect pills */
    div[data-testid="stMultiSelect"] span div {{
        background-color: {colors["form_accent_color"]} !important;
        color: white !important;
    }}
    
    div[data-testid="stMultiSelect"] span {{
        background-color: {colors["form_accent_color"]} !important;
        color: white !important;
    }}
    
    /* Fix checkbox color */
    div[data-testid="stCheckbox"] label div[data-testid="stCheckbox"] div[aria-checked="true"] {{
        background-color: {colors["form_accent_color"]} !important;
        border-color: {colors["form_accent_color"]} !important;
    }}
    
    /* Fix radio button color */
    div[data-testid="stRadio"] label div[data-testid="stRadio"] div[aria-checked="true"] {{
        background-color: {colors["form_accent_color"]} !important;
        border-color: {colors["form_accent_color"]} !important;
    }}
    
    /* All buttons - Base styling */
    .stButton > button, 
    button[kind="primary"], 
    button[kind="secondary"] {{
        border-radius: 6px !important;
        font-weight: 500 !important;
        padding: 0.375rem 1rem !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }}
    
    /* Standard and primary buttons */
    .stButton > button,
    button[kind="primary"] {{
        background-color: {colors["button_color"]} !important;
        color: {colors["button_text_color"]} !important;
        border: 1px solid {colors["button_color"]} !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12) !important;
    }}
    
    .stButton > button:hover,
    button[kind="primary"]:hover {{
        background-color: {colors["button_hover_color"]} !important;
        border-color: {colors["button_color"]} !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
    }}
    
    /* Secondary buttons */
    button[kind="secondary"] {{
        background-color: {colors["secondary_button_color"]} !important;
        color: {colors["secondary_button_text"]} !important;
        border: 1px solid {colors["secondary_button_color"]} !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12) !important;
    }}
    
    button[kind="secondary"]:hover {{
        background-color: {colors["secondary_button_color"]}cc !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
        transform: translateY(-2px) !important;
    }}
    
    /* Download button */
    [data-testid="stDownloadButton"] button {{
        background-color: {colors["button_color"]} !important;
        color: {colors["button_text_color"]} !important;
        border-color: {colors["button_color"]} !important;
    }}
    
    [data-testid="stDownloadButton"] button:hover {{
        background-color: {colors["button_hover_color"]} !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
    }}
    
    /* Disabled buttons */
    .stButton > button:disabled,
    button[kind="primary"]:disabled,
    button[kind="secondary"]:disabled {{
        opacity: 0.6 !important;
        cursor: not-allowed !important;
        transform: none !important;
        box-shadow: none !important;
    }}
    
    /* Enhanced metrics */
    div[data-testid="metric-container"] {{
        background-color: {colors["card_bg_color"]};
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid {colors["border_color"]};
    }}
    
    div[data-testid="metric-container"] > div:nth-child(1) {{
        color: {colors["light_text"]};
        font-size: 0.9rem;
        font-weight: 500;
    }}
    
    div[data-testid="metric-container"] > div:nth-child(2) {{
        color: {colors["text_color"]};
        font-size: 1.8rem;
        font-weight: 600;
    }}
    
    /* Enhanced alerts */
    div[data-testid="stAlert"] {{
        border-radius: 6px;
        border-width: 1px;
        padding: 0.75rem 1rem;
    }}
    
    /* Make all cursors visible regardless of theme */
    input, textarea, [data-baseweb="input"] input, [data-baseweb="textarea"] textarea, [data-baseweb="select"] input {{
        caret-color: {colors["primary_color"]} !important;
    }}
    
    /* Tabs styling */
    button[data-baseweb="tab"] {{
        font-weight: 600;
    }}
    
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {colors["primary_color"]} !important;
        border-bottom-color: {colors["primary_color"]} !important;
    }}
    
    /* Progress bar enhancements */
    div[role="progressbar"] > div:first-child {{
        background-color: {colors["light_accent"]};
    }}
    
    div[role="progressbar"] > div:nth-child(2) {{
        background-color: {colors["primary_color"]};
    }}
    </style>
    """, unsafe_allow_html=True)
    
    return is_dark_theme 

def get_component_styles():
    """
    Returns a dictionary of common component styles that can be reused across the app.
    These styles are based on the current theme colors.
    """
    colors = get_theme_colors()
    
    # Define reusable component styles
    return {
        "card_container": f"""
            background-color: {colors["card_bg_color"]};
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 10px 20px rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
            border: 1px solid {colors["border_color"]};
            color: {colors["text_color"]};
        """,
        
        "timer_container": f"""
            background-color: {colors["card_bg_color"]};
            border-radius: 15px;
            padding: 2rem 1.5rem;
            box-shadow: 0 10px 20px rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
            border: 1px solid {colors["border_color"]};
            color: {colors["text_color"]};
            text-align: center;
        """,
        
        "settings_container": f"""
            background-color: {colors["card_bg_color"]};
            border-radius: 15px;
            padding: 1.2rem;
            box-shadow: 0 10px 20px rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
            border: 1px solid {colors["border_color"]};
            color: {colors["text_color"]};
            text-align: left;
        """,
        
        "transition_container": f"""
            background-color: {colors["card_bg_color"]};
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 10px 20px rgba(0,0,0,0.05);
            border: 1px solid {colors["border_color"]};
            text-align: center;
            color: {colors["text_color"]};
        """,
        
        "stats_card": f"""
            background-color: {colors["card_bg_color"]}; 
            border-radius: 10px;
            padding: 15px; 
            text-align: center; 
            border: 1px solid {colors["border_color"]};
            color: {colors["text_color"]};
        """,
        
        "section_heading": f"""
            color: {colors["text_color"]}; 
            font-size: 1.5rem; 
            font-weight: 600; 
            margin-bottom: 1rem;
            padding-bottom: 0.5rem; 
            border-bottom: 2px solid {colors["primary_color"]};
        """,
        
        "main_heading": f"""
            color: {colors["text_color"]}; 
            font-size: 1.8rem; 
            font-weight: 700;
            margin-bottom: 1.2rem;
            padding: 0.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid {colors["primary_color"]};
            display: flex;
            align-items: center;
            gap: 10px;
            background-color: {"#1a202c" if colors["is_dark_theme"] else "transparent"}; 
            border-radius: 8px;
        """,
        
        "control_button": f"""
            background-color: {colors["primary_color"]} !important;
            color: white !important;
            font-size: 24px !important;
            border-radius: 50% !important;
            width: 60px !important;
            height: 60px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 0 !important;
            min-width: unset !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
        """,
        
        "pause_button": f"""
            background-color: {colors["accent_color"]} !important;
            color: white !important;
            font-size: 24px !important;
            border-radius: 50% !important;
            width: 60px !important;
            height: 60px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 0 !important;
            min-width: unset !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
        """,
        
        "reset_button": f"""
            background-color: {colors["border_color"]} !important;
            color: white !important;
            font-size: 24px !important;
            border-radius: 50% !important;
            width: 60px !important;
            height: 60px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 0 !important;
            min-width: unset !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
        """
    } 