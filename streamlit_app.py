import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from crewai import Agent, Task, Crew, Process
from langchain_community.llms import Ollama
from restaurant_feedback import get_restaurant_feedback, convert_to_dataframe, create_pivot_table, create_summary
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Restaurant Feedback Analysis Dashboard",
    page_icon="🍽️",
    layout="wide"
)

# Add custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🍽️ Restaurant Feedback Analysis Dashboard")
st.markdown("""
    This dashboard uses AI agents to analyze customer feedback for different restaurants.
    Get detailed insights and recommendations based on customer responses.
""")

# Load data
@st.cache_data
def load_data():
    try:
        feedback_data = get_restaurant_feedback()
        df = convert_to_dataframe(feedback_data)
        pivot = create_pivot_table(df)
        summary = create_summary(df)
        return df, pivot, summary
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        # Return empty DataFrames with correct structure
        return pd.DataFrame(columns=["Restaurant", "Question", "Answer"]), pd.DataFrame(), pd.DataFrame()

# Create AI Agents
def create_agents():
    # Initialize the Ollama LLM
    llm = Ollama(
        model="qwen2.5-coder:14b",  # or any other model you have pulled in Ollama
        temperature=0.7,
        base_url="http://localhost:11434"
    )
    
    # Create Data Analyst Agent
    data_analyst = Agent(
        role='Data Analyst',
        goal='Analyze restaurant feedback data and identify key patterns and trends',
        backstory="""You are an expert data analyst with years of experience in 
        analyzing customer feedback and satisfaction metrics. You excel at identifying 
        patterns and providing actionable insights.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    # Create Business Consultant Agent
    business_consultant = Agent(
        role='Business Consultant',
        goal='Provide strategic recommendations based on customer feedback analysis',
        backstory="""You are a seasoned business consultant specializing in 
        restaurant operations and customer experience. You help businesses improve 
        their performance based on data-driven insights.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    return data_analyst, business_consultant

# Create analysis tasks
def create_tasks(data_analyst, business_consultant, df, summary):
    # Task 1: Data Analysis
    analysis_task = Task(
        description=f"""
        Analyze the following restaurant feedback data and provide a detailed text report for each restaurant.
        For each restaurant, include:
        1. Restaurant name
        2. Positive aspects based on customer responses
        3. Negative aspects based on customer responses
        4. Key areas for improvement based on specific customer feedback
        
        Data to analyze:
        Summary Statistics:
        {summary.to_string()}
        
        Detailed Feedback:
        {df.to_string()}
        
        Format your response as a clear, readable text report with sections for each restaurant.
        Focus on specific customer feedback and responses to provide actionable insights.
        """,
        expected_output="A detailed text report analyzing each restaurant's feedback, highlighting positives, negatives, and improvement areas based on customer responses.",
        agent=data_analyst
    )
    
    # Task 2: Recommendations
    recommendation_task = Task(
        description=f"""
        Based on the data analysis, provide specific, actionable recommendations for each restaurant.
        For each restaurant, include:
        1. Restaurant name
        2. Immediate actions to address negative feedback
        3. Strategies to maintain and enhance positive aspects
        4. Specific improvements based on customer responses
        
        Data to analyze:
        Summary Statistics:
        {summary.to_string()}
        
        Detailed Feedback:
        {df.to_string()}
        
        Format your response as a clear, actionable text report with specific recommendations for each restaurant.
        Focus on practical steps that can be implemented based on customer feedback.
        """,
        expected_output="A detailed text report with specific, actionable recommendations for each restaurant based on customer feedback analysis.",
        agent=business_consultant
    )
    
    return analysis_task, recommendation_task

try:
    # Load data
    df, pivot, summary = load_data()
    
    if df.empty:
        st.warning("No data available. Please check your database connection.")
    else:
        # Sidebar filters
        st.sidebar.header("Filters")
        selected_restaurants = st.sidebar.multiselect(
            "Select Restaurants",
            options=df['Restaurant'].unique(),
            default=df['Restaurant'].unique()
        )
        
        # Filter data based on selection
        filtered_df = df[df['Restaurant'].isin(selected_restaurants)]
        filtered_pivot = pivot[pivot.index.isin(selected_restaurants)]
        filtered_summary = summary[summary.index.isin(selected_restaurants)]
        
        # Main content
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Overall Satisfaction Rate")
            fig = px.bar(
                filtered_summary,
                y=filtered_summary.index,
                x='Positive_Percentage',
                orientation='h',
                title='Positive Response Rate by Restaurant',
                labels={'Positive_Percentage': 'Positive Response Rate (%)'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Response Distribution")
            fig = go.Figure()
            for restaurant in filtered_summary.index:
                fig.add_trace(go.Bar(
                    name=restaurant,
                    x=['Positive', 'Negative'],
                    y=[
                        filtered_summary.loc[restaurant, 'Positive_Responses'],
                        filtered_summary.loc[restaurant, 'Negative_Responses']
                    ]
                ))
            fig.update_layout(
                title='Response Distribution by Restaurant',
                barmode='group',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Feedback Summary")
            st.dataframe(filtered_summary)
            
            st.subheader("Detailed Feedback")
            st.dataframe(filtered_pivot)
        
        # AI Analysis Section
        st.subheader("🤖 AI-Powered Analysis")
        
        if st.button("Run AI Analysis"):
            with st.spinner("AI agents are analyzing the feedback data..."):
                try:
                    # Create agents and tasks
                    data_analyst, business_consultant = create_agents()
                    analysis_task, recommendation_task = create_tasks(
                        data_analyst, business_consultant, filtered_df, filtered_summary
                    )
                    
                    # Create and run the crew
                    crew = Crew(
                        agents=[data_analyst, business_consultant],
                        tasks=[analysis_task, recommendation_task],
                        verbose=True,
                        process=Process.sequential
                    )
                    
                    # Get results
                    result = crew.kickoff()
                    
                    # Display results
                    st.markdown("### Analysis Results")
                    st.write(result)
                except Exception as e:
                    st.error(f"Error during AI analysis: {str(e)}")
                    st.info("Please make sure Ollama is running locally and the model is available.")
        
        # Question-wise analysis
        st.subheader("Question-wise Analysis")
        selected_question = st.selectbox(
            "Select a Question",
            options=filtered_pivot.columns
        )
        
        question_data = filtered_df[filtered_df['Question'] == selected_question]
        fig = px.pie(
            question_data,
            names='Answer',
            title=f'Response Distribution for: {selected_question}',
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please check if the database connection is working properly.") 