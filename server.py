import os
import subprocess
import logging
from flask import Flask, request, jsonify, Blueprint
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configuration
PORT = int(os.getenv('PORT', '443'))
STATUS = 'online'
SERVERS = 1
CLIENTS = 0

class Mail:
    @staticmethod
    def support(subject, message, email):
        """Send support email."""
        full_message = f"Subject: {subject}\n\n{message}\n\nReply to: {email}"
        subprocess.run(
            ['mail', '-s', subject, 'support@elipson.dev'],
            input=full_message.encode(),
            check=True
        )

class User:
    """User management class."""
    
    @staticmethod
    def login(username, password):
        """Login method."""
        conn = sqlite3.connect('/var/www/server.elipson.dev/users.db')
        cursor = conn.cursor()

        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        return result and result[0] == password

    @staticmethod
    def register(username, password, email):
        """Register a new user safely."""
        conn = sqlite3.connect('/var/www/server.elipson.dev/users.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", (email, username, password))
        conn.commit()
        conn.close()

class Database:
    """Database interaction class."""

    @staticmethod
    def get(database, line, col):
        """Get data from the database."""
        if database == "users":
            return {
                "Error": "401 Unauthorized",
                "Message": "You are not authorized to access this resource."
            }
        return {}

    @staticmethod
    def inject(database, line, col, value):
        """Inject data into the database."""
        if database == "users":
            print(line, col, value)
            return True  # Placeholder for actual injection
        return False

def create_app():
    """Create Flask app."""
    app = Flask(__name__)

    @app.route('/')
    def index_route():
        """Index route."""
        params = request.args
        if not params:
            return jsonify({
                "status": STATUS,
                "returned": f"server is running on port {PORT}",
                "info": f"I have {CLIENTS} clients and {SERVERS} servers"
            })

        service = params.get('service')
        arg1 = params.get('arg1')
        arg2 = params.get('arg2')
        arg3 = params.get('arg3')

        if service == 'login' and arg1 and arg2:
            if not User.login(arg1, arg2):
                return "Login failed", 503
        elif service == 'register' and arg1 and arg2 and arg3:
            User.register(arg1, arg2, arg3)
        elif service == 'get' and arg1 and arg2 and arg3:
            return jsonify(Database.get(arg1, arg2, arg3))
        elif service == 'inject' and arg1 and arg2 and arg3:
            Database.inject(arg1, arg2, arg3)
        elif service == 'mail' and arg1 and arg2 and arg3:
            Mail.support(arg1, arg2, arg3)
        else:
            return "Invalid or missing parameters", 400

        return "OK", 200

    @app.errorhandler(503)
    def service_unavailable(error):
        """Handle 503 Service Unavailable errors."""
        return jsonify({
            "error": "Service Unavailable",
            "message": "The server is currently unable to handle the request due to temporary overloading or maintenance."
        }), 503

    # OpenAI API Key Blueprint
    openAiBearer = Blueprint("openAiBearer", __name__)

    @openAiBearer.route("/openAiBearer", methods=["POST"])
    def get_openai_bearer():
        return "/var/www/server.elipson.dev/secrets/openaikey.htm"

    app.register_blueprint(openAiBearer, url_prefix='/api')

    return app

def main():
    """Main function to run the server."""
    app = create_app()
    ssl_context = ('/etc/letsencrypt/live/server.elipson.dev/fullchain.pem', '/etc/letsencrypt/live/server.elipson.dev/privkey.pem')
    app.run(host='0.0.0.0', port=PORT, ssl_context=ssl_context)

if __name__ == "__main__":
    main()
