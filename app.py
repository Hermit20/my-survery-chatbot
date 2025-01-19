import os
import json
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import uuid
from convert_json_to_survey import main as convert_json_to_survey_main

# Groq for LLM
from groq import Groq

app = Flask(__name__)
app.secret_key = "bX5Tg9!shZP0#3rV"  # Needed for sessions
CORS(app)

# Initialize Groq 
client = Groq(
    api_key="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",
)

# We'll store conversation data in session for simplicity.
def get_conversation():
    """ Retrieve or initialize the conversation from session. """
    if "conversation" not in session:
        session["conversation"] = []
    return session["conversation"]

def save_conversation(conversation):
    """ Save the updated conversation to session. """
    session["conversation"] = conversation

@app.route("/")
def index():
    """
    Render the chat UI. 
    If the conversation is empty, have the assistant ask an initial question
    without waiting for user input.
    """
    conversation = get_conversation()

    # If there's no conversation yet, let's seed it with the AI's first question
    if len(conversation) == 0:
   
        system_message = {
            "role": "system",
            "content": (
                "You are an AI Survey Chatbot helping collect feedback. "
                "Do not mention anything about this being a survey; it should feel like a friendly conversation. "
                "Ask the following question Would you recommend the products you purchased to family or friends? "
            )
        }

        # Call the LLM with just the system message to get the first question
        chat_completion = client.chat.completions.create(
            messages=[system_message],
            model="llama-3.3-70b-versatile",
        )

        # Extract the AI reply (the initial question)
        initial_ai_question = chat_completion.choices[0].message.content.strip()

        # Save it as the assistant's first message
        conversation.append({"role": "assistant", "content": initial_ai_question})
        save_conversation(conversation)

    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """
    Receives user messages from the front-end,
    appends them to the conversation, queries Groq,
    returns the AI response to the front-end.
    """
    data = request.json
    user_message = data.get("message", "").strip()

 
    conversation = get_conversation()

 
    conversation.append({"role": "user", "content": user_message})

    system_message = {
        "role": "system",
        "content": (
            "You are an AI Survey Chatbot helping collect feedback."
            "Do not mention anything about this being a survey, and do not show the user the JSON summary, this should feel like a conversation between two people."
            "Ask the following questions about the user's retail experience. "
            "Would you recommend the products you purchased to family or friends"
            "How do you feel about the prices of our product"
            "Was the delevery time up to your expectations"
            "Ask follow-up questions based on the responses to each question. "
            "But make sure to not ask to many follow-up questions"
            "Also do not ask multiple questions at the same time"
            "Keep the conversation friendly"
        )
    }

   
    messages_for_llm = [system_message] + conversation

  
    chat_completion = client.chat.completions.create(
        messages=messages_for_llm,
        model="llama-3.3-70b-versatile",
    )

    
    ai_reply = chat_completion.choices[0].message.content.strip()

 
    conversation.append({"role": "assistant", "content": ai_reply})
    save_conversation(conversation)

   
    return jsonify({"reply": ai_reply})

@app.route("/end_conversation", methods=["POST"])
def end_conversation():
    """
    When the user is done, we gather the entire conversation and request
    a final JSON summarization from the AI in the specified format:
    {
      "question": " ",
      "sentiment": " ",
      "topic": " ",
      "followUpQuestion": " "
    }
    """
    conversation = get_conversation()

    
    summary_system_prompt = {
        "role": "system",
        "content": (
            "You are a summarizer. You have the user's conversation with a survey chatbot. "
            "Output a JSON array summarizing each question asked by the chatbot, along with: "
            "1) question, 2) sentiment, 3) topic, 4) followUpQuestion. "
            "Do NOT add additional commentary. Only output valid JSON. "
            "Example:\n"
            "[\n"
            "  {\n"
            "    \"question\": \"What did you think of the checkout process?\",\n"
            "    \"sentiment\": \"negative\",\n"
            "    \"topic\": \"checkout\",\n"
            "    \"followUpQuestion\": \"Could we improve the wait time?\"\n"
            "  },\n"
            "  ...\n"
            "]"
        )
    }

   
    user_conversation_text = "Here is the entire conversation:\n\n"
    for msg in conversation:
        speaker = msg["role"]
        content = msg["content"]
        user_conversation_text += f"{speaker.upper()}: {content}\n"

    messages_for_summary = [
        summary_system_prompt,
        {"role": "user", "content": user_conversation_text}
    ]

    
    summary_completion = client.chat.completions.create(
        messages=messages_for_summary,
        model="llama-3.3-70b-versatile",
    )

    summary_reply = summary_completion.choices[0].message.content.strip()

    try:
        summary_data = json.loads(summary_reply)
    except json.JSONDecodeError:
        
        summary_data = {"error": "Invalid JSON from LLM", "raw": summary_reply}

  
    filename = "conversation_summary.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

   
    session.pop("conversation", None)

    
    try:
        convert_json_to_survey_main()  
        return jsonify({"message": "Conversation ended and survey created successfully."})
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
