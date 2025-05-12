import sqlite3
import http.server
import socketserver
from urllib.parse import parse_qs

# Connects to database
Connection = sqlite3.connect('botc_database.db')
cursor = Connection.cursor()
print("Successfully Connected to SQLite")

# Creates table if it doesn't already exist
sqlite_create_table_query = '''CREATE TABLE IF NOT EXISTS Games (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            character TEXT NOT NULL,
                            alignment TEXT NOT NULL,
                            win TEXT NOT NULL);'''
cursor.execute(sqlite_create_table_query)
Connection.commit()

def validate_input(character, alignment, win):
    """
    Ensures input meets sanitisation rules before allowing it to be stored.
    """
    if not character or not alignment or not win:
        return False
    if alignment not in ["Good", "Evil"]:
        return False
    if win not in ["True", "False"]:
        return False
    if not isinstance(character, str) or len(character) > 20:
        return False
    if any(char in character for char in "<>/\\:*?\"|!@#$%^&() "):
        return False
    if not character.isalpha():
        return False
    return True

def insertData(character, alignment, win):
    """
    Inserts valid data into the Games table.
    """
    # Capitalizes variables
    character = character.capitalize()
    alignment = alignment.capitalize()
    win = win.capitalize()

    try:
        sqlite_insert_with_param = """INSERT INTO Games (character, alignment, win) VALUES (?, ?, ?);"""
        cursor.execute(sqlite_insert_with_param, (character, alignment, win))
        Connection.commit()
        print("Information successfully committed")
    except sqlite3.Error as error:
        print("Error while inserting data into SQLite table:", error)

# Defines port
PORT = 8000

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(open("addgame.html", "rb").read())  # Serve the form page
        else:
            # Serve other files (like styles.css)
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        """Handles POST requests and processes form submissions."""
        if self.path == "/submit":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8")
            data = parse_qs(post_data)

            character = data.get("character", [""])[0]
            alignment = data.get("alignment", [""])[0]
            win = data.get("win", [""])[0]

            # Validate Input
            if not validate_input(character, alignment, win):
                self.send_response(302)  # Redirect on validation failure
                self.send_header("Location", "/")  # Redirect back to form
                self.end_headers()
                return

            # Insert Data if Valid
            insertData(character, alignment, win)

            # Success Response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Data submitted successfully!</h1></body></html>")
            
        else:
            self.send_response(404)
            self.end_headers()

# Starts the server
with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    print(f"Serving HTTP on port {PORT}")
    httpd.serve_forever()

# Closes connection
cursor.close()
Connection.close()
print("SQLite connection is closed")
