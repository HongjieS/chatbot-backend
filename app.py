from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Replace with your Assistant ID
ASSISTANT_ID = "asst_ExmNOH6JnD7u06HMzzKcOeg4"

@app.route("/")
def home():
    return jsonify({"message": "API is running."})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message", "")
        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Create a new thread
        thread = openai.Thread.create()
        thread_id = thread["id"]

        # Add user message to the thread
        openai.Thread.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )

        # Generate a response from the Assistant
        response = openai.Thread.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        # Get the Assistant's reply
        reply = response.get("message", {}).get("content", "I'm not sure how to respond to that.")
        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"reply": "Sorry, something went wrong. Please try again later."}), 500


if __name__ == "__main__":
    app.run(debug=True)
