from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS  # Import Flask-CORS
import os
import requests
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired

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

        if service == 'getOpenAIToken':
            return get_openai_token()

        elif service == 'get':
            return get_data(arg1, arg2, arg3)

        elif service == 'inject':
            return inject_data(arg1, arg2, arg3)

        return jsonify({"error": "Invalid or missing parameters"}), 400

    def generate_token():
        """Generate a token for the client."""
        s = Serializer(app.config['SECRET_KEY'], expires_in=3600)
        return s.dumps({'access': 'openai'}).decode('utf-8')

    def verify_token(token):
        """Verify the token from the client."""
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return False  # Token has expired
        except BadSignature:
            return False  # Token is invalid
        return data

    def get_openai_token():
        """Generate and return a token for the client."""
        token = generate_token()
        return jsonify({"token": token}), 200

    def get_openai_key(token):
        """Verify the token and return the OpenAI API key securely."""
        if not verify_token(token):
            return jsonify({"error": "Invalid or expired token"}), 403

        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            return jsonify({"api_key": api_key}), 200
        else:
            return jsonify({"error": "API key not found"}), 404

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
        if origin != "https://elipson.dev":
            return jsonify({"error": "Unauthorized origin"}), 403

        # Handle actual POST request
        token = request.json.get('token')
        return get_openai_key(token)

    app.register_blueprint(openAiBearer, url_prefix='/api')

    return app

def main():
    """Main function to run the server."""
    app = create_app()
    ssl_context = ('/etc/letsencrypt/live/server.elipson.dev/fullchain.pem', '/etc/letsencrypt/live/server.elipson.dev/privkey.pem')
    app.run(host='0.0.0.0', port=443, ssl_context=ssl_context)

if __name__ == "__main__":
    main()