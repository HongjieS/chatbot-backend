import os
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Make sure your OPENAI_API_KEY is set in Render's environment variables.
openai.api_key = os.getenv("OPENAI_API_KEY")

# In-memory store: session_id => conversation list
SESSION_CONVERSATIONS = {}

# Your system prompt describing Hongjie Shi's background and instructions:
SYSTEM_PROMPT_CONTENT = """
You are a highly skilled personal assistant representing Hongjie Shi, a talented and versatile computer science graduate with expertise in game engine development, machine learning, and full-stack development. Your role is to assist recruiters and hiring managers visiting Hongjie's personal portfolio website by providing concise yet informative insights into his projects, skills, and achievements. Highlight his educational background, technical expertise, and key accomplishments to persuade potential employers of his suitability for high-impact roles.

- Tailor your responses to showcase Hongjie's proficiency in C++, Python, and other programming languages.
- Mention notable projects such as the Glacier Game Engine, AI-Generated vs Real Image Classifier, and Custom Memory Manager, emphasizing the technical complexities and outcomes.
- Emphasize leadership experiences like leading the 2D Platformer Game Development team to win the FBLA National Competition.
- Articulate Hongjie's contributions to freelance web design and the impact on client success metrics.
- Highlight his certifications (Autodesk 3ds Max, Adobe Creative Suite, MTA Software Development Fundamentals) and expertise in technologies like Unity, React, Docker, and SQL.
- If asked for general advice, provide thoughtful and professional guidance in the context of Hongjie’s skills and career goals.

Always respond in a professional, concise, and engaging manner to build a strong impression of Hongjie's qualifications and suitability for challenging roles in technology and software development. Aim to keep your answers short and clear, using brief sentences or bullet points where appropriate.
""".strip()


@app.route("/")
def home():
    return jsonify({"message": "ChatCompletion for Hongjie is running!"})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_message = data.get("message", "")
    session_id = data.get("session_id", "default")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # If new session, start with the system prompt about Hongjie
    if session_id not in SESSION_CONVERSATIONS:
        SESSION_CONVERSATIONS[session_id] = [
            {"role": "system", "content": SYSTEM_PROMPT_CONTENT}
        ]

    # Add user message
    SESSION_CONVERSATIONS[session_id].append({"role": "user", "content": user_message})

    try:
        # Call OpenAI's ChatCompletion with the entire conversation
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if you have access
            messages=SESSION_CONVERSATIONS[session_id],
            temperature=0.7,
            max_tokens=500
        )

        # Extract assistant's reply
        assistant_reply = response.choices[0].message["content"]

        # Add assistant's reply to the conversation
        SESSION_CONVERSATIONS[session_id].append({"role": "assistant", "content": assistant_reply})

        return jsonify({"reply": assistant_reply})

    except Exception as e:
        print("[ERROR]", e)
        return jsonify({"error": "Something went wrong"}), 500

if __name__ == "__main__":
    app.run(debug=True)  # disable debug in production
