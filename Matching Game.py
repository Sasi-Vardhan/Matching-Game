import streamlit as st
import pandas as pd
import random
import time
from PIL import Image
import io
import base64
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Set page config
st.set_page_config(
    page_title="Match The Following Game",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to improve the UI
st.markdown("""
<style>
    .match-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    .question-box, .answer-box {
        padding: 10px;
        border-radius: 5px;
        margin: 5px;
        min-height: 50px;
        display: flex;
        align-items: center;
    }
    .question-box {
        background-color: #f0f7ff;
        border: 1px solid #4b91ff;
        width: 100%;
    }
    .answer-box {
        background-color: #fff0f0;
        border: 1px solid #ff7c7c;
        width: 100%;
    }
    .match-item {
        font-weight: 500;
    }
    .results {
        margin-top: 20px;
        padding: 15px;
        border-radius: 5px;
        background-color: #f8f9fa;
    }
    .score-display {
        font-size: 24px;
        text-align: center;
        margin: 20px 0;
    }
    .correct {
        color: green;
        font-weight: bold;
    }
    .incorrect {
        color: red;
        text-decoration: line-through;
    }
    .container {
        max-width: 1200px;
        margin: 0 auto;
    }
    .title {
        text-align: center;
        margin-bottom: 20px;
    }
    .instructions {
        margin-bottom: 20px;
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 5px;
    }
    .line-canvas {
        position: relative;
        width: 100%;
        height: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'questions' not in st.session_state:
    st.session_state.questions = [
        {"id": "q1", "text": "Capital of France"},
        {"id": "q2", "text": "Largest planet in our solar system"},
        {"id": "q3", "text": "Element with symbol O"},
        {"id": "q4", "text": "Fastest land animal"},
        {"id": "q5", "text": "Author of 'Romeo and Juliet'"}
    ]

if 'answers' not in st.session_state:
    st.session_state.answers = [
        {"id": "a1", "text": "Paris", "correct_question_id": "q1"},
        {"id": "a2", "text": "Jupiter", "correct_question_id": "q2"},
        {"id": "a3", "text": "Oxygen", "correct_question_id": "q3"},
        {"id": "a4", "text": "Cheetah", "correct_question_id": "q4"},
        {"id": "a5", "text": "William Shakespeare", "correct_question_id": "q5"}
    ]
    random.shuffle(st.session_state.answers)

if 'user_matches' not in st.session_state:
    st.session_state.user_matches = {}

if 'submitted' not in st.session_state:
    st.session_state.submitted = False

if 'score' not in st.session_state:
    st.session_state.score = 0

if 'new_game' not in st.session_state:
    st.session_state.new_game = False

def reset_game():
    st.session_state.user_matches = {}
    st.session_state.submitted = False
    st.session_state.score = 0
    random.shuffle(st.session_state.answers)
    st.session_state.new_game = False

def calculate_score():
    correct_matches = 0
    total_questions = len(st.session_state.questions)
    
    for q_id, a_id in st.session_state.user_matches.items():
        # Find the correct answer for this question
        correct_a_id = None
        for answer in st.session_state.answers:
            if answer['correct_question_id'] == q_id:
                # Get the current answer id
                correct_a_id = answer['id']
                break
        
        if a_id == correct_a_id:
            correct_matches += 1
    
    st.session_state.score = correct_matches
    st.session_state.submitted = True
    
    return correct_matches, total_questions

def create_connection_visualization():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    
    # Turn off axes
    ax.axis('off')
    
    # Position questions on the left
    question_positions = {}
    for i, q in enumerate(st.session_state.questions):
        y_pos = 9 - (i * 2)
        question_positions[q['id']] = (2, y_pos)
        ax.text(1, y_pos, q['text'], ha='right', va='center', fontsize=12)
    
    # Position answers on the right
    answer_positions = {}
    for i, a in enumerate(st.session_state.answers):
        y_pos = 9 - (i * 2)
        answer_positions[a['id']] = (8, y_pos)
        ax.text(9, y_pos, a['text'], ha='left', va='center', fontsize=12)
    
    # Draw connections based on user matches
    for q_id, a_id in st.session_state.user_matches.items():
        if q_id in question_positions and a_id in answer_positions:
            start = question_positions[q_id]
            end = answer_positions[a_id]
            
            # Find correct answer for this question
            correct_a_id = None
            for answer in st.session_state.answers:
                if answer['correct_question_id'] == q_id:
                    correct_a_id = answer['id']
                    break
            
            # Set color based on correctness
            color = 'green' if a_id == correct_a_id else 'red'
            
            ax.annotate('', 
                        xy=end, 
                        xytext=start,
                        arrowprops=dict(arrowstyle='->', lw=2, color=color))
    
    # Save figure to a bytes buffer
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    
    # Return the image as base64 encoded string
    return base64.b64encode(buf.getvalue()).decode()

# Main app
st.markdown("<h1 class='title'>Match The Following Game</h1>", unsafe_allow_html=True)

st.markdown("""
<div class='instructions'>
    <h3>Instructions:</h3>
    <p>Match each question on the left with the correct answer on the right by selecting the corresponding answer from the dropdown menu next to each question.</p>
    <p>When you're done, click 'Submit Answers' to see your score!</p>
</div>
""", unsafe_allow_html=True)

# Create two columns for questions and their dropdown answers
col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3>Questions</h3>", unsafe_allow_html=True)
    for i, question in enumerate(st.session_state.questions):
        st.markdown(f"<div class='question-box'><span class='match-item'>{i+1}. {question['text']}</span></div>", 
                    unsafe_allow_html=True)

with col2:
    st.markdown("<h3>Your Answers</h3>", unsafe_allow_html=True)
    for i, question in enumerate(st.session_state.questions):
        q_id = question['id']
        # Create a list of answers for the dropdown
        answer_options = [{"label": f"{j+1}. {answer['text']}", "value": answer['id']} 
                          for j, answer in enumerate(st.session_state.answers)]
        # Insert an empty option at the beginning
        answer_options.insert(0, {"label": "Select an answer", "value": ""})
        
        # Get the current selection for this question
        current_selection = st.session_state.user_matches.get(q_id, "")
        
        # Create a dropdown for this question
        selected_answer = st.selectbox(
            f"Match for Question {i+1}",
            options=[opt["value"] for opt in answer_options],
            format_func=lambda x: next((opt["label"] for opt in answer_options if opt["value"] == x), ""),
            key=f"dropdown_{q_id}",
            label_visibility="collapsed"
        )
        
        # Update the user_matches dictionary when selection changes
        if selected_answer != current_selection:
            if selected_answer == "":
                if q_id in st.session_state.user_matches:
                    del st.session_state.user_matches[q_id]
            else:
                st.session_state.user_matches[q_id] = selected_answer

# Submit button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    submit_button = st.button("Submit Answers", use_container_width=True, 
                              disabled=len(st.session_state.user_matches) < len(st.session_state.questions) or st.session_state.submitted)

# Display results if submitted
if submit_button or st.session_state.submitted:
    correct_matches, total_questions = calculate_score()
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h2 class='results'>Results</h2>", unsafe_allow_html=True)
    
    # Display score
    percentage = (correct_matches / total_questions) * 100
    st.markdown(
        f"<div class='score-display'>Your Score: <strong>{correct_matches}/{total_questions}</strong> ({percentage:.1f}%)</div>",
        unsafe_allow_html=True
    )
    
    # Generate and display the connection visualization
    viz_base64 = create_connection_visualization()
    st.markdown(f"<div style='text-align: center;'><img src='data:image/png;base64,{viz_base64}' width='800'></div>", unsafe_allow_html=True)
    
    # Display detailed results
    st.markdown("<h3>Detailed Results:</h3>", unsafe_allow_html=True)
    
    for question in st.session_state.questions:
        q_id = question['id']
        q_text = question['text']
        
        selected_a_id = st.session_state.user_matches.get(q_id, None)
        selected_a_text = ""
        for answer in st.session_state.answers:
            if answer['id'] == selected_a_id:
                selected_a_text = answer['text']
                break
        
        # Find the correct answer
        correct_a_text = ""
        for answer in st.session_state.answers:
            if answer['correct_question_id'] == q_id:
                correct_a_text = answer['text']
                break
        
        is_correct = False
        for answer in st.session_state.answers:
            if answer['id'] == selected_a_id and answer['correct_question_id'] == q_id:
                is_correct = True
                break
        
        if is_correct:
            st.markdown(f"""
            <div style='margin-bottom: 10px; padding: 10px; border-left: 4px solid green; background-color: #f0fff0;'>
                <strong>Question:</strong> {q_text}<br>
                <strong>Your answer:</strong> <span class='correct'>{selected_a_text}</span> ✓
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='margin-bottom: 10px; padding: 10px; border-left: 4px solid red; background-color: #fff0f0;'>
                <strong>Question:</strong> {q_text}<br>
                <strong>Your answer:</strong> <span class='incorrect'>{selected_a_text}</span> ✗<br>
                <strong>Correct answer:</strong> {correct_a_text}
            </div>
            """, unsafe_allow_html=True)
    
    # Play again button
    if st.button("Play Again", key="play_again"):
        reset_game()
        st.experimental_rerun()

# Add an admin section to customize questions and answers
st.markdown("<hr>", unsafe_allow_html=True)
with st.expander("Admin: Customize Questions & Answers"):
    st.write("Enter your custom questions and answers below:")
    
    # Number of questions to set
    num_pairs = st.number_input("Number of Question-Answer Pairs", min_value=2, max_value=10, value=5)
    
    custom_questions = []
    custom_answers = []
    
    for i in range(num_pairs):
        cols = st.columns(2)
        with cols[0]:
            q_text = st.text_input(f"Question {i+1}", value=st.session_state.questions[i]['text'] if i < len(st.session_state.questions) else "")
        with cols[1]:
            a_text = st.text_input(f"Answer {i+1}", value=next((a['text'] for a in st.session_state.answers if a['correct_question_id'] == f"q{i+1}"), ""))
        
        if q_text and a_text:
            custom_questions.append({"id": f"q{i+1}", "text": q_text})
            custom_answers.append({"id": f"a{i+1}", "text": a_text, "correct_question_id": f"q{i+1}"})
    
    if st.button("Update Questions & Answers") and len(custom_questions) == num_pairs and len(custom_answers) == num_pairs:
        st.session_state.questions = custom_questions
        st.session_state.answers = custom_answers
        random.shuffle(st.session_state.answers)
        st.session_state.user_matches = {}
        st.session_state.submitted = False
        st.success("Questions and answers updated! The game has been reset.")
        st.experimental_rerun()
