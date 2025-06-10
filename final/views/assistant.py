import streamlit as st
from datetime import datetime
from utils.ai import initialize_gemini, get_ai_assistant_response
from utils.theme import apply_theme_aware_styles

def show_assistant():
    """
    Display the AI Assistant page
    """
    # Add warning banner at the top
    st.warning("""
        🚧 **Work in Progress**
        
        The AI Assistant feature is currently under development. We're working on enhancing its capabilities, adding more productivity-focused features, and improving response quality. Stay tuned for updates!
    """)
    
    # Apply theme-aware styling
    is_dark_theme = apply_theme_aware_styles()
    
    # Define theme-specific colors
    if is_dark_theme:
        primary_color = "#4F8BF9"
        secondary_color = "#1E1E1E"
        text_color = "#FFFFFF"
        border_color = "#333333"
        bg_color = "#0E1117"
        assistant_msg_bg = "#383838"
        user_msg_bg = "#1E3A8A"
        suggestion_bg = "#2C2C2C"
        suggestion_hover = "#3D3D3D"
    else:
        primary_color = "#4F8BF9"
        secondary_color = "#F0F2F6"
        text_color = "#262730"
        border_color = "#E0E0E0"
        bg_color = "#FFFFFF"
        assistant_msg_bg = "#F0F2F6"
        user_msg_bg = "#E1EFFE"
        suggestion_bg = "#F6F6F6"
        suggestion_hover = "#EAEAEA"
    
    # Custom styling for the assistant page
    st.markdown(f"""
    <style>
        /* Chat Messages Styling */
        .stChatMessage [data-testid="stChatMessageContent"] {{
            border-radius: 15px;
            padding: 15px;
            line-height: 1.5;
        }}
        
        /* User message styling */
        .stChatMessage [data-testid="stChatMessageContent"].user {{
            background-color: {user_msg_bg} !important;
            border: 1px solid {border_color};
        }}
        
        /* Assistant message styling */
        .stChatMessage [data-testid="stChatMessageContent"].assistant {{
            background-color: {assistant_msg_bg} !important;
            border: 1px solid {border_color};
        }}
        
        /* Info box styling */
        .tip-box {{
            background-color: {assistant_msg_bg};
            border-radius: 10px;
            padding: 10px;
            border: 1px solid {border_color};
            color: {text_color};
        }}
        
        /* Suggestion buttons styling */
        .stButton>button {{
            background-color: {suggestion_bg};
            color: {text_color};
            border: 1px solid {border_color};
            border-radius: 10px;
            padding: 10px 15px;
            font-size: 14px;
            margin-bottom: 10px;
            transition: all 0.3s;
        }}
        
        .stButton>button:hover {{
            background-color: {suggestion_hover};
            border-color: {primary_color};
        }}
        
        /* Assistant header styling */
        .header-assistant {{
            color: {primary_color};
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 20px;
            text-align: center;
            padding-bottom: 10px;
            border-bottom: 2px solid {primary_color};
        }}
        
        /* Sidebar headers */
        .sidebar-header {{
            color: {primary_color};
            font-size: 18px;
            font-weight: bold;
            margin-top: 20px;
            margin-bottom: 10px;
            padding-bottom: 5px;
            border-bottom: 1px solid {border_color};
        }}
    </style>
    """, unsafe_allow_html=True)
    
    # Display header
    st.markdown('<div class="header-assistant">ZenCoach Assistant</div>', unsafe_allow_html=True)
    
    # Initialize Gemini API
    gemini_api_ready = initialize_gemini()
    
    if not gemini_api_ready:
        st.error("Gemini API not available. Please check your .env file to ensure you have a valid Google AI API key.")
        return
    
    # Initialize chat history in session state if not already present
    if "assistant_messages" not in st.session_state:
        st.session_state.assistant_messages = []
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Function to set user input based on clicked suggestion
    def set_user_input(suggestion):
        st.session_state.user_input = suggestion
    
    # Display welcome message and add it to message history if no messages
    if not st.session_state.assistant_messages:
        # Create the welcome message content
        welcome_message = """
        👋 **Welcome to ZenCoach!** I'm your productivity and time management assistant.
        
        I can help you with:
        * Time management strategies
        * Focus techniques
        * Overcoming procrastination
        * Setting effective goals
        * Work-life balance tips
        * Habit formation
        * Using ZenFlow features effectively
        
        How can I help you be more productive today?
        """
        
        # Add the welcome message to the session state
        st.session_state.assistant_messages.append({
            "role": "assistant", 
            "content": welcome_message
        })
    
    # Display all chat messages (including the welcome message if just added)
    for message in st.session_state.assistant_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)
    
    # Add prompt suggestions if we just showed the welcome message
    if len(st.session_state.assistant_messages) == 1 and st.session_state.assistant_messages[0]["role"] == "assistant":
        st.markdown("<p><strong>Try asking about:</strong></p>", unsafe_allow_html=True)
        
        # Define suggestion topics with their content
        suggestions = [
            "How do I overcome procrastination?",
            "What is the Pomodoro technique?",
            "Tips for better work-life balance",
            "How to set effective SMART goals",
            "Best way to prioritize tasks"
        ]
        
        # Create multiple columns for a more compact layout
        cols = st.columns(3)
        
        # Create suggestion buttons using native Streamlit components
        for i, suggestion in enumerate(suggestions):
            # Place buttons in different columns for better layout
            col_index = i % 3
            
            if cols[col_index].button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                # This code runs when the suggestion button is clicked
                # Set the question in the chat input
                query = suggestion
                
                # Directly process the suggestion as if it was submitted
                # Add user message to chat history
                st.session_state.assistant_messages.append({"role": "user", "content": query})
                
                # Get AI response with spinner
                with st.spinner("Thinking..."):
                    response_text, chat_history, error = get_ai_assistant_response(
                        query,
                        st.session_state.chat_history
                    )
                    
                    if error:
                        st.error(error)
                    else:
                        # Store the updated chat history
                        if chat_history:
                            st.session_state.chat_history = chat_history
                        
                        # Add the response to the session state
                        st.session_state.assistant_messages.append({"role": "assistant", "content": response_text})
                
                # Rerun to update the UI with the new messages
                st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Ask about productivity or time management...", key="user_input"):
        # Add user message to chat history
        st.session_state.assistant_messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt, unsafe_allow_html=True)
        
        # Get AI response with spinner to indicate loading
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_text, chat_history, error = get_ai_assistant_response(
                    prompt,
                    st.session_state.chat_history
                )
                
                if error:
                    st.error(error)
                    return
                
                # Store the updated chat history
                if chat_history:
                    st.session_state.chat_history = chat_history
                
                # Display and save the response
                st.markdown(response_text, unsafe_allow_html=True)
                st.session_state.assistant_messages.append({"role": "assistant", "content": response_text})
    
    # Add sidebar options
    st.sidebar.markdown("<div class='sidebar-header'>Assistant Options</div>", unsafe_allow_html=True)
    
    # Clear chat button with confirmation
    clear_chat = st.sidebar.button("Clear Chat History", key="clear_chat")
    if clear_chat:
        confirm_clear = st.sidebar.checkbox("Confirm clearing chat history", key="confirm_clear")
        if confirm_clear:
            st.session_state.assistant_messages = []
            st.session_state.chat_history = []
            st.rerun()
    
    # Add productivity tips in the sidebar
    st.sidebar.markdown("<div class='sidebar-header'>Quick Productivity Tips</div>", unsafe_allow_html=True)
    
    # Expand tip sections
    with st.sidebar.expander("Pomodoro Technique", expanded=False):
        st.markdown(f"""
        <div class="tip-box">
            <p><strong>How it works:</strong></p>
            <ol>
                <li>Work for 25 minutes without distractions</li>
                <li>Take a 5-minute break</li>
                <li>After 4 cycles, take a longer 15-30 minute break</li>
            </ol>
            <p><em>Perfect for: Fighting procrastination and improving focus</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    with st.sidebar.expander("Eisenhower Matrix", expanded=False):
        st.markdown(f"""
        <div class="tip-box">
            <p><strong>Categorize tasks as:</strong></p>
            <ul>
                <li>Urgent & Important: Do first</li>
                <li>Important but Not Urgent: Schedule</li>
                <li>Urgent but Not Important: Delegate</li>
                <li>Neither Urgent nor Important: Eliminate</li>
            </ul>
            <p><em>Perfect for: Prioritization and decision-making</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    with st.sidebar.expander("Time Blocking", expanded=False):
        st.markdown(f"""
        <div class="tip-box">
            <p><strong>Steps:</strong></p>
            <ol>
                <li>Identify your most important tasks</li>
                <li>Allocate specific time blocks to each task</li>
                <li>Group similar activities together</li>
                <li>Include buffer time between blocks</li>
            </ol>
            <p><em>Perfect for: Deep work and optimizing your daily schedule</em></p>
        </div>
        """, unsafe_allow_html=True)