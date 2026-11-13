from flask import Flask, render_template
from config import config_by_name
from app.extensions import db

def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Initialize extensions
    db.init_app(app)

    # Register Blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.assessment_routes import assessment_bp
    from app.routes.gap_routes import gap_bp
    from app.routes.analyzer_routes import analyzer_bp
    from app.routes.learning_routes import learning_bp
    from app.routes.practice_routes import practice_bp
    from app.routes.portfolio_routes import portfolio_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(assessment_bp)
    app.register_blueprint(gap_bp)
    app.register_blueprint(analyzer_bp)
    app.register_blueprint(learning_bp)
    app.register_blueprint(practice_bp)
    app.register_blueprint(portfolio_bp)

    # Custom template filters
    @app.template_filter("round_pct")
    def round_pct(val):
        try:
            return f"{float(val):.1f}%"
        except (ValueError, TypeError):
            return "0.0%"

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("errors/500.html"), 500

    return app
