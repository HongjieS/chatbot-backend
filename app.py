from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# 1. OpenAI Beta Assistants endpoints
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Replace with your actual Assistant ID from the Beta Assistants dashboard
ASSISTANT_ID = "asst_EXmNOH6JnD7u06HMzrKc0eg4"
OPENAI_API_URL = "https://api.openai.com/v1"

# 2. Include the Beta header. Note the "assistants=v2"
HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json",
    "OpenAI-Beta": "assistants=v2",
}

# 3. In-memory store for session -> thread mapping.
#    In production, use a database or Redis.
SESSION_THREADS = {}

@app.route("/")
def home():
    return jsonify({"message": "API is running with Beta Assistants."})

@app.route("/chat", methods=["POST"])
def chat():
    """
    1) Checks if there's an existing thread for this session.
       If not, create a new thread: POST /assistants/{assistant_id}/threads
    2) Add the user's message: POST /assistants/{assistant_id}/threads/{thread_id}/messages
    3) Run the assistant: POST /assistants/{assistant_id}/threads/{thread_id}/runs
    4) Return the assistant's reply to the frontend.
    """
    try:
        data = request.json
        user_message = data.get("message")
        session_id = data.get("session_id", "default")

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # 1) If no thread exists, create one
        if session_id not in SESSION_THREADS:
            thread_url = f"{OPENAI_API_URL}/assistants/{ASSISTANT_ID}/threads"
            create_thread_resp = requests.post(thread_url, headers=HEADERS, json={})
            if create_thread_resp.status_code != 200:
                return jsonify({"error": "Failed to create thread"}), 500
            thread_id = create_thread_resp.json().get("id")
            SESSION_THREADS[session_id] = thread_id
        else:
            thread_id = SESSION_THREADS[session_id]

        # 2) Add user’s message to the thread
        message_url = f"{OPENAI_API_URL}/assistants/{ASSISTANT_ID}/threads/{thread_id}/messages"
        message_payload = {
            "role": "user",
            "content": user_message
        }
        message_resp = requests.post(message_url, headers=HEADERS, json=message_payload)
        if message_resp.status_code != 200:
            return jsonify({"error": "Failed to add message to thread"}), 500

        # 3) Run the assistant
        run_url = f"{OPENAI_API_URL}/assistants/{ASSISTANT_ID}/threads/{thread_id}/runs"
        run_resp = requests.post(run_url, headers=HEADERS, json={})
        if run_resp.status_code != 200:
            return jsonify({"error": "Failed to run assistant"}), 500

        # 4) Extract the assistant's reply from the response
        result_json = run_resp.json()
        # The assistant’s message is typically found in result_json["message"]["content"]
        assistant_reply = (
            result_json.get("message", {}).get("content", "No response from assistant.")
        )

        return jsonify({"reply": assistant_reply})

    except Exception as e:
        print(f"Error occurred: {e}")
        return (
            jsonify({"reply": "Sorry, something went wrong. Please try again later."}),
            500,
        )


if __name__ == "__main__":
    # In production, set debug=False
    app.run(debug=True)
