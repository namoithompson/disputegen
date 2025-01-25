from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Retrieve OpenAI API key securely from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/generate-dispute", methods=["POST"])
def generate_dispute():
    if not request.is_json:
        return jsonify({"error": "Request must be in JSON format"}), 400

    try:
        data = request.get_json()

        # Extract required fields
        creditor = data.get("creditor")
        default_amount = data.get("default_amount")
        breach_details = data.get("breach_details")

        if not creditor or not default_amount or not breach_details:
            return jsonify({"error": "Missing required fields"}), 400

        # Build the chat messages
        messages = [
            {"role": "system", "content": "You are an assistant that drafts professional dispute letters."},
            {"role": "user", "content": f"Creditor: {creditor}\nDefault Amount: {default_amount}\nBreach Details: {breach_details}"}
        ]

        # Generate the dispute letter using Chat Completion API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use gpt-4 for better results if available
            messages=messages,
            max_tokens=350,
            temperature=0.7
        )

        dispute_letter = response['choices'][0]['message']['content'].strip()

        return jsonify({"dispute_letter": dispute_letter}), 200

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred while generating the dispute letter."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)