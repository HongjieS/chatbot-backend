from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

# Load OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def index():
    return render_template("index.html")  # Ensure this HTML file exists in the 'templates' folder

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message", "")
        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        print(f"User Message: {user_message}")

        # Attempt to use the preferred model
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",  # Ensure this model exists in OpenAI API
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_message}
                ]
            )
        except openai.error.InvalidRequestError as e:
            print(f"Model gpt-4o-mini failed: {e}")
            # Fallback to gpt-4
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_message}
                ]
            )

        # Extract the bot's reply
        reply = response.get("choices", [{}])[0].get("message", {}).get("content", "I'm not sure how to respond to that.")
        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"reply": "Sorry, something went wrong. Please try again later."}), 500

if __name__ == "__main__":
    app.run(debug=True)
