import streamlit as st
from utils.theme import apply_theme_aware_styles, get_theme_colors

# Set up the page configuration
st.set_page_config(
    page_title="ZenFlow Theme Test",
    page_icon="🎨",
    layout="wide"
)

# Add theme toggle functionality
if 'theme' not in st.session_state:
    # Initialize with system preference or default to light
    st.session_state.theme = 'light'

# Function to toggle theme
def toggle_theme(theme_name):
    st.session_state.theme = theme_name
    st.rerun()

# Apply our theme-aware styling - this will handle all styling centrally
is_dark = apply_theme_aware_styles()

# Get the current theme's color palette
colors = get_theme_colors()

# Display current theme info and toggle buttons
st.title("ZenFlow Theme Tester")

# Create toggle buttons at the top right
col1, col2, col3, col4 = st.columns([1, 1, 0.15, 0.15])
with col1:
    st.write(f"Current theme: {st.session_state.get('theme', 'unknown')}")
    st.write(f"Is dark mode: {is_dark}")
with col3:
    if st.button("🌙 Dark", use_container_width=True):
        toggle_theme('dark')
with col4:
    if st.button("☀️ Light", use_container_width=True):
        toggle_theme('light')

# Theme color palette section
st.header("ZenFlow Color Palette")

# Display the color palette
st.subheader("Primary Color Palette")
cols = st.columns(4)
with cols[0]:
    st.markdown(f'<div style="background-color: {colors["primary_color"]}; height: 50px; border-radius: 6px;"></div>', unsafe_allow_html=True)
    st.write("Primary Color")
    st.code(colors["primary_color"])
with cols[1]:
    st.markdown(f'<div style="background-color: {colors["accent_color"]}; height: 50px; border-radius: 6px;"></div>', unsafe_allow_html=True)
    st.write("Accent Color")
    st.code(colors["accent_color"])
with cols[2]:
    st.markdown(f'<div style="background-color: {colors["medium_accent"]}; height: 50px; border-radius: 6px;"></div>', unsafe_allow_html=True)
    st.write("Medium Accent")
    st.code(colors["medium_accent"])
with cols[3]:
    st.markdown(f'<div style="background-color: {colors["light_accent"]}; height: 50px; border-radius: 6px;"></div>', unsafe_allow_html=True)
    st.write("Light Accent")
    st.code(colors["light_accent"])

# Status colors
st.subheader("Status Colors")
cols = st.columns(3)
with cols[0]:
    st.markdown(f'<div style="background-color: {colors["error_color"]}; height: 50px; border-radius: 6px;"></div>', unsafe_allow_html=True)
    st.write("Error Color")
    st.code(colors["error_color"])
with cols[1]:
    st.markdown(f'<div style="background-color: {colors["warning_color"]}; height: 50px; border-radius: 6px;"></div>', unsafe_allow_html=True)
    st.write("Warning Color")
    st.code(colors["warning_color"])
with cols[2]:
    st.markdown(f'<div style="background-color: {colors["success_color"]}; height: 50px; border-radius: 6px;"></div>', unsafe_allow_html=True)
    st.write("Success Color")
    st.code(colors["success_color"])

# Additional theme colors
st.subheader("UI Colors")
cols = st.columns(4)
with cols[0]:
    st.markdown(f'<div style="background-color: {colors["bg_color"]}; height: 50px; border-radius: 6px; border: 1px solid #ddd;"></div>', unsafe_allow_html=True)
    st.write("Background")
    st.code(colors["bg_color"])
with cols[1]:
    st.markdown(f'<div style="background-color: {colors["card_bg_color"]}; height: 50px; border-radius: 6px; border: 1px solid #ddd;"></div>', unsafe_allow_html=True)
    st.write("Card Background")
    st.code(colors["card_bg_color"])
with cols[2]:
    st.markdown(f'<div style="background-color: {colors["text_color"]}; height: 50px; border-radius: 6px;"></div>', unsafe_allow_html=True)
    st.write("Text Color")
    st.code(colors["text_color"])
with cols[3]:
    st.markdown(f'<div style="background-color: {colors["border_color"]}; height: 50px; border-radius: 6px;"></div>', unsafe_allow_html=True)
    st.write("Border Color")
    st.code(colors["border_color"])

# Typography
st.header("Typography")
st.markdown("""
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6

Normal paragraph text. Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

**Bold text** and *italic text* and `code text`.

> Blockquote: Lorem ipsum dolor sit amet, consectetur adipiscing elit.
""")

# Display card examples
st.header("Component Examples")

