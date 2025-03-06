"""
Server module for managing user interactions and database operations.
"""
 
import os
import subprocess
import logging
from flask import Flask, request, jsonify
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configuration
PORT = int(os.getenv('PORT', '443'))
STATUS = 'online'
RUNNING = False
SERVERS = 1
CLIENTS = 0

class User:
    """User management class."""

    @staticmethod
    def login(username, password):
        """Login method."""
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()

        conn.close()

        if result and result[0] == password:
            return True
        return False
    @staticmethod
    def register(username, password, email):
        subprocess.run(f"sqlite3 users.db \"INSERT INTO users (email, username, password) VALUES ('{email}', '{username}', '{password}');\", shell=True)")
class Database:
    """Database interaction class."""

    @staticmethod
    def get(database, line, col):
        """Get data from the database."""
        if database == "users":
            message = {
                "Error": "401 Unauthorized",
                "Message": "You are not authorized to access this resource."
            }
        return message

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
            index = {
                "status": STATUS,
                "returned": f"server is running on port {PORT}",
                "info": f"I have {CLIENTS} clients and {SERVERS} servers"
            }
            return jsonify(index)

        required_params = ['service', 'arg1', 'arg2', 'arg3']
        if all(param in params for param in required_params):
            service = params.get('service')
            arg1 = params.get('arg1')
            arg2 = params.get('arg2')
            arg3 = params.get('arg3')
            return jsonify({
                "Service": service,
                "Arg1": arg1,
                "Arg2": arg2,
                "Arg3": arg3
            })
        if service == 'login':
            User.login(arg1, arg2)
        elif service == 'register':
            User.register(arg1, arg2, arg3)
        elif service == 'get':
            Database.get(arg1, arg2, arg3)
        elif service == 'inject':
            Database.inject(arg1, arg2, arg3)
        else:
            return None
        return "Missing required parameters: service, arg1, arg2, arg3", 400

    @app.errorhandler(503)
    def service_unavailable(error):
        """Handle 503 Service Unavailable errors."""
        response = jsonify({
            "error": "Service Unavailable",
            "message": "The server is currently unable to handle the request due to temporary overloading or maintenance of the server."
        })
        response.status_code = 503
        return response

    return app

def main():
    """Main function to run the server."""
    app = create_app()
    ssl_context = ('/etc/letsencrypt/live/server.elipson.dev/fullchain.pem', '/etc/letsencrypt/live/server.elipson.dev/privkey.pem')
    app.run(host='0.0.0.0', port=PORT, ssl_context=ssl_context)

if __name__ == "__main__":
    main()