# Restaurant Feedback Analysis Dashboard

A powerful Streamlit-based dashboard that uses AI agents to analyze restaurant customer feedback and provide actionable insights. The application combines data visualization with AI-powered analysis to help restaurants understand customer satisfaction and identify areas for improvement.

## Features

- 📊 Interactive data visualization with Plotly
- 🤖 AI-powered analysis using CrewAI and Ollama
- 📈 Real-time feedback analysis
- 🏪 Restaurant-specific insights
- 📱 Responsive and user-friendly interface
- 🔍 Detailed question-wise analysis

## Prerequisites

- Python 3.8 or higher
- MySQL database
- Ollama installed locally (for AI analysis)
- Required Python packages (listed in requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/restaurant-feedback.git
cd restaurant-feedback
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
Create a `.env` file in the project root with the following variables:
```
DB_HOST=your_mysql_host
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=your_database_name
```

5. **Set up Ollama:**

    * Download and install Ollama from https://ollama.ai
    * Run Ollama server
    * Pull the required LLM.

## Database Setup

1. Create a MySQL database
   1. Create Database ```restaurant_feedback```
   2. create tables
      ```
        answers    
         feedback                      
        questions                     
         restaurants                  
         users   
      ```
   3. for users table
      ```sql
       CREATE TABLE users (
       user_id INT AUTO_INCREMENT PRIMARY KEY,
       name VARCHAR(255) NOT NULL,
       email VARCHAR(255) UNIQUE NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
      ```
   4. for restaurants table
      ```sql
      CREATE TABLE restaurants (
       restaurant_id INT AUTO_INCREMENT PRIMARY KEY,
       name VARCHAR(255) NOT NULL,
       location VARCHAR(255),
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
      ```
   5. for questions table
      ```sql
         CREATE TABLE questions (
       question_id INT AUTO_INCREMENT PRIMARY KEY,
       question_text TEXT NOT NULL
         );
      ```
   6. for feedback table
      ```sql
      CREATE TABLE feedback (
       feedback_id INT AUTO_INCREMENT PRIMARY KEY,
       user_id INT,
       restaurant_id INT,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (user_id) REFERENCES users(user_id),
       FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
         );
      ```
   7. for answer table
      ```sql
         CREATE TABLE answers (
       answer_id INT AUTO_INCREMENT PRIMARY KEY,
      feedback_id INT,
       question_id INT,
       answer_text TINYINT(1) NOT NULL DEFAULT 0,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (feedback_id) REFERENCES feedback(feedback_id),
       FOREIGN KEY (question_id) REFERENCES questions(question_id)
         );
      ```
    
2. Run the following SQL to create the required table:
```sql
CREATE TABLE restaurant_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant VARCHAR(255),
    question VARCHAR(255),
    answer VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run streamlit_app.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Use the sidebar filters to select specific restaurants for analysis

4. Click "Run AI Analysis" to generate AI-powered insights

## Features in Detail

### Data Visualization
- Overall satisfaction rate by restaurant
- Response distribution charts
- Question-wise analysis with pie charts
- Interactive data tables

### AI Analysis
- Restaurant-specific analysis including:
  - Positive aspects
  - Negative aspects
  - Key areas for improvement
- Actionable recommendations based on customer feedback

### Data Management
- Real-time data loading from MySQL database
- Cached data for improved performance
- Error handling for database connection issues

## Project Structure

```
restaurant-feedback/
├── streamlit_app.py      # Main Streamlit application
├── restaurant_feedback.py # Database and data processing functions
├── requirements.txt      # Python package dependencies
├── .env                 # Environment variables
└── README.md           # Project documentation
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Streamlit for the amazing dashboard framework
- CrewAI for the AI agent implementation
- Ollama for providing local LLM capabilities
- Plotly for interactive visualizations

## Support

For support, please open an issue in the GitHub repository or contact the maintainers. 
