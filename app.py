from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = "asst_EXmNOH6JnD7u06HMzrKc0eg4"  # Replace with your Assistant ID
OPENAI_API_URL = "https://api.openai.com/v1"

# Headers for OpenAI API with Assistants v2
HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json",
    "OpenAI-Beta": "assistants=v2",
}

@app.route("/")
def home():
    return jsonify({"message": "API is running."})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message", "")
        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Step 1: Create a thread
        thread_response = requests.post(f"{OPENAI_API_URL}/threads", headers=HEADERS)
        if thread_response.status_code != 200:
            print("Thread creation failed:", thread_response.json())
            return jsonify({"error": "Failed to create thread"}), 500

        thread_id = thread_response.json().get("id")
        if not thread_id:
            print("Thread ID missing in response:", thread_response.json())
            return jsonify({"error": "Invalid thread creation response"}), 500

        # Step 2: Add user message to the thread
        message_payload = {
            "role": "user",
            "content": user_message,
        }
        message_response = requests.post(
            f"{OPENAI_API_URL}/threads/{thread_id}/messages",
            headers=HEADERS,
            json=message_payload,
        )
        if message_response.status_code != 200:
            print("Message addition failed:", message_response.json())
            return jsonify({"error": "Failed to add message to thread"}), 500

        # Step 3: Run the assistant on the thread
        run_payload = {
            "assistant_id": ASSISTANT_ID,
        }
        run_response = requests.post(
            f"{OPENAI_API_URL}/threads/{thread_id}/runs",
            headers=HEADERS,
            json=run_payload,
        )
        if run_response.status_code != 200:
            print("Run failed:", run_response.json())
            return jsonify({"error": "Failed to run assistant"}), 500

        # Log the run response
        print("Run Response:", run_response.json())

        # Extract the Assistant's reply
        reply = run_response.json().get("message", {}).get("content", "No response from assistant.")
        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"reply": "Sorry, something went wrong. Please try again later."}), 500



if __name__ == "__main__":
    app.run(debug=True)
