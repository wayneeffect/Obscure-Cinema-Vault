import os
import random
import logging
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

# Configure logging for observability on Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static")

# Environment & Config
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_DISCOVER_URL = "https://api.themoviedb.org/3/discover/movie"

# Hardening: Security Headers & CSP via Talisman
Talisman(
    app,
    content_security_policy={
        'default-src': '\'self\'',
        'img-src': ['\'self\'', 'https://image.tmdb.org', 'data:'],
        'style-src': ['\'self\'', '\'unsafe-inline\'', 'https://fonts.googleapis.com'],
        'font-src': ['\'self\'', 'https://fonts.gstatic.com']
    },
    force_https=os.getenv("FLASK_ENV") == "production"
)

# Hardening: Rate Limiting (Prevents API abuse / spam)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"],
    storage_uri="memory://"
)

@app.route("/")
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route("/api/pick-movie", methods=["GET"])
@limiter.limit("15 per minute")  # Max 15 clicks/minute per IP
def pick_obscure_movie():
    # 1. Config Verification
    if not TMDB_API_KEY:
        logger.error("TMDB_API_KEY environment variable is not set.")
        return jsonify({
            "error": "Server Configuration Error",
            "message": "The movie service is currently misconfigured."
        }), 500

    # 2. Input Validation (Safe boundaries for obscurity rating)
    try:
        max_votes = int(request.args.get("max_votes", 500))
        max_votes = max(50, min(max_votes, 1500))  # Bound between 50 and 1500
    except ValueError:
        max_votes = 500

    # TMDB Discover Parameters for High-Rating Obscurity
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
        "sort_by": "vote_average.desc",
        "vote_count.gte": 15,
        "vote_count.lte": max_votes,
        "vote_average.gte": 6.8,
        "page": random.randint(1, 15)  # Randomize pagination for discovery
    }

    try:
        # Enforce strict 5.0 second timeout to prevent hung worker threads
        res = requests.get(TMDB_DISCOVER_URL, params=params, timeout=5.0)
        res.raise_for_status()

        data = res.json()
        results = data.get("results", [])

        if not results:
            return jsonify({
                "error": "Not Found",
                "message": "No obscure movies matched the search criteria. Try again!"
            }), 404

        selected = random.choice(results)

        # 3. Payload Sanitization & Null Fallbacks
        poster_path = selected.get("poster_path")
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

        return jsonify({
            "title": selected.get("title", "Unknown Title"),
            "overview": selected.get("overview") or "No plot summary available for this obscure title.",
            "release_date": selected.get("release_date", "Unknown Release Date"),
            "rating": selected.get("vote_average", "N/A"),
            "vote_count": selected.get("vote_count", 0),
            "poster_url": poster_url
        }), 200

    # 4. Explicit Error Handling Pipeline
    except requests.exceptions.Timeout:
        logger.warning("TMDB API request timed out.")
        return jsonify({
            "error": "Gateway Timeout",
            "message": "The movie database took too long to respond. Please try again."
        }), 504

    except requests.exceptions.RequestException as e:
        logger.error(f"TMDB Request Error: {e}")
        return jsonify({
            "error": "Bad Gateway",
            "message": "Unable to communicate with the upstream movie database."
        }), 502

    except Exception as e:
        logger.error(f"Unexpected Exception: {e}")
        return jsonify({
            "error": "Internal Error",
            "message": "An unexpected error occurred."
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
