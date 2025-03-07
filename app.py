import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# Set page config
st.set_page_config(
    page_title="Lifting Tracker",
    page_icon="💪",
    layout="wide"
)

# Constants
EXERCISE_TYPES = {
    "Lower Body": ["Squats", "Deadlifts", "Pause Squats"],
    "Upper Body": ["Curls", "Dips", "Pull-ups", "Triceps", "Farmer Carry"]
}

# Define the file path for the JSON data
DATA_FILE = 'workout_data.json'

# Initialize session state for data storage and form progress
if 'workouts' not in st.session_state:
    st.session_state.workouts = []
if 'show_exercise_details' not in st.session_state:
    st.session_state.show_exercise_details = False
if 'show_set_details' not in st.session_state:
    st.session_state.show_set_details = False
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}
if 'rerun' not in st.session_state:
    st.session_state.rerun = False

def save_workout_data():
    """Save workout data to a JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(st.session_state.workouts, f)

def load_workout_data():
    """Load workout data from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            st.session_state.workouts = json.load(f)

def reset_form():
    """Reset the form state"""
    st.session_state.show_exercise_details = False
    st.session_state.show_set_details = False
    st.session_state.form_data = {}
    st.session_state.rerun = not st.session_state.rerun

def main():
    st.title("💪 Lifting Tracker")
    
    # Load existing data
    load_workout_data()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Add Workout", "View History", "Analytics"])
    
    if page == "Add Workout":
        add_workout_page()
    elif page == "View History":
        view_history_page()
    else:
        analytics_page()

