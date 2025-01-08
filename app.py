import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import logging

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# Configure logging for better debugging
logging.basicConfig(level=logging.INFO)

# Fetch OpenAI API key from the environment
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logging.error("OpenAI API key not set. Make sure OPENAI_API_KEY is configured in the environment.")

@app.route('/chat', methods=['POST'])
def chat():
    # Get the user message from the request
    user_message = request.json.get('message', '').strip()

    # Validate the message
    if not user_message:
        logging.warning("Received an empty message.")
        return jsonify({"reply": "Message cannot be empty."}), 400

    try:
        # Log the user message
        logging.info(f"User message: {user_message}")

        # Interact with the OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_message}]
        )

        # Extract the bot's reply
        reply = response.choices[0].message.content
        logging.info(f"Bot reply: {reply}")
        return jsonify({"reply": reply})

    except openai.error.OpenAIError as api_error:
        # Log OpenAI-specific errors
        logging.error(f"OpenAI API error: {api_error}")
        return jsonify({"reply": "There was an error communicating with OpenAI. Please try again later."}), 500

    except Exception as e:
        # Log generic errors
        logging.error(f"Unexpected error: {e}")
        return jsonify({"reply": "Sorry, something went wrong. Please try again later."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
