import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# -------------------------------
# 1. REQUIRED CONFIG
# -------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Must be set in your Render environment
ASSISTANT_ID = "asst_EXmNOH6JnD7u06HMzrKc0eg4"  # The Assistant you created in Beta
BASE_URL = "https://api.openai.com/v1"

# The required Beta header
HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json",
    "OpenAI-Beta": "assistants=v2",
}

# In-memory store of session_id -> thread_id mapping
SESSION_THREADS = {}

@app.route("/")
def home():
    return jsonify({"message": "Beta Assistants API is running!"})

@app.route("/chat", methods=["POST"])
def chat():
    """
    1. If no thread exists for session_id, create a new one.
    2. Add the user's message to the thread.
    3. Run the assistant to get a reply.
    4. Return the reply.
    """
    try:
        data = request.json or {}
        user_message = data.get("message")
        session_id = data.get("session_id", "default")

        if not user_message:
            return jsonify({"error": "No message provided."}), 400

        # -- (A) CREATE THREAD IF NEEDED --
        if session_id not in SESSION_THREADS:
            thread_endpoint = f"{BASE_URL}/assistants/{ASSISTANT_ID}/threads"
            create_resp = requests.post(thread_endpoint, headers=HEADERS, json={})

            # Print debug info so you can see what happened
            print("\n[DEBUG] CREATE THREAD response:", create_resp.status_code, create_resp.text)

            if create_resp.status_code != 200:
                return jsonify({"error": f"Failed to create thread: {create_resp.text}"}), 500

            thread_id = create_resp.json().get("id")
            SESSION_THREADS[session_id] = thread_id
        else:
            thread_id = SESSION_THREADS[session_id]

        # -- (B) ADD USER MESSAGE --
        message_endpoint = f"{BASE_URL}/assistants/{ASSISTANT_ID}/threads/{thread_id}/messages"
        msg_payload = {"role": "user", "content": user_message}
        msg_resp = requests.post(message_endpoint, headers=HEADERS, json=msg_payload)

        print("[DEBUG] ADD MESSAGE response:", msg_resp.status_code, msg_resp.text)

        if msg_resp.status_code != 200:
            return jsonify({"error": f"Failed to add message: {msg_resp.text}"}), 500

        # -- (C) RUN THE ASSISTANT --
        run_endpoint = f"{BASE_URL}/assistants/{ASSISTANT_ID}/threads/{thread_id}/runs"
        run_resp = requests.post(run_endpoint, headers=HEADERS, json={})

        print("[DEBUG] RUN ASSISTANT response:", run_resp.status_code, run_resp.text)

        if run_resp.status_code != 200:
            return jsonify({"error": f"Failed to run assistant: {run_resp.text}"}), 500

        # The assistant's reply is typically found at run_resp.json()["message"]["content"]
        result_json = run_resp.json()
        assistant_message = result_json.get("message", {}).get("content", "No response from assistant.")

        # Return that message to the frontend
        return jsonify({"reply": assistant_message})

    except Exception as e:
        print("[ERROR]", e)
        return jsonify({"error": "An unexpected error occurred on the server."}), 500


if __name__ == "__main__":
    app.run(debug=True)  # Turn off debug in production
