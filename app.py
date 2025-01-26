from flask import Flask, request, jsonify
import openai
import os
import re

app = Flask(__name__)

# Retrieve OpenAI API key securely from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/generate-dispute", methods=["POST"])
def generate_dispute():
    print("Endpoint '/generate-dispute' hit")

    if not request.is_json:
        return jsonify({"error": "Request must be in JSON format"}), 400

    data = request.get_json()
    print(f"Received data: {data}")

    # 1. Grab the "original" section
    original = data.get("original", {})
    if not original:
        return jsonify({"error": "Missing 'original' object in JSON"}), 400

    # 2. Extract first_name and last_name
    names = original.get("names", {})
    first_name = names.get("first_name", "").strip()
    last_name = names.get("last_name", "").strip()
    full_name = (first_name + " " + last_name).strip() or "Unknown Name"

    # 3. Extract the post_content
    post_content = original.get("post_content", "").strip()

    # 4. Combine all non-empty "description_" fields
    breach_texts = []
    for key, value in original.items():
        if key.startswith("description_"):
            clean_val = value.strip()
            if clean_val:
                breach_texts.append(clean_val)

    # Turn the breach_texts list into one string
    if breach_texts:
        breach_details = "\n\n".join(breach_texts)
    else:
        breach_details = "No applicable breaches identified."

    # 5. (Optional) Parse out certain fields from post_content if needed
    #    For example, if you want to extract the "Current credit Provider" or "Current outstanding debt"
    #    from post_content via regex, you can do so here. Otherwise, we just pass it raw.

    # Build the messages for OpenAI
    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that drafts professional dispute letters. "
                "Use the provided user data to write a coherent, formal letter."
            )
        },
        {
            "role": "user",
            "content": (
                f"Client Name: {full_name}\n\n"
                f"User's description of how they received the default:\n{post_content}\n\n"
                f"Breach Details:\n{breach_details}\n\n"
                "Please draft a professional dispute letter incorporating the above information."
            )
        }
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=350,
            temperature=0.7
        )

        dispute_letter = response["choices"][0]["message"]["content"].strip()
        print(f"Generated dispute letter: {dispute_letter}")

        return jsonify({"dispute_letter": dispute_letter}), 200

    except openai.OpenAIError as e:
        print(f"OpenAI API Error: {str(e)}")
        return jsonify({"error": "OpenAI API Error", "details": str(e)}), 500
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
