# [Previous imports remain the same...]

def yes_no_buttons(key, question, pre_answered=False):
    """Create horizontal yes/no buttons with green background if pre-answered"""
    col1, col2, col3 = st.columns([10, 1, 1])
    
    with col1:
        if pre_answered:
            st.markdown(f'<div style="background-color: #d4edda; padding: 10px; border-radius: 5px;">{question}</div>', unsafe_allow_html=True)
        else:
            st.write(question)
    
    with col2:
        yes_button = st.button('Yes', key=f'{key}_yes')
        if yes_button:
            st.session_state.answers[key] = 'y'
    
    with col3:
        no_button = st.button('No', key=f'{key}_no')
        if no_button:
            st.session_state.answers[key] = 'n'
    
    # Show current selection
    if key in st.session_state.answers:
        st.write(f"Selected: {'Yes' if st.session_state.answers[key] == 'y' else 'No'}")

def frequency_buttons(key, question, options, pre_answered=False):
    """Create horizontal frequency buttons"""
    col1, *option_cols = st.columns([10] + [1] * len(options))
    
    with col1:
        if pre_answered:
            st.markdown(f'<div style="background-color: #d4edda; padding: 10px; border-radius: 5px;">{question}</div>', unsafe_allow_html=True)
        else:
            st.write(question)
    
    for option, col in zip(options, option_cols):
        with col:
            if st.button(option, key=f'{key}_{option}'):
                st.session_state.answers[key] = option
    
    # Show current selection
    if key in st.session_state.answers:
        st.write(f"Selected: {st.session_state.answers[key]}")

# [Previous function definitions remain the same until the questions screen...]

# Questions screen
elif st.session_state.current_step == 'questions':
    st.title("Course Information")
    
    for section, q_range in sections.items():
        st.header(f"Section {section}")
        for i in q_range:
            q_key = f'Q{i}'
            pre_answered = q_key in st.session_state.answers and st.session_state.answers[q_key] != ""
            
            if i in [21, 22]:  # Percentage questions
                col1, col2 = st.columns([10, 2])
                with col1:
                    if pre_answered:
                        st.markdown(f'<div style="background-color: #d4edda; padding: 10px; border-radius: 5px;">{QUESTIONS[q_key]}</div>', unsafe_allow_html=True)
                    else:
                        st.write(QUESTIONS[q_key])
                with col2:
                    st.session_state.answers[q_key] = st.number_input(
                        "",
                        0, 100,
                        value=int(st.session_state.answers[q_key]) if st.session_state.answers[q_key] else 0,
                        key=q_key
                    )
            
            elif i == 23:  # Duration question
                col1, col2 = st.columns([10, 2])
                with col1:
                    if pre_answered:
                        st.markdown(f'<div style="background-color: #d4edda; padding: 10px; border-radius: 5px;">{QUESTIONS[q_key]}</div>', unsafe_allow_html=True)
                    else:
                        st.write(QUESTIONS[q_key])
                with col2:
                    st.session_state.answers[q_key] = st.number_input(
                        "",
                        0, 180,
                        value=int(st.session_state.answers[q_key]) if st.session_state.answers[q_key] else 0,
                        key=q_key
                    )
            
            elif i in [24, 26, 27, 28]:  # Frequency questions
                frequency_buttons(
                    q_key,
                    QUESTIONS[q_key],
                    ['every class', 'every week', 'once in a while', 'rarely'],
                    pre_answered
                )
            
            elif i == 44:  # Often/sometimes/rarely question
                frequency_buttons(
                    q_key,
                    QUESTIONS[q_key],
                    ['often', 'sometimes', 'rarely'],
                    pre_answered
                )
            
            else:  # Yes/No questions
                yes_no_buttons(q_key, QUESTIONS[q_key], pre_answered)
        
        st.markdown("---")

    if st.button("Submit"):
        # [Submit handling remains the same...]

# [Rest of the code remains the same...]