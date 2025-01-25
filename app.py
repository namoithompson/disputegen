import logging
from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

logging.basicConfig(level=logging.INFO)

@app.route("/generate-dispute", methods=["POST"])
def generate_dispute():
    if not request.is_json:
        logging.info("Request is not in JSON format.")
        return jsonify({"error": "Request must be in JSON format"}), 400

    try:
        data = request.get_json()
        logging.info(f"Request data: {data}")

        creditor = data.get("creditor")
        default_amount = data.get("default_amount")
        breach_details = data.get("breach_details")

        if not creditor or not default_amount or not breach_details:
            logging.info("Missing required fields.")
            return jsonify({"error": "Missing required fields"}), 400

        messages = [
            {"role": "system", "content": "You are an assistant that drafts professional dispute letters."},
            {"role": "user", "content": f"Creditor: {creditor}\nDefault Amount: {default_amount}\nBreach Details: {breach_details}"}
        ]

        logging.info("Calling OpenAI API...")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=350,
            temperature=0.7
        )
        logging.info("OpenAI API response received.")

        dispute_letter = response['choices'][0]['message']['content'].strip()
        logging.info("Dispute letter generated successfully.")

        return jsonify({"dispute_letter": dispute_letter}), 200

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred while generating the dispute letter."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
