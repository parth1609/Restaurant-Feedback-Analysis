import mysql.connector
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_restaurant_feedback():
    """Connect to MySQL and fetch restaurant feedback data"""
    try:
        # Get database credentials from environment variables
        host = os.getenv('MYSQL_HOST', 'localhost')
        user = os.getenv('MYSQL_USER', 'root')
        password = os.getenv('MYSQL_PASSWORD', 'lottie@qwer_908')  # Default password from your setup
        database = os.getenv('MYSQL_DATABASE', 'restaurant_feedback')
        
        print(f"Attempting to connect to database with host: {host}, user: {user}, database: {database}")
        
        # Establish connection to your MySQL database
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        print("Successfully connected to the database")
        
        # Create a cursor object
        cursor = conn.cursor()
        
        # Execute the query
        query = """
            select
            r.name as restaurant_name,
            q.question_text,
            a.answer_text
        from
            users u
        join
            feedback f on u.user_id = f.user_id
        join
            restaurants r on f.restaurant_id = r.restaurant_id
        join 
            answers a on f.feedback_id = a.feedback_id
        join
            questions q on a.question_id = q.question_id;
        """
        cursor.execute(query)
        
        # Fetch all rows
        feedback_data = cursor.fetchall()
        print(f"Retrieved {len(feedback_data)} rows of feedback data")
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        return feedback_data
        
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        print(f"Error Code: {err.errno}")
        print(f"SQL State: {err.sqlstate}")
        return []
    except Exception as e:
        print(f"General Error: {e}")
        print(f"Error Type: {type(e)}")
        return []

def convert_to_dataframe(feedback_data):
    """Convert raw feedback data to a structured DataFrame"""
    if not feedback_data:
        print("No feedback data received from database")
        # Create a sample DataFrame with the expected structure
        return pd.DataFrame({
            "Restaurant": ["Sadhana", "OYO"],
            "Question": [
                "Did the food meet your expectations in terms of taste, quality and presentation?",
                "Did you receive value for the money spent?"
            ],
            "Answer": ["No", "Yes"]
        })
        
    print(f"Converting {len(feedback_data)} rows of feedback data to DataFrame")
    
    # Create lists to store the data
    restaurants = []
    questions = []
    answers = []
    
    # Extract data from tuples
    for row in feedback_data:
        restaurant_name, question, answer = row
        restaurants.append(restaurant_name)
        questions.append(question)
        answers.append("Yes" if answer == 1 else "No")
    
    # Create DataFrame
    df = pd.DataFrame({
        "Restaurant": restaurants,
        "Question": questions,
        "Answer": answers
    })
    
    print(f"Created DataFrame with shape: {df.shape}")
    return df

def create_pivot_table(df):
    """Create a pivot table to show all questions and answers by restaurant"""
    if df.empty:
        print("Empty DataFrame received for pivot table creation")
        return pd.DataFrame()
        
    # Create a pivot table with restaurants as rows and questions as columns
    pivot_df = df.pivot_table(
        index="Restaurant",
        columns="Question",
        values="Answer",
        aggfunc=lambda x: ', '.join(x)
    )
    
    return pivot_df

def create_summary(df):
    """Create a summary of feedback by restaurant"""
    if df.empty:
        print("Empty DataFrame received for summary creation")
        return pd.DataFrame()
        
    # Group by restaurant and calculate metrics
    summary = df.groupby("Restaurant").agg(
        Total_Questions=("Question", "count"),
        Positive_Responses=("Answer", lambda x: (x == "Yes").sum()),
        Negative_Responses=("Answer", lambda x: (x == "No").sum())
    )
    
    # Calculate percentage of positive responses
    summary["Positive_Percentage"] = (summary["Positive_Responses"] / summary["Total_Questions"]) * 100
    
    return summary 