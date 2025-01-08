from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

# Load OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def home():
    return jsonify({"message": "API is running."})  # Simple JSON response for root route

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message", "")
        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        print(f"User Message: {user_message}")

        # OpenAI GPT request
        response = openai.ChatCompletion.create(
            model="asst_EXmNOH6JnD7u06HMzrKc0eg4",  # Replace with a valid model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ]
        )

        # Extract reply
        reply = response.get("choices", [{}])[0].get("message", {}).get("content", "I'm not sure how to respond to that.")
        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"reply": "Sorry, something went wrong. Please try again later."}), 500


if __name__ == "__main__":
    app.run(debug=True)
