# Survey Chatbot

The Survey Chatbot is designed to facilitate interactive surveys by engaging users in conversational dialogues. 
Built with Python, it leverages natural language processing to enhance user experience during data collection.

## Features

- **Conversational Surveys**: Engages users through dynamic dialogues to collect survey responses.
- **Sentiment Analysis**: Compiles and summarizes conversation data for into diffrent sentiments such as Positive Negative and Neutral. And then stores this data on a Surevy Monkey Survey using thier API

## Project Structure

- `app.py`: Main application file that runs the chatbot.
- `conversation_summary.json`: Stores summaries of user conversations.
- `convert_json_to_survey.py`: Utility script to transform JSON data into survey formats, using SurveyMonkeys API.
- `templates/`: Contains HTML and CSS code for the chatbot interface.
- `static/`: Holds and image file for the SurveyMoney Logo and JavaScript code.

## Requirements

- Python 3.x
- Flask
- Additional dependencies listed in `requirements.txt`

## To Run

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Hermit20/my-survery-chatbot.git

2. **Navigate to the project directory**
   cd my-survery-chatbot
   
3. **Install dependencies**
   pip install -r requirements.txt

4. **Run the application**
   python app.py

5. **Access the chatbot**
   Open your web browser and navigate to http://localhost:5000


**Contributing**
Contributions are welcome! Please fork the repository and create a pull request with your proposed changes.
