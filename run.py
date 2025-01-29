
from flask import Flask, render_template, request, jsonify
from textblob import TextBlob

app = Flask(__name__)

# In-memory storage for reviews
reviews = []
review_id_counter = 0

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add_review", methods=["POST"])
def add_review():
    global review_id_counter
    data = request.json
    name = data.get("name")
    review = data.get("review")

    # Perform sentiment analysis
    sentiment_score = TextBlob(review).sentiment.polarity
    sentiment_label = "Positive" if sentiment_score > 0 else "Negative" if sentiment_score < 0 else "Neutral"

    # Add review to storage
    reviews.append({
        "id": review_id_counter,
        "name": name,
        "review": review,
        "sentiment": sentiment_label
    })
    review_id_counter += 1

    # Calculate rating
    total_reviews = len(reviews)
    positive_count = sum(1 for r in reviews if r["sentiment"] == "Positive")
    rating = (positive_count / total_reviews) * 5 if total_reviews > 0 else 0

    return jsonify({
        "reviews": reviews,
        "rating": round(rating, 2)
    })

@app.route("/delete_review", methods=["POST"])
def delete_review():
    data = request.json
    review_id = data.get("id")

    global reviews
    reviews = [r for r in reviews if r["id"] != review_id]

    # Recalculate rating
    total_reviews = len(reviews)
    positive_count = sum(1 for r in reviews if r["sentiment"] == "Positive")
    rating = (positive_count / total_reviews) * 5 if total_reviews > 0 else 0

    return jsonify({
        "reviews": reviews,
        "rating": round(rating, 2)
    })


if __name__ == "__main__":
    app.run(debug=True)
