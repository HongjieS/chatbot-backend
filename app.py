from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# OpenAI API setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = "asst_EXmNOH6JnD7u06HMzrKc0eg4"  # Replace with your assistant ID
OPENAI_API_URL = "https://api.openai.com/v1"

HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json",
    "OpenAI-Beta": "assistants=v2",
}

# Store session threads (Use Redis or database for production)
SESSION_THREADS = {}

@app.route("/")
def home():
    return jsonify({"message": "API is running."})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        # Extract user message and session ID
        data = request.json
        user_message = data.get("message")
        session_id = data.get("session_id", "default")

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Check if thread exists for the session
        if session_id not in SESSION_THREADS:
            thread_response = requests.post(f"{OPENAI_API_URL}/threads", headers=HEADERS)
            if thread_response.status_code != 200:
                return jsonify({"error": "Failed to create thread"}), 500
            thread_id = thread_response.json().get("id")
            SESSION_THREADS[session_id] = thread_id
        else:
            thread_id = SESSION_THREADS[session_id]

        # Add the user message to the thread
        message_payload = {"role": "user", "content": user_message}
        message_response = requests.post(
            f"{OPENAI_API_URL}/threads/{thread_id}/messages",
            headers=HEADERS,
            json=message_payload,
        )
        if message_response.status_code != 200:
            return jsonify({"error": "Failed to add message to thread"}), 500

        # Run the assistant
        run_payload = {"assistant_id": ASSISTANT_ID}
        run_response = requests.post(
            f"{OPENAI_API_URL}/threads/{thread_id}/runs",
            headers=HEADERS,
            json=run_payload,
        )
        if run_response.status_code != 200:
            return jsonify({"error": "Failed to run assistant"}), 500

        # Extract and return the assistant's reply
        reply = run_response.json().get("message", {}).get("content", "No response from assistant.")
        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"reply": "Sorry, something went wrong. Please try again later."}), 500


if __name__ == "__main__":
    app.run(debug=True)
