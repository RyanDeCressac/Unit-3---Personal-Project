import sqlite3
import http.server
import socketserver
from urllib.parse import parse_qs

# Connects to database
Connection = sqlite3.connect('botc_database.db')
cursor = Connection.cursor()
print("Successfully Connected to SQLite")

# Creates Games table if it doesn't already exist
sqlite_create_table_query = '''CREATE TABLE IF NOT EXISTS Games (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            character TEXT NOT NULL,
                            alignment TEXT NOT NULL,
                            win TEXT NOT NULL);'''
cursor.execute(sqlite_create_table_query)
Connection.commit()

# Creates Login table if it doesn't already exist
sqlite_create_table_query = '''CREATE TABLE IF NOT EXISTS Login (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL,
                            password TEXT NOT NULL);'''
cursor.execute(sqlite_create_table_query)
Connection.commit()

def validate_register(username, password):
    """
    Ensures input meets sanitisation rules before allowing it to be stored.
    """
    if not username or not password:
        return False
    if not isinstance(username, str) or len(username) > 20:
        return False
    if any(char in username for char in "<>/\\:*?\"|!@#$%^&() "):
        return False
    if not username.isalpha():
        return False
    if not isinstance(password, str) or len(username) < 7:
        return False
    if any(char in password for char in "<> "):
        return False
    if checkUsername(username) == True:
        return False
    return True

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

def insertLoginData(username, password):
    """
    Inserts valid data into the Login table.
    """
    try:
        sqlite_insert_with_param = """INSERT INTO Login (username, password) VALUES (?, ?);"""
        cursor.execute(sqlite_insert_with_param, (username, password))
        Connection.commit()
        print("Information successfully committed")
    except sqlite3.Error as error:
        print("Error while inserting data into SQLite table:", error)

def insertGameData(character, alignment, win):
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

def checkLogin(username, password):
    '''
    Checks if username and password are in the database
    '''
    cursor.execute('SELECT username, password FROM Login')
    rows = cursor.fetchall()
    for row in rows:
        if row[0] == username and row[1] == password:
            return True
    return False

def checkUsername(username):
    '''
    Checks if username is in the database
    '''
    cursor.execute('SELECT username FROM Login')
    usernames = cursor.fetchall()
    for saved_username in usernames:
        if  username == saved_username[0]:
            return True
    return False

# Defines port
PORT = 8000

checkUsername("balls")

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":  # Directs to index.html
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(open("index.html", "rb").read())  # Serve index.html

        else:
            # Serve other files (like styles.css)
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        '''
        Handles POST requests and processes form submissions.
        '''
        if self.path == "/submit":
            '''
            Logging a game
            '''
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
            insertGameData(character, alignment, win)

            # Success Response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Data submitted successfully!</h1></body></html>")

        elif self.path == "/register":
            '''
            Registering an account
            '''
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8")
            data = parse_qs(post_data)

            username = data.get("username", [""])[0]
            password = data.get("password", [""])[0]

            # Validate Input
            if not validate_register(username,password):
                # Unsuccess Response
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(open("register.html", "rb").read())  # Serve index.html
                return
            
            else:
                #You would hash here, but since this is an offline website, hashing is unneccesary

                # Success Response
                insertLoginData(username, password)
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(open("index.html", "rb").read())  # Serve index.html
        
        elif self.path == "/login":
            '''
            Logging in
            '''
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8")
            data = parse_qs(post_data)

            username = data.get("username", [""])[0]
            password = data.get("password", [""])[0]

            if checkLogin(username, password) == True:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(open("mainpage.html", "rb").read())  # Serve mainpage.html
            
            else:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(open("index.html", "rb").read())  # Serve index.html

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
