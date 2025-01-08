from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("The OpenAI API key is not set in the environment variable 'OPENAI_API_KEY'.")

ASSISTANT_ID = "asst_ExmNOH6JnD7u06HMzzKcOeg4"  # Replace with your Assistant ID
OPENAI_API_URL = "https://api.openai.com/v1"

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
        # Step 1: Get and validate the user's input
        user_message = request.json.get("message", "").strip()
        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Step 2: Create a thread
        thread_response = requests.post(f"{OPENAI_API_URL}/threads", headers=HEADERS)
        if thread_response.status_code != 200:
            return jsonify({
                "error": "Failed to create thread",
                "details": thread_response.json()
            }), thread_response.status_code

        thread_id = thread_response.json().get("id")
        if not thread_id:
            return jsonify({"error": "Thread ID missing in response"}), 500

        # Step 3: Add user message to the thread
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
            return jsonify({
                "error": "Failed to add message to thread",
                "details": message_response.json()
            }), message_response.status_code

        # Step 4: Run the assistant on the thread
        run_payload = {
            "assistant_id": ASSISTANT_ID,
        }
        run_response = requests.post(
            f"{OPENAI_API_URL}/threads/{thread_id}/runs",
            headers=HEADERS,
            json=run_payload,
        )
        if run_response.status_code != 200:
            return jsonify({
                "error": "Failed to run assistant",
                "details": run_response.json()
            }), run_response.status_code

        # Step 5: Extract the Assistant's reply
        reply_message = run_response.json().get("results", [{}])[0].get("message", {}).get("content")
        if not reply_message:
            return jsonify({"reply": "Sorry, I don't have a response at the moment."})

        return jsonify({"reply": reply_message})

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"reply": "Sorry, something went wrong. Please try again later."}), 500


if __name__ == "__main__":
    app.run(debug=True)
