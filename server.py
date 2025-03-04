"""
This module contains the server implementation using Flask.
"""

from flask import Flask, request

PORT = 3000
CLIENTS = 5
SERVERS = 1

databases = {
    'test': {},
    'users': {},
    'transactions': []
}

class User:
    """Class for user-related operations."""

    @staticmethod
    def login(username, password):
        """Login a user with the given username and password."""
        return username == "test" and password == "test"

    @staticmethod
    def register(username, password):
        """Register a user with the given username and password."""
        return username == "test" and password == "test"

class Database:
    """Class for database-related operations."""

    @staticmethod
    def get(database, row, col):
        """Get a value from the database."""
        if database in databases:
            if row in databases[database]:
                if col in databases[database][row]:
                    return databases[database][row][col]
        return None

    @staticmethod
    def inject(database, row, col, value):
        """Inject a value into the database."""
        if database in databases:
            if row in databases[database]:
                databases[database][row][col] = value
            else:
                databases[database][row] = {col: value}
        else:
            databases[database] = {row: {col: value}}

def main():
    """Main function to run the server."""
    print(f"server is running on port {PORT}")
    status = 'online'
    result = f"""
███████╗██████╗░░██████╗██╗██╗░░░░░░█████╗░███╗░░██╗
██╔════╝██╔══██╗██╔════╝██║██║░░░░░██╔══██╗████╗░██║
█████╗░░██████╔╝╚█████╗░██║██║░░░░░██║░░██║██╔██╗██║
██╔══╝░░██╔═══╝░░╚═══██╗██║██║░░░░░██║░░██║██║╚████║
███████╗██║░░░░░██████╔╝██║███████╗╚█████╔╝██║░╚███║
╚══════╝╚═╝░░░░░╚═════╝░╚═╝╚══════╝░╚════╝░╚═╝░░╚══╝
200 OK
Status: {status}
Server is running on port {PORT}
I have {CLIENTS} clients and {SERVERS} servers
    """
    print(result)

    app = Flask(__name__)

    @app.route('/query', methods=['GET'])
    def query_params():
        """Handle query parameters."""
        param1 = request.args.get('service')
        param2 = request.args.get('arg1')
        param3 = request.args.get('arg2')
        param4 = request.args.get('arg3')
        if param1 == 'login':
            return str(User.login(param2, param3))
        if param1 == 'register':
            return str(User.register(param2, param3))
        if param1 == 'get':
            return str(Database.get(param2, param3, param4))
        return "Invalid service"

    app.run(port=PORT)

if __name__ == "__main__":
    main()