def add_workout_page():
    st.header("Add New Workout")
    
    # First group of fields (always visible)
    st.subheader("Basic Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        user = st.selectbox("Select User", ["Adam", "Asim"], key="user_select")
        if user:
            st.session_state.form_data['user'] = user
    
    with col2:
        date = st.date_input("Select Date", datetime.now(), key="date_select")
        if date:
            st.session_state.form_data['date'] = date
    
    with col3:
        workout_type = st.selectbox("Select Workout Type", list(EXERCISE_TYPES.keys()), key="workout_type_select")
        if workout_type:
            st.session_state.form_data['workout_type'] = workout_type
    
    # Continue button for first section
    first_section_complete = all(key in st.session_state.form_data for key in ['user', 'date', 'workout_type'])
    if first_section_complete:
        if st.button("Continue to Exercise Details"):
            st.session_state.show_exercise_details = True
            st.session_state.rerun = not st.session_state.rerun
    
    # Second group of fields
    if st.session_state.show_exercise_details:
        st.subheader("Exercise Details")
        if 'exercise_count' not in st.session_state:
            st.session_state.exercise_count = 1
        
        # Display input fields for each exercise
        for idx in range(st.session_state.exercise_count):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.selectbox("Select Exercise", 
                             EXERCISE_TYPES[st.session_state.form_data['workout_type']], 
                             key=f"exercise_select_{idx}")
            
            with col2:
                st.number_input("Number of Sets", 
                                min_value=1, 
                                value=3, 
                                key=f"num_sets_input_{idx}")
            
            with col3:
                st.number_input("Target Reps per Set", 
                                min_value=1, 
                                value=10, 
                                key=f"target_reps_input_{idx}")
            
            with col4:
                if st.button("Remove", key=f"remove_exercise_{idx}", on_click=lambda i=idx: remove_exercise(i)):
                    pass
        
        if st.button("Add Exercise", on_click=add_exercise_callback):
            pass
        
        # Continue button for second section
        if st.button("Continue to Set Details"):
            st.session_state.show_set_details = True
            st.session_state.form_data['exercises'] = []
            for idx in range(st.session_state.exercise_count):
                exercise_data = {
                    "exercise": st.session_state[f"exercise_select_{idx}"],
                    "num_sets": st.session_state[f"num_sets_input_{idx}"],
                    "target_reps": st.session_state[f"target_reps_input_{idx}"]
                }
                st.session_state.form_data['exercises'].append(exercise_data)
            st.session_state.rerun = not st.session_state.rerun
    
    # Set details section
    if st.session_state.show_set_details:
        st.subheader("Set Details")
        sets_data = []
        
        for exercise_info in st.session_state.form_data['exercises']:
            exercise = exercise_info['exercise']
            st.write(f"### {exercise}")
            for i in range(exercise_info['num_sets']):
                col1, col2, col3, col4 = st.columns([1, 2, 2, 3])
                
                with col1:
                    st.markdown(f"**Set {i+1}**")
                
                with col2:
                    reps = st.number_input(f"{exercise} Set {i+1} reps", 
                                         min_value=1, 
                                         value=exercise_info['target_reps'], 
                                         key=f"reps_{exercise}_{i}")
                
                with col3:
                    weight = st.number_input(f"{exercise} Weight (kg)", 
                                           min_value=0, 
                                           value=0, 
                                           key=f"weight_{exercise}_{i}")
                
                with col4:
                    notes = st.text_input(f"{exercise} Notes", key=f"notes_{exercise}_{i}")
                
                sets_data.append({
                    "exercise": exercise,
                    "set_number": i + 1,
                    "reps": reps,
                    "weight": f"{weight}kg",
                    "notes": notes
                })
        
        st.session_state.form_data['sets'] = sets_data
        
        # Submit button
        if st.button("Add Workout"):
            for exercise_info in st.session_state.form_data['exercises']:
                exercise = exercise_info['exercise']
                workout_entry = {
                    "user": st.session_state.form_data['user'],
                    "date": st.session_state.form_data['date'].strftime("%Y-%m-%d"),
                    "workout_type": st.session_state.form_data['workout_type'],
                    "exercise": exercise,
                    "target_reps": exercise_info['target_reps'],
                    "sets": [s for s in sets_data if s['exercise'] == exercise],
                    "notes": st.session_state.form_data.get('notes', '')
                }
                st.session_state.workouts.append(workout_entry)
            save_workout_data()
            st.success("Workout added successfully!")
            reset_form()
            st.session_state.rerun = not st.session_state.rerun

def view_history_page():
    st.header("Workout History")
    
    if not st.session_state.workouts:
        st.info("No workouts recorded yet.")
        return
    
    # Aggregate data to show one line per workout
    aggregated_workouts = []
    for index, workout in enumerate(st.session_state.workouts):
        # Find the set with the highest weight
        max_weight_set = max(workout['sets'], key=lambda x: int(x['weight'].replace('kg', '')))
        max_weight = int(max_weight_set['weight'].replace('kg', ''))
        reps_at_max_weight = max_weight_set['reps']
        
        aggregated_workouts.append({
            "index": index,
            "user": workout['user'],
            "date": workout['date'],
            "workout_type": workout['workout_type'],
            "exercise": workout['exercise'],
            "reps_at_max_weight": reps_at_max_weight,
            "max_weight": max_weight
        })
    
    df = pd.DataFrame(aggregated_workouts)
    
    # Add filters
    col1, col2 = st.columns(2)
    with col1:
        selected_user = st.multiselect("Filter by User", df['user'].unique(), default=df['user'].unique())
    with col2:
        selected_exercise = st.multiselect("Filter by Exercise", df['exercise'].unique(), default=df['exercise'].unique())
    
    # Apply filters
    filtered_df = df[
        (df['user'].isin(selected_user)) &
        (df['exercise'].isin(selected_exercise))
    ]
    
    # Display the filtered data
    st.dataframe(filtered_df)
    
    # Edit and remove functionality
    if not filtered_df.empty:
        selected_index = st.selectbox("Select Workout to Edit or Remove", filtered_df['index'])
        if st.button("Edit Workout"):
            edit_workout(selected_index)
        if st.button("Remove Workout"):
            st.session_state.workouts.pop(selected_index)
            save_workout_data()
            st.success("Workout removed successfully!")
            st.session_state.rerun = not st.session_state.rerun

    # Add download button for backup
    st.download_button(
        label="Download Backup",
        data=download_workout_data(),
        file_name='workout_data_backup.json',
        mime='application/json'
    )

    # Add import button for uploading JSON backup
    uploaded_file = st.file_uploader("Upload Backup JSON", type="json")
    if uploaded_file is not None:
        # Read the uploaded file
        uploaded_data = json.load(uploaded_file)
        # Ensure the uploaded data is a list
        if isinstance(uploaded_data, list):
            # Replace the existing data with the uploaded data
            st.session_state.workouts = uploaded_data
            save_workout_data()
            st.success("Backup imported successfully!")
        else:
            st.error("Invalid file format. Please upload a valid JSON backup.")

def edit_workout(index):
    workout = st.session_state.workouts[index]
    st.subheader("Edit Workout")
    
    # Edit form
    user = st.selectbox("Select User", ["Adam", "Asim"], index=["Adam", "Asim"].index(workout['user']))
    date = st.date_input("Select Date", datetime.strptime(workout['date'], "%Y-%m-%d"))
    workout_type = st.selectbox("Select Workout Type", list(EXERCISE_TYPES.keys()), index=list(EXERCISE_TYPES.keys()).index(workout['workout_type']))
    exercise = st.selectbox("Select Exercise", EXERCISE_TYPES[workout_type], index=EXERCISE_TYPES[workout_type].index(workout['exercise']))
    target_reps = st.number_input("Target Reps per Set", min_value=1, value=workout['target_reps'])
    
    # Update sets
    sets_data = []
    for i, set_data in enumerate(workout['sets']):
        col1, col2, col3, col4 = st.columns([1, 2, 2, 3])
        with col1:
            st.markdown(f"**Set {i+1}**")
        with col2:
            reps = st.number_input(f"Set {i+1} reps", min_value=1, value=set_data['reps'], key=f"edit_reps_{i}")
        with col3:
            weight = st.number_input(f"Weight (kg)", min_value=0, value=int(set_data['weight'].replace('kg', '')), key=f"edit_weight_{i}")
        with col4:
            notes = st.text_input(f"Notes", value=set_data['notes'], key=f"edit_notes_{i}")
        sets_data.append({
            "set_number": i + 1,
            "reps": reps,
            "weight": f"{weight}kg",
            "notes": notes
        })
    
    if st.button("Save Changes"):
        st.session_state.workouts[index] = {
            "user": user,
            "date": date.strftime("%Y-%m-%d"),
            "workout_type": workout_type,
            "exercise": exercise,
            "target_reps": target_reps,
            "sets": sets_data,
            "notes": workout.get('notes', '')
        }
        save_workout_data()
        st.success("Workout updated successfully!")
        st.session_state.rerun = not st.session_state.rerun

def analytics_page():
    st.header("Workout Analytics")
    
    if not st.session_state.workouts:
        st.info("No workouts recorded yet.")
        return
    
    # Prepare data for analytics
    analytics_data = []
    for workout in st.session_state.workouts:
        total_reps = sum(set_data['reps'] for set_data in workout['sets'])
        max_weight = max(int(set_data['weight'].replace('kg', '')) for set_data in workout['sets'])
        total_weight_lifted = sum(set_data['reps'] * int(set_data['weight'].replace('kg', '')) for set_data in workout['sets'])
        
        analytics_data.append({
            "date": workout['date'],
            "user": workout['user'],
            "exercise": workout['exercise'],
            "max_weight": max_weight,
            "total_reps": total_reps,
            "total_weight_lifted": total_weight_lifted
        })
    
    df = pd.DataFrame(analytics_data)
    
    # Aggregate data to handle duplicates
    df_aggregated = df.groupby(['date', 'user', 'exercise']).agg({
        "max_weight": "max",
        "total_reps": "sum",
        "total_weight_lifted": "sum"
    }).reset_index()
    
    # User interface for selecting user, exercises, and metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_user = st.selectbox("Select User", df_aggregated['user'].unique())
    with col2:
        selected_exercises = st.multiselect("Select Exercises", df_aggregated['exercise'].unique(), default=df_aggregated['exercise'].unique())
    with col3:
        metric = st.selectbox("Select Metric", ["max_weight", "total_reps", "total_weight_lifted"], format_func=lambda x: x.replace('_', ' ').title())
    
    # Filter data based on user selection
    filtered_df = df_aggregated[(df_aggregated['user'] == selected_user) & (df_aggregated['exercise'].isin(selected_exercises))]
    
    # Plot the line graph
    if not filtered_df.empty:
        st.line_chart(filtered_df.pivot(index='date', columns='exercise', values=metric))
    else:
        st.info("No data available for the selected exercises.")

def format_historical_data():
    # Define the historical data
    historical_data = [
        {
            "date": "2023-03-06",
            "user": "Adam",
            "workout_type": "Lower Body",
            "exercises": [
                {
                    "exercise": "Squats",
                    "sets": [
                        {"reps": 5, "weight": "20kg"},
                        {"reps": 5, "weight": "40kg"},
                        {"reps": 5, "weight": "50kg"},
                        {"reps": 5, "weight": "60kg"},
                        {"reps": 5, "weight": "70kg"},
                        {"reps": 5, "weight": "60kg"},
                        {"reps": 5, "weight": "40kg", "notes": "Pause"}
                    ]
                },
                {
                    "exercise": "Deadlifts",
                    "sets": [
                        {"reps": 5, "weight": "40kg"},
                        {"reps": 5, "weight": "50kg"},
                        {"reps": 5, "weight": "70kg"},
                        {"reps": 5, "weight": "80kg"},
                        {"reps": 5, "weight": "80kg"}
                    ]
                }
            ]
        },
        {
            "date": "2023-03-06",
            "user": "Asim",
            "workout_type": "Lower Body",
            "exercises": [
                {
                    "exercise": "Squats",
                    "sets": [
                        {"reps": 5, "weight": "30kg"},
                        {"reps": 5, "weight": "40kg"},
                        {"reps": 5, "weight": "40kg"},
                        {"reps": 5, "weight": "40kg"},
                        {"reps": 5, "weight": "30kg", "notes": "Pause"}
                    ]
                },
                {
                    "exercise": "Deadlifts",
                    "sets": [
                        {"reps": 5, "weight": "30kg"},
                        {"reps": 5, "weight": "30kg"},
                        {"reps": 5, "weight": "40kg"},
                        {"reps": 5, "weight": "40kg"},
                        {"reps": 5, "weight": "40kg"}
                    ]
                }
            ]
        }
        # Add more entries as needed
    ]
    
    # Print formatted data for review
    for entry in historical_data:
        st.write(entry)

def insert_historical_data():
    pass  # Function is no longer needed after initial insertion

# Ensure the function is not called again
# insert_historical_data()

def add_exercise_callback():
    # Increment exercise count
    st.session_state.exercise_count += 1
    
    # Initialize session state for the new exercise
    idx = st.session_state.exercise_count - 1
    if f"exercise_select_{idx}" not in st.session_state:
        st.session_state[f"exercise_select_{idx}"] = EXERCISE_TYPES[st.session_state.form_data['workout_type']][0]
    if f"num_sets_input_{idx}" not in st.session_state:
        st.session_state[f"num_sets_input_{idx}"] = 3
    if f"target_reps_input_{idx}" not in st.session_state:
        st.session_state[f"target_reps_input_{idx}"] = 10

def remove_exercise(idx):
    st.session_state.exercise_count -= 1
    del st.session_state[f"exercise_select_{idx}"]
    del st.session_state[f"num_sets_input_{idx}"]
    del st.session_state[f"target_reps_input_{idx}"]

def download_workout_data():
    """Prepare workout data for download"""
    return json.dumps(st.session_state.workouts, indent=4)

if __name__ == "__main__":
    main() 