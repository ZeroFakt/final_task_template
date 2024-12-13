
from flask import Blueprint, request, jsonify
from app.services.search import search_links
from app.services.news import fetch_news

api_bp = Blueprint("api", __name__)

@api_bp.route("/search", methods=["GET"])
def search_endpoint():
    query = request.args.get("query", "ЧелГУ")
    results = search_links(query)
    status_code = 200 if "error" not in results else 500
    return jsonify(results), status_code

@api_bp.route("/news", methods=["GET"])
def news_endpoint():
    try:
        news = fetch_news()
        if not news:
            return jsonify({"error": "Новости не найдены"}), 404
        return jsonify(news), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
