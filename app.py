import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)

# Fetch OpenAI API key from the environment
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message", "")
        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        print(f"User Message: {user_message}")

        # OpenAI API Request
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"User: {user_message}\nAI:",
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )

        print(f"OpenAI Response: {response}")

        # Extract reply
        reply = response.get("choices", [{}])[0].get("text", "").strip()
        if not reply:
            print("No reply generated.")
            return jsonify({"reply": "I couldn't generate a response. Please try again later."})

        return jsonify({"reply": reply})

    except Exception as e:
        # Log the full traceback
        import traceback
        traceback.print_exc()
        print(f"Error occurred: {e}")
        return jsonify({"reply": "Sorry, something went wrong. Please try again later."}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
