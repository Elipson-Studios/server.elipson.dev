from flask import Flask, request, jsonify, Blueprint, redirect, url_for
from flask_cors import CORS  # Import Flask-CORS
import os
import sqlite3
import requests
from itsdangerous import URLSafeTimedSerializer as Serializer, BadSignature, SignatureExpired

def create_app():
    """Create Flask app."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')

    # Enable CORS for the app (for specific route)
    CORS(app, resources={r"/api/*": {"origins": "https://elipson.dev"}})

    @app.route('/')
    def index_route():
        """Index route."""
        params = request.args
        if not params:
            return jsonify({
                "status": "online",
                "returned": "server is running",
                "info": "information about server status"
            })

        service = params.get('service')
        arg1 = params.get('arg1')
        arg2 = params.get('arg2')
        arg3 = params.get('arg3')

        if service == 'getOpenAIKey':
            return get_openai_key()

        elif service == 'get':
            return get_data(arg1, arg2, arg3)

        elif service == 'inject':
            return inject_data(arg1, arg2, arg3)

        return jsonify({"error": "Invalid or missing parameters"}), 400

    @app.route('/login', methods=['GET'])
    def login():
        """Generate a login token and return a URL."""
        username = request.args.get('username')
        password = request.args.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        # Validate username and password against the database
        try:
            conn = sqlite3.connect('/var/www/server.elipson.dev/users.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                serializer = Serializer(app.config['SECRET_KEY'], expires_in=3600)  # Token expires in 1 hour
                token = serializer.dumps({'username': username}).decode('utf-8')
                login_url = f"https://elipson.dev/dashboard?token={token}"
                return jsonify({"login_url": login_url})
            else:
                return jsonify({"error": "Invalid username or password"}), 401

        except sqlite3.Error as e:
            return jsonify({"error": f"Database error: {str(e)}"}), 500

    def get_openai_key():
        """Read and use the OpenAI API key to make a request."""
        key_file_path = '/var/www/server.elipson.dev/secrets/openaikey.htm'

        try:
            with open(key_file_path, 'r') as key_file:
                api_key = key_file.read().strip()
            
            if not api_key:
                return jsonify({"error": "API key not found"}), 404
            
            # Make a request to OpenAI's API (example)
            headers = {"Authorization": f"Bearer {api_key}"}
            openai_response = requests.post(
                "https://api.openai.com/v1/your-endpoint",
                headers=headers,
                json={"your_request_payload": "data"}
            )

            if openai_response.status_code == 200:
                return jsonify(openai_response.json()), 200
            else:
                return jsonify({"error": "Failed to communicate with OpenAI API", "details": openai_response.json()}), openai_response.status_code
        
        except FileNotFoundError:
            return jsonify({"error": "API key file not found"}), 404
        except Exception as e:
            return jsonify({"error": f"Error reading API key: {str(e)}"}), 500

    def get_data(database, line, col):
        """Get data from the database."""
        if database == "users":
            # Placeholder code for getting user data (this should be adapted)
            return jsonify({"message": "Fetched data successfully."}), 200
        return jsonify({"error": "Invalid database"}), 400

    def inject_data(database, line, col, value):
        """Inject data into the database."""
        if database == "users":
            # Placeholder code for injecting data (this should be adapted)
            return jsonify({"message": "Data injected successfully."}), 200
        return jsonify({"error": "Invalid database"}), 400

    # OpenAI API Key Blueprint
    openAiBearer = Blueprint("openAiBearer", __name__)

    # Ensure this route handles OPTIONS requests, as well
    @openAiBearer.route("/openAiBearer", methods=["POST", "OPTIONS"])
    def openai_bearer():
        if request.method == 'OPTIONS':
            # Handle CORS preflight request
            response = jsonify({"message": "CORS preflight successful"})
            response.status_code = 200
            return response

        # Validate the Origin header
        origin = request.headers.get('Origin')
        if not origin:
            return jsonify({"error": "Missing Origin header"}), 403
        if origin != "https://elipson.dev":
            return jsonify({"error": f"Unauthorized origin: {origin}"}), 403

        # Handle actual POST request
        try:
            data = request.json
            if not data or 'input' not in data:
                return jsonify({"error": "Invalid request data"}), 400
            
            # Use the get_openai_key() function to make the request
            return get_openai_key()

        except Exception as e:
            return jsonify({"error": f"Error processing request: {str(e)}"}), 500

    app.register_blueprint(openAiBearer, url_prefix='/api')

    return app

def main():
    """Main function to run the server."""
    app = create_app()
    ssl_context = ('/etc/letsencrypt/live/server.elipson.dev/fullchain.pem', '/etc/letsencrypt/live/server.elipson.dev/privkey.pem')
    app.run(host='0.0.0.0', port=443, ssl_context=ssl_context)

if __name__ == "__main__":
    main()