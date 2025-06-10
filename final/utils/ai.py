import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def initialize_gemini():
    """Initialize the Gemini API with the API key"""
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        return True
    return False

def get_ai_assistant_response(prompt, chat_history=None):
    """Get a response from the AI assistant using Gemini 1.5 Flash
    
    Args:
        prompt (str): The user's question or prompt
        chat_history (list): Optional list of previous chat messages
        
    Returns:
        tuple: (response_text, error_message)
    """
    # Check if API key is configured
    if not GEMINI_API_KEY:
        return None, None, "Gemini API key not configured. Please check your .env file."
    
    try:
        # Initialize the model with gemini-1.5-flash
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Define system prompt to ensure the assistant stays within productivity scope
        system_prompt = """
        You are ZenCoach, a productivity and time management AI assistant within the ZenFlow app.
        
        Guidelines:
        1. Only respond to questions related to productivity, time management, goal setting, habit formation,
           work-life balance, focus techniques, procrastination, and related productivity topics.
        2. For any questions outside this scope, politely redirect the conversation back to productivity.
        3. Provide practical, actionable advice backed by research when possible.
        4. Keep responses concise but thorough, focusing on usable tips.
        5. Be encouraging and supportive, but honest.
        6. Only reference features that actually exist in the ZenFlow app:
           - Tasks: Create and manage tasks with deadlines, reminders, and AI-generated subtasks
           - Focus: Pomodoro timer with customizable work/break durations
           - Vision Board: Visualize goals with customizable themes and layouts
           - AI Assistant: Get productivity advice and guidance
        
        Remember: Your purpose is to help users improve their productivity and achieve their goals.
        Do not mention features that don't exist in the app.
        """
        
        # Create a chat session if there's no history
        if not chat_history:
            chat = model.start_chat(history=[])
            # Add the system prompt as the first message
            chat.send_message(system_prompt)
        else:
            # If chat history exists, reconstruct the chat
            chat = model.start_chat(history=chat_history)
        
        # Send the user's prompt and get response
        response = chat.send_message(prompt)
        
        # Return the response text and the updated chat history
        return response.text, chat.history, None
    
    except Exception as e:
        return None, None, f"Error getting AI response: {str(e)}"

def generate_subtasks(task_name, task_description=None):
    """Generate subtasks for a given task using Gemini AI"""
    # Check if API key is configured
    if not GEMINI_API_KEY:
        return None, "Gemini API key not configured. Please check your .env file."
    
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-flash-8b')
        
        # Create prompt
        description_text = f" Description: {task_description}" if task_description else ""
        prompt = f"""
        Task: {task_name}{description_text}
        
        Break down the task into a logical sequence of clear, specific, and actionable subtasks that can be completed one by one.

        Only include as many subtasks as are reasonably necessary to complete the task effectively — avoid over-explaining trivial actions.
        For simple tasks, return only a few high-level steps.
        For complex tasks, expand with more detailed steps (up to 10).
        Format the output as a numbered list of subtasks only, with no extra explanation.
        Example:
        1. First subtask
        2. Second subtask
        3. Third subtask
        """
        
        # Generate response
        response = model.generate_content(prompt)
        
        # Process response text to extract subtasks
        response_text = response.text.strip()
        
        # Parse the numbered list
        subtasks = []
        for line in response_text.split('\n'):
            line = line.strip()
            # Skip empty lines
            if not line:
                continue
            
            # Try to match numbered format (e.g., "1. Subtask")
            parts = line.split('. ', 1)
            if len(parts) == 2 and parts[0].isdigit():
                subtask = parts[1].strip()
                if subtask:
                    subtasks.append(subtask)
            else:
                # Include lines that don't match the numbered format
                subtasks.append(line)
        
        return subtasks, None
    except Exception as e:
        return None, f"Error generating subtasks: {str(e)}"

def generate_action_plan(task_name, task_description=None, subtasks=None):
    """Generate a detailed action plan for a task using Gemini AI"""
    # Check if API key is configured
    if not GEMINI_API_KEY:
        return None, "Gemini API key not configured. Please check your .env file."
    
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-flash-8b')
        
        # Create prompt with subtasks if available
        subtasks_text = ""
        if subtasks and len(subtasks) > 0:
            subtasks_text = "Current subtasks:\n" + "\n".join([f"- {subtask}" for subtask in subtasks])
        
        description_text = f" Description: {task_description}" if task_description else ""
        prompt = f"""
        Task: {task_name}{description_text}
        
        {subtasks_text}
        
        Create a comprehensive action plan for completing this task successfully.
        Include the following sections:
        1. Overview - A brief summary of the approach
        2. Resources Needed - What tools, materials, or information will be required
        3. Step-by-Step Approach - Detailed steps to complete the task
        4. Potential Challenges - What obstacles might arise and how to overcome them
        5. Timeline - Estimated time required for completion
        
        Keep the plan concise but thorough.
        """
        
        # Generate response
        response = model.generate_content(prompt)
        
        return response.text.strip(), None
    except Exception as e:
        return None, f"Error generating action plan: {str(e)}"
