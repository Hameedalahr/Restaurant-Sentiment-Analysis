

// JavaScript file to handle Restaurant Sentiment Analysis interactions

// Array to store reviews
const reviews = [];

// Function to determine sentiment of a review
function getSentiment(text) {
    const positiveWords = ["good", "great", "amazing", "excellent", "fantastic", "positive", "love", "happy", "satisfied"];
    const negativeWords = ["bad", "terrible", "awful", "poor", "negative", "hate", "unhappy", "disappointed"];

    let positiveScore = 0;
    let negativeScore = 0;

    const words = text.toLowerCase().split(/\s+/);

    words.forEach(word => {
        if (positiveWords.includes(word)) positiveScore++;
        if (negativeWords.includes(word)) negativeScore++;
    });

    if (positiveScore > negativeScore) return "Positive";
    if (negativeScore > positiveScore) return "Negative";
    return "Neutral";
}

// Function to handle review submission
function submitReview() {
    const name = document.getElementById("name").value;
    const reviewText = document.getElementById("review").value;

    if (!name || !reviewText) {
        alert("Please fill out both your name and your review before submitting!");
        return;
    }

    const sentiment = getSentiment(reviewText);
    let rating;

    if (sentiment === "Positive") {
        rating = 5;
    } else if (sentiment === "Negative") {
        rating = 0;
    } else {
        rating = 3; // Neutral sentiment gets a default rating of 3
    }

    const review = {
        name: name,
        text: reviewText,
        sentiment: sentiment,
        rating: rating,
    };

    reviews.push(review);
    document.getElementById("name").value = "";
    document.getElementById("review").value = "";

    updateReviews();
}

// Function to update reviews section
function updateReviews() {
    const reviewsContainer = document.getElementById("reviews-container");
    reviewsContainer.innerHTML = "<h2>Reviews</h2>"; // Reset container

    reviews.forEach((review, index) => {
        const reviewCard = document.createElement("div");
        reviewCard.className = "review-card";

        reviewCard.innerHTML = `
            <h3>${review.name}</h3>
            <p>${review.text}</p>
            <p>Sentiment: ${review.sentiment}</p>
            <p>Rating: ⭐ ${review.rating} / 5</p>
            <button onclick="deleteReview(${index})">Delete</button>
        `;

        reviewsContainer.appendChild(reviewCard);
    });

    updateAverageRating();
}

// Function to calculate and display average rating
function updateAverageRating() {
    if (reviews.length === 0) {
        document.getElementById("rating").textContent = "⭐ 0 / 5";
        return;
    }

    const totalRating = reviews.reduce((sum, review) => sum + review.rating, 0);
    const averageRating = (totalRating / reviews.length).toFixed(1);

    document.getElementById("rating").textContent = `⭐ ${averageRating} / 5`;
}

// Function to delete a review
function deleteReview(index) {
    reviews.splice(index, 1);
    updateReviews();
}
