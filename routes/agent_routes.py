from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from services.farming_agent import farming_agent_service
from services.voice_service import voice_service
from services.rate_limiter import rate_limit

agent_bp = Blueprint("agent", __name__, url_prefix="/agent")

@agent_bp.route("/assistant", methods=["GET"])
@login_required
def assistant():
    languages = voice_service.get_supported_languages()
    tools = farming_agent_service.tools
    return render_template("assistant.html", languages=languages, tools=tools)

@agent_bp.route("/chat", methods=["POST"])
@login_required
@rate_limit(limit=15, window_seconds=60)
def chat():
    data = request.get_json() or {}
    user_query = data.get("query", "").strip()
    language = data.get("language", current_user.preferred_language or "en")
    
    if not user_query:
        return jsonify({"status": "error", "message": "Query cannot be empty."}), 400
        
    result = farming_agent_service.run_agent(user_query, current_user.id, language=language)
    return jsonify(result)
