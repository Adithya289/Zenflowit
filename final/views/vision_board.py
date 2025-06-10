import os
import json
import streamlit as st
from models.vision_board import VisionBoard
from utils.theme import apply_theme_aware_styles
from utils.db import save_vision_board_customizations, load_vision_board_customizations
# from utils.vision_board import (
#     save_uploaded_image, 
#     save_image_from_url, 
#     get_image_base64, 
#     get_tile_css,
#     available_themes
# )

def show_vision_board():
    """Display the vision board page with new UI focused on customization"""
    if "user_id" not in st.session_state:
        st.warning("Please log in to access your Vision Board.")
        return
    
    # Add theme-aware styling for vision board
    st.markdown("""
    <style>
    /* Theme-aware vision board styling */
    .vision-board-container {
        background-color: var(--background-color);
        border: 1px solid var(--secondary-background-color);
        border-radius: 0.8rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
    
    /* Custom headers */
    .vision-header {
        text-align: center;
        color: var(--primary-color);
        margin-bottom: 1.5rem;
    }
    
    .vision-subheader {
        text-align: center;
        margin-bottom: 1.5rem;
        font-size: 1.2rem;
        color: var(--text-color);
    }
    
    /* Style for mini boards */
    .mini-board {
        background-color: var(--background-color);
        border: 2px solid var(--primary-color);
        border-radius: 0.8rem;
        padding: 1rem;
        margin-bottom: 1rem;
        min-height: 200px;
    }
    
    .mini-board-header {
        color: var(--primary-color);
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    /* Custom button styles */
    .vision-button {
        background-color: var(--primary-color) !important;
        color: white !important;
        border-radius: 0.5rem !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    /* Empty board styling */
    .empty-board {
        width: 100%;
        height: 500px;
        background-color: var(--background-color);
        border: 4px dashed var(--secondary-background-color);
        border-radius: 15px;
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 auto 20px auto;
        overflow: auto;
    }
    
    .empty-board-text {
        text-align: center;
        padding: 20px;
        color: var(--text-color);
    }
    
    .warning-banner {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        display: flex;
        align-items: center;
    }
    
    .warning-banner.dark {
        background-color: rgba(255, 171, 0, 0.1);
        border: 1px solid rgba(255, 171, 0, 0.2);
    }
    
    .warning-banner.light {
        background-color: rgba(255, 171, 0, 0.1);
        border: 1px solid rgba(255, 171, 0, 0.2);
    }
    
    .warning-icon {
        font-size: 1.2rem;
        margin-right: 0.5rem;
    }
    
    .warning-text {
        font-size: 0.9rem;
        line-height: 1.4;
    }
    </style>
    """, unsafe_allow_html=True)
    
    user_id = st.session_state.user_id
    
    # Initialize session state variables
    if "show_vision_board_creator" not in st.session_state:
        # Load saved customizations from database
        saved_customizations = load_vision_board_customizations(user_id)
        if saved_customizations:
            st.session_state.show_vision_board_creator = True
            st.session_state.category_customizations = saved_customizations
        else:
            st.session_state.show_vision_board_creator = False
            st.session_state.category_customizations = {}
    
    if "vision_board_frame_shape" not in st.session_state:
        st.session_state.vision_board_frame_shape = "Square"
    if "vision_board_theme" not in st.session_state:
        current_theme = VisionBoard.get_user_theme(user_id)
        st.session_state.vision_board_theme = current_theme or "default"
    if "category_customizations" not in st.session_state:
        # Load saved customizations from database
        st.session_state.category_customizations = load_vision_board_customizations(user_id)
    
    # Ensure all existing categories have the description field
    for key in st.session_state.category_customizations:
        if "description" not in st.session_state.category_customizations[key]:
            st.session_state.category_customizations[key]["description"] = "Add your aspirations here"
        
    # Page title with better styling
    st.markdown("""
    <h1 class="vision-header">✨ Vision Board ✨</h1>
    <p class="vision-subheader">Visualize your dreams, aspirations, and goals</p>
    """, unsafe_allow_html=True)
    
    # Apply theme-aware styling
    is_dark_theme = apply_theme_aware_styles()
    
    # Add work-in-progress message at the top
    wip_warning_html = f"""
    <div class="warning-banner {'dark' if is_dark_theme else 'light'}">
        <div class="warning-icon">🚧</div>
        <div class="warning-text">
            <strong>Work in Progress:</strong> This Vision Board feature is currently under development. More functionality, including saving your boards and adding content to each category, will be available soon. Feel free to explore the current customization options!
        </div>
    </div>
    """
    st.markdown(wip_warning_html, unsafe_allow_html=True)
    
    # Show image size warning banner
    warning_html = f"""
    <div class="warning-banner {'dark' if is_dark_theme else 'light'}">
        <div class="warning-icon">⚠️</div>
        <div class="warning-text">
            Please note that images are stored in base64 format. Using very large images may impact performance.
            Consider using compressed or resized images for optimal experience.
        </div>
    </div>
    """
    st.markdown(warning_html, unsafe_allow_html=True)
    
    # Main button to start creating vision board
    if not st.session_state.show_vision_board_creator:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎨 Create Your Vision Board", use_container_width=True, key="start_vision_board"):
                st.session_state.show_vision_board_creator = True
                st.rerun()
    
    # Show customization options if button was clicked
    if st.session_state.show_vision_board_creator:
        # Define the categories with emojis
        categories = [
            {"id": 1, "name": "💼 Career & Financial", "color": "#3f51b5"},
            {"id": 2, "name": "🧘‍♂️ Health & Wellness", "color": "#4caf50"},
            {"id": 3, "name": "🧠 Personal Growth", "color": "#9c27b0"},
            {"id": 4, "name": "🌿 Spiritual", "color": "#009688"},
            {"id": 5, "name": "❤️ Relationships", "color": "#e91e63"},
            {"id": 6, "name": "✈️ Travel & Adventure", "color": "#2196f3"},
            {"id": 7, "name": "🏡 Lifestyle", "color": "#ff9800"},
            {"id": 8, "name": "🎨 Hobbies", "color": "#673ab7"},
            {"id": 9, "name": "📅 Time & Routine", "color": "#795548"}
        ]
        
        # Get a list of all category names
        category_names = [cat["name"] for cat in categories]
        
        # Initialize session state for selected categories
        if "selected_categories" not in st.session_state:
            st.session_state.selected_categories = []
        
        # Move category selection to the top
        col1, col2, col3 = st.columns([1, 4, 1])
        
        with col1:
            st.write("#### Choose Categories")  # Add back the heading
            # Use selectbox for category selection with minimal styling
            new_category = st.selectbox(
                "",  # Remove label
                options=category_names,
                key="category_select",
                label_visibility="collapsed"  # Hide label completely
            )
            
            # Add button to add the selected category
            if st.button("➕ Add", use_container_width=True):
                if new_category:
                    # Generate a unique key for this category instance using timestamp
                    import time
                    timestamp = int(time.time() * 1000)  # Current time in milliseconds
                    cat_key = f"cat_{new_category.replace(' ', '_')}_{timestamp}"
                    
                    # Add the category with its unique key
                    st.session_state.selected_categories.append({
                        "name": new_category,
                        "key": cat_key
                    })
                    
                    # Initialize customization for this category if it doesn't exist
                    if cat_key not in st.session_state.category_customizations:
                        st.session_state.category_customizations[cat_key] = {
                            "theme": st.session_state.vision_board_theme,
                            "frame": st.session_state.vision_board_frame_shape,
                            "bg_image": None,
                            "description": "Add your aspirations here"  # Add default description
                        }
                    
                    # Save the changes to the database
                    try:
                        if save_vision_board_customizations(user_id, st.session_state.category_customizations):
                            st.rerun()
                    except Exception as e:
                        st.error("Failed to save changes. Please try again.")
        
        # Empty space for better layout
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        
        # Preview container for the vision board
        if not st.session_state.selected_categories:
            # Show an empty board with instructions if no categories selected
            st.markdown("""
            <div class="empty-board">
                <div class="empty-board-text">
                    <p style="font-size: 1.2rem;">Select categories to see mini-boards here</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Create a container for the vision board
            with st.container():
                # Dictionary to map category names to their info
                category_info = {cat["name"]: cat for cat in categories}
                
                # Create the mini boards using Streamlit's native components
                for i in range(0, len(st.session_state.selected_categories), 2):
                    # Create columns for this row
                    cols = st.columns(2)
                    
                    for j in range(2):
                        idx = i + j
                        if idx < len(st.session_state.selected_categories):
                            category = st.session_state.selected_categories[idx]
                            cat_name = category["name"]
                            cat_key = category["key"]
                            cat = category_info.get(cat_name, {"color": "#ce93d8"})
                            
                            # Create a mini vision board in this column
                            with cols[j]:
                                # Extract the emoji from the category name
                                emoji = ""
                                if ":" in cat_name:
                                    parts = cat_name.split(" ", 1)
                                    emoji = parts[0]
                                    label = parts[1] if len(parts) > 1 else cat_name
                                else:
                                    label = cat_name
                                
                                # Use the existing unique key from the category dictionary
                                cat_key = category["key"]
                                
                                # Initialize customization for this category if it doesn't exist
                                if cat_key not in st.session_state.category_customizations:
                                    st.session_state.category_customizations[cat_key] = {
                                        "theme": st.session_state.vision_board_theme,
                                        "frame": st.session_state.vision_board_frame_shape,
                                        "bg_image": None,
                                        "description": "Add your aspirations here"  # Add default description
                                    }
                                
                                # Create session state for tracking this category's customization panel
                                if f"show_customize_{cat_key}" not in st.session_state:
                                    st.session_state[f"show_customize_{cat_key}"] = False
                                
                                # Use a container for proper placement of the + button
                                with st.container():
                                    col1, col2 = st.columns([0.9, 0.1])  # 90-10 split for content vs button
                                    with col2:
                                        # Add a small button to toggle the customization panel
                                        customize_button = st.button(
                                            "➕", 
                                            key=f"customize_btn_{cat_key}",
                                            help=f"Customize {label} board"
                                        )
                                
                                # Toggle customization panel visibility when button is clicked
                                if customize_button:
                                    st.session_state[f"show_customize_{cat_key}"] = not st.session_state[f"show_customize_{cat_key}"]
                                    st.rerun()
                                
                                # Show customization panel if toggled on
                                if st.session_state[f"show_customize_{cat_key}"]:
                                    st.markdown(f"##### Customize {label}")
                                    # Create two columns for frame and color options
                                    custom_col1, custom_col2 = st.columns(2)
                                    
                                    with custom_col1:
                                        # Frame shape selection for this category
                                        frame_options = ["Square", "Frame", "Circle"]
                                        selected_frame = st.selectbox(
                                            "Frame Shape",
                                            options=frame_options,
                                            index=frame_options.index(st.session_state.category_customizations[cat_key]["frame"]),
                                            key=f"frame_{cat_key}"
                                        )
                                        
                                        # Update category's frame if changed
                                        if selected_frame != st.session_state.category_customizations[cat_key]["frame"]:
                                            st.session_state.category_customizations[cat_key]["frame"] = selected_frame
                                            # Automatically save the change
                                            try:
                                                if save_vision_board_customizations(user_id, st.session_state.category_customizations):
                                                    st.rerun()
                                            except Exception as e:
                                                st.error("Failed to save changes. Please try again.")
                                    
                                    with custom_col2:
                                        # Background color selection for this category
                                        color_options = {
                                            "lightblue": {"name": "Light Blue", "color": "#e3f2fd", "text": "#0d47a1", "border": "#90caf9"},
                                            "lightgreen": {"name": "Light Green", "color": "#e8f5e9", "text": "#2e7d32", "border": "#a5d6a7"},
                                            "purple": {"name": "Purple", "color": "#f3e5f5", "text": "#6a1b9a", "border": "#ce93d8"},
                                            "pink": {"name": "Pink", "color": "#fce4ec", "text": "#c2185b", "border": "#f48fb1"},
                                            "yellow": {"name": "Yellow", "color": "#fffde7", "text": "#fbc02d", "border": "#fff59d"},
                                            "orange": {"name": "Orange", "color": "#fff3e0", "text": "#e65100", "border": "#ffcc80"},
                                            "red": {"name": "Red", "color": "#ffebee", "text": "#c62828", "border": "#ef9a9a"}
                                        }
                                        
                                        # Create a list of color names for the dropdown
                                        color_names = [color_info["name"] for key, color_info in color_options.items()]
                                        color_keys = list(color_options.keys())
                                        
                                        # Find current theme index for this category
                                        cat_theme = st.session_state.category_customizations[cat_key]["theme"]
                                        current_theme_index = 0
                                        for idx, key in enumerate(color_keys):
                                            if key == cat_theme:
                                                current_theme_index = idx
                                                break
                                        
                                        # Use a dropdown for color selection
                                        selected_color_name = st.selectbox(
                                            "Background Color",
                                            options=color_names,
                                            index=current_theme_index,
                                            key=f"color_{cat_key}"
                                        )
                                        
                                        # Map the selected name back to the key
                                        selected_index = color_names.index(selected_color_name)
                                        selected_color_key = color_keys[selected_index]
                                        
                                        # Update category's theme if changed
                                        if selected_color_key != st.session_state.category_customizations[cat_key]["theme"]:
                                            st.session_state.category_customizations[cat_key]["theme"] = selected_color_key
                                            # Automatically save the change
                                            try:
                                                if save_vision_board_customizations(user_id, st.session_state.category_customizations):
                                                    st.rerun()
                                            except Exception as e:
                                                st.error("Failed to save changes. Please try again.")

                                    # Add description customization
                                    st.markdown("---")
                                    st.write("#### Description")
                                    new_description = st.text_input(
                                        "Board Description",
                                        value=st.session_state.category_customizations[cat_key]["description"],
                                        key=f"description_{cat_key}",
                                        help="Enter a description or aspiration for this board"
                                    )
                                    if new_description != st.session_state.category_customizations[cat_key]["description"]:
                                        st.session_state.category_customizations[cat_key]["description"] = new_description
                                        # Automatically save the change
                                        try:
                                            if save_vision_board_customizations(user_id, st.session_state.category_customizations):
                                                st.rerun()
                                        except Exception as e:
                                            st.error("Failed to save changes. Please try again.")

                                    # Add background image upload option
                                    st.markdown("---")
                                    st.write("#### Background Image")
                                    
                                    # Image uploader
                                    uploaded_file = st.file_uploader(
                                        "Upload an image for this category",
                                        type=["jpg", "jpeg", "png", "gif"],
                                        key=f"bg_image_{cat_key}"
                                    )
                                    
                                    # Handle uploaded file
                                    if uploaded_file is not None:
                                        # Convert the uploaded file to base64 for display
                                        import base64
                                        from io import BytesIO
                                        
                                        # Read the file and encode it
                                        bytes_data = uploaded_file.getvalue()
                                        b64str = base64.b64encode(bytes_data).decode()
                                        
                                        # Set the image in the customization data
                                        file_ext = uploaded_file.name.split(".")[-1]
                                        img_str = f"data:image/{file_ext};base64,{b64str}"
                                        
                                        # Update the bg_image in session state
                                        st.session_state.category_customizations[cat_key]["bg_image"] = img_str
                                        # Automatically save the change
                                        try:
                                            if save_vision_board_customizations(user_id, st.session_state.category_customizations):
                                                st.success("Background image uploaded successfully!")
                                        except Exception as e:
                                            st.error("Failed to save changes. Please try again.")
                                    
                                    # Option to remove the background image if one exists
                                    if st.session_state.category_customizations[cat_key]["bg_image"] is not None:
                                        if st.button("Remove Background Image", key=f"remove_bg_{cat_key}"):
                                            st.session_state.category_customizations[cat_key]["bg_image"] = None
                                            # Automatically save the change
                                            try:
                                                if save_vision_board_customizations(user_id, st.session_state.category_customizations):
                                                    st.rerun()
                                            except Exception as e:
                                                st.error("Failed to save changes. Please try again.")
                                    
                                    # Add a "Done" button to close the customization panel
                                    st.markdown("---")
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        if st.button("Done", key=f"done_customize_{cat_key}"):
                                            st.session_state[f"show_customize_{cat_key}"] = False
                                            st.rerun()
                                    with col2:
                                        if st.button("🗑️ Delete Board", key=f"delete_{cat_key}", type="secondary"):
                                            # Remove this category from selected categories
                                            st.session_state.selected_categories = [
                                                cat for cat in st.session_state.selected_categories 
                                                if cat["key"] != cat_key
                                            ]
                                            # Remove its customizations
                                            if cat_key in st.session_state.category_customizations:
                                                del st.session_state.category_customizations[cat_key]
                                            # Save the changes to the database
                                            try:
                                                if save_vision_board_customizations(user_id, st.session_state.category_customizations):
                                                    st.rerun()
                                            except Exception as e:
                                                st.error("Failed to save changes. Please try again.")
                                
                                # Get the category-specific style settings
                                cat_theme_key = st.session_state.category_customizations[cat_key]["theme"]
                                cat_frame = st.session_state.category_customizations[cat_key]["frame"]
                                
                                # Get theme styles for this specific category
                                theme_styles = {
                                    "lightblue": {"bg": "#e3f2fd", "border": "#90caf9", "text": "#0d47a1"},
                                    "lightgreen": {"bg": "#e8f5e9", "border": "#a5d6a7", "text": "#2e7d32"},
                                    "purple": {"bg": "#f3e5f5", "border": "#ce93d8", "text": "#6a1b9a"},
                                    "pink": {"bg": "#fce4ec", "border": "#f48fb1", "text": "#c2185b"},
                                    "yellow": {"bg": "#fffde7", "border": "#fff59d", "text": "#fbc02d"},
                                    "orange": {"bg": "#fff3e0", "border": "#ffcc80", "text": "#e65100"},
                                    "red": {"bg": "#ffebee", "border": "#ef9a9a", "text": "#c62828"}
                                }
                                
                                # Use category specific style
                                if cat_theme_key in theme_styles:
                                    cat_style = theme_styles[cat_theme_key]
                                else:
                                    cat_style = theme_styles["lightblue"]  # Default fallback
                                
                                # Set border style based on frame shape selection
                                if cat_frame == "Square":
                                    border_radius = "0px"
                                    border_style = f"4px solid {cat_style['border']}"
                                    box_shadow = "none"
                                elif cat_frame == "Frame":
                                    border_radius = "15px"
                                    border_style = f"12px solid {cat_style['border']}"
                                    box_shadow = f"0 0 15px {cat_style['border']}, inset 0 0 15px {cat_style['border']}"
                                else:  # Circle
                                    border_radius = "50%"
                                    border_style = f"4px solid {cat_style['border']}"
                                    box_shadow = "none"
                                
                                # Get the background image
                                bg_image = st.session_state.category_customizations[cat_key]["bg_image"]
                                
                                # Determine background style based on whether an image is uploaded
                                if bg_image:
                                    content_bg_style = f"background-image: url('{bg_image}'); background-size: cover; background-position: center;"
                                    heading_style = "color: white; margin: 0; text-align: center; width: 100%; line-height: 1.2; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);"
                                else:
                                    content_bg_style = f"background-color: {cat_style['bg']};"
                                    heading_style = f"color: {cat_style['text']}; margin: 0; text-align: center; width: 100%; line-height: 1.2;"

                                # Mini board container with enhanced styling and category-specific customizations
                                st.markdown(f"""
                                <div style="
                                    background-color: {cat_style['bg']};
                                    border: {border_style};
                                    border-radius: {border_radius};
                                    padding: 0;
                                    margin-bottom: 30px;
                                    text-align: center;
                                    height: 400px;
                                    display: flex;
                                    flex-direction: column;
                                    box-shadow: {box_shadow};
                                    transition: transform 0.3s ease;
                                    overflow: hidden;
                                ">
                                    <div style="
                                        background-color: {cat_style['border']}40;
                                        padding: 10px;
                                        height: 15%;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        border-bottom: 2px solid {cat_style['border']};
                                    ">
                                        <h3 style="{heading_style}">{emoji} {label}</h3>
                                    </div>
                                    <div style="
                                        {content_bg_style}
                                        height: 70%;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        padding: 20px;
                                        position: relative;
                                    ">
                                    </div>
                                    <div style="
                                        background-color: {cat_style['border']}20;
                                        height: 15%;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        padding: 5px 10px;
                                        border-top: 1px solid {cat_style['border']};
                                        font-size: 0.9rem;
                                        color: {cat_style['text']};
                                    ">
                                        {st.session_state.category_customizations[cat_key]["description"]}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
            
            # No instructions message displayed now
    
    # Handle adding items to vision board categories
    if "adding_item_to_category" in st.session_state and st.session_state.adding_item_to_category:
        category_name = st.session_state.adding_item_to_category
        
        # Create a form to add a new item to the selected category
        st.subheader(f"Add Item to {category_name}")
        
        # Form for adding a vision board item
        with st.form(key="add_vision_item_form"):
            # Item title
            item_title = st.text_input("Title", placeholder="Enter a title for your vision board item")
            
            # Description (optional)
            item_description = st.text_area("Description (optional)", 
                                           placeholder="Add a description or affirmation",
                                           height=100)
            
            # Image options - URL or upload
            image_option = st.radio("Add an image (optional)", 
                                   ["No image", "Upload image", "Image URL"])
            
            image_file = None
            image_url = None
            
            if image_option == "Upload image":
                image_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
            elif image_option == "Image URL":
                image_url = st.text_input("Image URL", placeholder="Enter the URL of an image")
            
            # Is this an affirmation?
            is_affirmation = st.checkbox("This is an affirmation")
            
            # Submit and cancel buttons
            col1, col2 = st.columns(2)
            with col1:
                submit_button = st.form_submit_button("Add to Vision Board")
            with col2:
                cancel_button = st.form_submit_button("Cancel")
        
        # Handle form submission
        if submit_button:
            if not item_title:
                st.error("Please enter a title for your vision board item")
            else:
                # Get the category ID
                category_id = None
                for cat in categories:
                    if cat["name"] == category_name:
                        category_id = cat["id"]
                        break
                
                # Save image if uploaded
                image_path = None
                if image_file is not None:
                    # Here you would save the image to a folder
                    # image_path = save_uploaded_image(image_file)
                    # For now, we'll just indicate that we would save it
                    image_path = "image_would_be_saved.jpg"  # Placeholder
                
                # Add the item to the vision board
                try:
                    # Add the item to the database
                    tile_id, newly_earned_rewards = VisionBoard.add_tile(
                        user_id, item_title, item_description, 
                        image_path, image_url, is_affirmation, category_id
                    )
                    
                    # Check if badges were earned and set redirect flag if needed
                    if newly_earned_rewards:
                        st.session_state.redirect_to_rewards = True
                    
                    # Show success message
                    st.success(f"Added '{item_title}' to {category_name}!")
                    
                    # Clear the adding state
                    st.session_state.adding_item_to_category = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding vision board item: {str(e)}")
        
        # Handle cancel button
        if cancel_button:
            st.session_state.adding_item_to_category = None
            st.rerun()
    
    # Placeholder for future content addition functionality
    # The 'Add Item' functionality will be implemented in a future update
    # Add work-in-progress message at the bottom of the page
    # st.markdown("---")
    # st.markdown("""
    # <div style="
    #     background-color: #fff8e1;
    #     border-left: 5px solid #ffc107;
    #     padding: 15px;
    #     margin: 20px 0;
    #     border-radius: 4px;
    # ">
    #     <h3 style="color: #ff6f00; margin-top: 0;">🚧 Work in Progress</h3>
    #     <p style="margin-bottom: 0;">
    #         This Vision Board feature is currently under development. More functionality, including saving your boards and adding content to each category, will be available soon. Feel free to explore the current customization options to create your board layout - try changing colors, frames, and uploading background images! Thank you for your patience!
    #     </p>
    # </div>
    # """, unsafe_allow_html=True)

    # Remove the save button from the sidebar since changes are now automatically saved
    with st.sidebar:
        # Remove the save button
        pass