with st.expander("Cards & Containers"):
    cols = st.columns(2)
    with cols[0]:
        st.markdown("""
        <div class="card">
            <h3>Standard Card</h3>
            <p>This is a standard card container with some content inside.</p>
            <p>Cards help organize related information together.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        with st.container():
            st.subheader("Container")
            st.write("This is a standard Streamlit container")
            st.info("It can contain any Streamlit widgets")

# Test buttons
st.subheader("Buttons")
button_cols = st.columns(4)
with button_cols[0]:
    st.button("Primary Button", use_container_width=True)
with button_cols[1]:
    st.button("Secondary Button", type="secondary", use_container_width=True)
with button_cols[2]:
    st.download_button("Download Button", "test data", use_container_width=True)
with button_cols[3]:
    st.button("Disabled Button", disabled=True, use_container_width=True)

# Test form inputs
st.subheader("Form Controls")
form_cols = st.columns(2)
with form_cols[0]:
    st.text_input("Text Input", "Sample text")
    st.number_input("Number Input", value=42)
    st.slider("Slider", 0, 100, 50)
    st.date_input("Date input")
with form_cols[1]:
    options = ["Option 1", "Option 2", "Option 3"]
    st.selectbox("Select Box", options)
    st.multiselect("Multi-select", options)
    st.checkbox("Checkbox")
    st.radio("Radio", options)

# Test tabs
st.subheader("Tabs")
tab1, tab2, tab3 = st.tabs(["Dashboard", "Settings", "Help"])
with tab1:
    st.write("Dashboard content")
    
    # Create Plotly bar chart with direct graph objects
    import plotly.graph_objects as go
    import pandas as pd
    
    bar_data = pd.DataFrame({
        'Category': ['A', 'B', 'C', 'D', 'E', 'F'],
        'Value': [1, 5, 2, 6, 2, 1]
    })
    
    # Create a figure with graph_objects for direct control
    fig_bar = go.Figure()
    
    # Add the bar trace with theme colors
    fig_bar.add_trace(
        go.Bar(
            x=bar_data['Category'],
            y=bar_data['Value'],
            marker_color=colors["primary_color"],
            name='Values'
        )
    )
    
    # Update the layout
    fig_bar.update_layout(
        title='Dashboard Metrics',
        template='plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=250,
        margin=dict(l=20, r=20, t=50, b=20),
        font_color=colors["text_color"]
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)
    
with tab2:
    st.write("Settings content")
    st.toggle("Enable notifications")
    st.select_slider("Brightness", options=["Low", "Medium", "High"])
with tab3:
    st.write("Help content")
    st.markdown("For more information, [visit our docs](https://example.com)")

# Add chart examples
st.subheader("Additional Chart Examples")

chart_cols = st.columns(2)

with chart_cols[0]:
    st.write("Bar Chart")
    # Create Plotly bar chart
    import plotly.graph_objects as go
    
    bar_data = pd.DataFrame({
        'Category': ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
        'Value': [3, 5, 7, 9, 5, 3, 1]
    })
    
    fig_bar = go.Figure()
    
    fig_bar.add_trace(
        go.Bar(
            x=bar_data['Category'],
            y=bar_data['Value'],
            marker_color=colors["primary_color"],
            name='Values'
        )
    )
    
    fig_bar.update_layout(
        title='Custom Bar Chart',
        template='plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=colors["text_color"]
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

with chart_cols[1]:
    st.write("Line Chart")
    # Create Plotly line chart
    import plotly.graph_objects as go
    
    line_data = pd.DataFrame({
        'X': [1, 2, 3, 4, 5, 6, 7],
        'Y': [1, 2, 3, 4, 5, 6, 7]
    })
    
    fig_line = go.Figure()
    
    fig_line.add_trace(
        go.Scatter(
            x=line_data['X'], 
            y=line_data['Y'],
            mode='lines',
            line=dict(
                color=colors["primary_color"],
                width=4
            ),
            name='Values'
        )
    )
    
    fig_line.update_layout(
        title='Custom Line Chart',
        template='plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=colors["text_color"]
    )
    
    st.plotly_chart(fig_line, use_container_width=True)

# Add interactive Plotly example 
st.subheader("Interactive Plotly Chart")
import plotly.graph_objects as go
import pandas as pd

# Create some example data
data = {'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Sales': [20, 35, 30, 40, 50, 45],
        'Expenses': [15, 25, 20, 30, 35, 30]}
df = pd.DataFrame(data)

# Create a figure with graph_objects for direct control
fig = go.Figure()

# Add the Sales trace
fig.add_trace(
    go.Scatter(
        x=df['Month'],
        y=df['Sales'],
        mode='lines+markers',
        line=dict(
            color=colors["primary_color"],
            width=4
        ),
        marker=dict(
            color=colors["primary_color"],
            size=10
        ),
        name='Sales'
    )
)

# Add the Expenses trace
fig.add_trace(
    go.Scatter(
        x=df['Month'],
        y=df['Expenses'],
        mode='lines+markers',
        line=dict(
            color=colors["accent_color"],
            width=4
        ),
        marker=dict(
            color=colors["accent_color"],
            size=10
        ),
        name='Expenses'
    )
)

# Update the layout to match our theme
fig.update_layout(
    title='Monthly Performance',
    template='plotly_white',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_color=colors["text_color"],
    legend=dict(
        font=dict(
            color=colors["text_color"]
        )
    )
)

# Plot the figure
st.plotly_chart(fig, use_container_width=True)

# Test alerts
st.subheader("Alerts")
st.info("This is an info message")
st.success("This is a success message")
st.warning("This is a warning message")
st.error("This is an error message")

# Test metric displays
st.subheader("Metrics")
metric_cols = st.columns(3)
with metric_cols[0]:
    st.metric("Revenue", "$500", "+20%")
with metric_cols[1]: 
    st.metric("Costs", "$250", "-10%")
with metric_cols[2]:
    st.metric("Profit", "$250", "+50%")

# Progress indicators
st.subheader("Progress Indicators")
st.progress(0.66)
with st.spinner("Loading..."):
    pass 