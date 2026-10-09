import os
from pathlib import Path
from flask import Flask, send_from_directory, render_template, abort, request
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from config import Config
from models.database import db
from models.user import User
from models.analysis import ModelRegistryEntry
from models.knowledge import KnowledgeDocument
from services.rag_service import rag_service

# Import Blueprints
from routes.auth_routes import auth_bp
from routes.main_routes import main_bp
from routes.crop_routes import crop_bp
from routes.agent_routes import agent_bp
from routes.knowledge_routes import knowledge_bp
from routes.weather_routes import weather_bp
from routes.soil_routes import soil_bp
from routes.recommendation_routes import recommendation_bp
from routes.irrigation_routes import irrigation_bp
from routes.monitoring_routes import monitoring_bp
from routes.market_routes import market_bp
from routes.admin_routes import admin_bp

csrf = CSRFProtect()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure directories exist
    Config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    Config.GENERATED_FOLDER.mkdir(parents=True, exist_ok=True)
    Config.SAVED_MODELS_FOLDER.mkdir(parents=True, exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    
    # Exclude AJAX chat API from CSRF token requirement for smooth frontend integration
    csrf.exempt(agent_bp)
    
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please sign in to access this agricultural module."
    login_manager.login_message_category = "warning"
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    # Enterprise Security Headers Middleware
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "microphone=(self), camera=(self)"
        
        # Static asset caching efficiency
        if request.path.startswith("/static/"):
            response.headers["Cache-Control"] = "public, max-age=86400"
            
        return response
        
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(crop_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(knowledge_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(soil_bp)
    app.register_blueprint(recommendation_bp)
    app.register_blueprint(irrigation_bp)
    app.register_blueprint(monitoring_bp)
    app.register_blueprint(market_bp)
    app.register_blueprint(admin_bp)
    
    # Serve uploaded images securely
    @app.route("/uploads/<filename>")
    def uploaded_file(filename):
        # Prevent directory traversal
        safe_path = Path(Config.UPLOAD_FOLDER) / filename
        if not safe_path.resolve().is_relative_to(Config.UPLOAD_FOLDER.resolve()):
            abort(403)
        return send_from_directory(Config.UPLOAD_FOLDER, filename)
        
    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("base.html", error_message="Page Not Found (404). Please return to dashboard."), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("base.html", error_message="Access Forbidden (403). Administrator credentials required."), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("base.html", error_message="Internal Server Error (500). The engineering team has been notified."), 500

    # Auto seed initial database and sample ICAR manual
    with app.app_context():
        db.create_all()
        # Seed admin if no users exist
        if User.query.count() == 0:
            admin = User(
                username="admin",
                email="admin@krishimitra.ai",
                role="admin",
                preferred_language="en",
                state_district="Bengaluru, Karnataka"
            )
            admin.set_password("Admin@KrishiMitra2026")
            db.session.add(admin)
            
            # Seed demo farmer
            farmer = User(
                username="farmer_ramesh",
                email="ramesh@krishimitra.ai",
                role="farmer",
                preferred_language="kn",
                state_district="Kolar, Karnataka"
            )
            farmer.set_password("Farmer@123")
            db.session.add(farmer)
            db.session.commit()
            print("Seeded default users: admin (admin@krishimitra.ai) and farmer_ramesh (ramesh@krishimitra.ai)")
            
        # Seed knowledge repository with authentic ICAR document if empty
        if KnowledgeDocument.query.count() == 0:
            sample_doc = Config.DATASETS_FOLDER / "sample_icar_tomato_manual.txt"
            if sample_doc.exists():
                try:
                    rag_service.ingest_document(
                        file_path=sample_doc,
                        title="ICAR Package of Practices: Tomato Disease & Nutrient Management",
                        author_source="ICAR-IIHR & UAS Bengaluru",
                        doc_type="Extension Manual",
                        language="en"
                    )
                    print("Seeded verified ICAR knowledge manual into vector store.")
                except Exception as e:
                    print(f"Error seeding knowledge document: {e}")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
