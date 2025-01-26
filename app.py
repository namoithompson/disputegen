from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Retrieve OpenAI API key securely from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/generate-dispute", methods=["POST"])
def generate_dispute():
    # Log that the endpoint was hit
    print("Endpoint '/generate-dispute' hit")

    # Check if the request is JSON
    if not request.is_json:
        print("Request is not in JSON format")
        return jsonify({"error": "Request must be in JSON format"}), 400

    try:
        # Parse the JSON data
        data = request.get_json()
        print(f"Received data: {data}")

        # Extract required fields
        creditor = data.get("creditor")
        default_amount = data.get("default_amount")
        breach_details = data.get("breach_details")

        # Validate fields
        if not creditor or not default_amount or not breach_details:
            print("Missing required fields in request data")
            return jsonify({"error": "Missing required fields"}), 400

        # Build the chat messages
        messages = [
            {"role": "system", "content": "You are an assistant that drafts professional dispute letters."},
            {"role": "user", "content": f"Creditor: {creditor}\nDefault Amount: {default_amount}\nBreach Details: {breach_details}"}
        ]
        print(f"Generated OpenAI messages: {messages}")

        # Call OpenAI Chat Completion API using the new interface
        response = openai.chat.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=350,
            temperature=0.7
        )
        print(f"OpenAI API Response: {response}")

        # Extract the generated letter
        dispute_letter = response["choices"][0]["message"]["content"].strip()
        print(f"Generated dispute letter: {dispute_letter}")

        return jsonify({"dispute_letter": dispute_letter}), 200

    except openai.OpenAIError as e:
        # Handle OpenAI API-specific errors
        print(f"OpenAI API Error: {str(e)}")
        return jsonify({"error": "OpenAI API Error", "details": str(e)}), 500
    except Exception as e:
        # Handle all other unexpected errors
        print(f"Unexpected Error: {str(e)}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


if __name__ == "__main__":
    # Run the app on port 5000
    app.run(host="0.0.0.0", port=5000)
