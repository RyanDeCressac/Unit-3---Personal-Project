import sqlite3
import http.server
import socketserver
from urllib.parse import parse_qs
import pandas as pd
import csv

# Connects to database
Connection = sqlite3.connect('botc_database.db')
cursor = Connection.cursor()
print("Successfully Connected to SQLite")

# Creates Games table if it doesn't already exist
sqlite_create_table_query = '''CREATE TABLE IF NOT EXISTS Games (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL,
                            character TEXT NOT NULL,
                            character_change TEXT NOT NULL,
                            starting_character TEXT,
                            alignment TEXT NOT NULL,
                            alignment_change TEXT NOT NULL,
                            win TEXT NOT NULL,
                            death TEXT NOT NULL,
                            death_type TEXT,
                            script_type TEXT NOT NULL,
                            player_count INTEGER NOT NULL,
                            traveller_count INTEGER);'''
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

def validate_input(character, character_change, starting_character, alignment, alignment_change, win, death, death_type, script_type, player_count, traveller_count):
    """
    Ensures input meets sanitisation rules before allowing it to be stored.
    """
    if not character or not character_change or not alignment or not alignment_change or not win or not death or not script_type or not player_count:
        print("Missing required input")
        return False
    if not username:
        print("Username is not set")
        return False
    if not isinstance(character, str) or findCharacterType(character) is None:
        print("Invalid character value")
        return False
    if character_change not in ["True", "False"]:
        print("Invalid character change value")
        return False
    if character_change == "True":
        if not isinstance(starting_character, str) or findCharacterType(starting_character) is None:
            print("Invalid starting character")
            return False
    if alignment not in ["Good", "Evil"]:
        print("Invalid alignment value")
        return False
    if alignment_change not in ["True", "False"]:
        print("Invalid alignment change value")
        return False
    if win not in ["True", "False"]:
        print("Invalid win value")
        return False
    if death not in ["True", "False"]:
        print("Invalid death value")
        return False
    if death == "True":
        if death_type not in ["Day", "Night"]:
            print("Invalid death type")
            return False
    if script_type not in ["tb", "bmr", "snv", "custom"]:
        print("Invalid script type")
        return False
    if player_count < 5 or player_count > 15:
        print("Invalid player count")
        return False
    if traveller_count < 0:
        print("Invalid traveller count")
        return False
    print("All inputs valid")
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

def insertGameData(character, character_change, starting_character, alignment, alignment_change, win, death, death_type, script_type, player_count, traveller_count):
    """
    Inserts valid data into the Games table.
    """

    try:
        sqlite_insert_with_param = """INSERT INTO Games (username, character, character_change, starting_character, alignment, alignment_change, win, death, death_type, script_type, player_count, traveller_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        cursor.execute(sqlite_insert_with_param, (username, character, character_change, starting_character, alignment, alignment_change, win, death, death_type, script_type, player_count, traveller_count))
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

def findCharacterType(character):
    '''
    Checks if character is in the character_type.csv file
    '''
    with open('character_type.csv', mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if character.capitalize() in row:  # Checks if the string exists in any row
                return row[0]
    return None

# Defines port
PORT = 8000

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":  # Directs to index.html
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(open("index.html", "rb").read())  # Serve index.html
        
        elif self.path == "/run_function.html":  # Directs to blankpage.html and sets up database
            query = "SELECT id, character, character_change, starting_character, alignment, alignment_change, win, death, death_type, script_type, player_count, traveller_count FROM Games WHERE username = ? ORDER BY id DESC"
            df = pd.read_sql_query(query, Connection, params=(username,))
            html_content = df.to_html(index=False, header=True, justify='center', border=0, classes='table table-striped')
            html_page = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>SQL Query Results</title>
                <style>
                    table {{ border-collapse: collapse; width: 50%; }}
                    th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
                </style>
            </head>
            <body>
                <h2>SQL Query Results</h2>
                {html_content}
                <button onclick="window.location.href='mainpage.html'">Return to Menu</button>
            </body>
            </html>
            """

            with open("blankpage.html", "w") as file:
                file.write(html_page)
                self.send_response(200)

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
            character = data.get("character", [""])[0] # What character were you playing
            character_change = data.get("character_change", [""])[0] # Did your character change
            starting_character = data.get("starting_character", [""])[0] # If you did change character, what character did you start as
            alignment = data.get("alignment", [""])[0] # What alignment were you
            alignment_change = data.get("alignment_change", [""])[0] # Did your alignment change
            win = data.get("win", [""])[0] # Did you win?
            death = data.get("death", [""])[0] # Did you die?
            death_type = data.get("death_type", [""])[0] # If you did die, when did you die
            script_type = data.get("script_type", [""])[0] # What script were you playing
            player_count = int(data.get("player_count", [""])[0]) # How many non-traveller players were there
            traveller_count = int(data.get("traveller_count", [""])[0]) # How many travellers were there  
        
            # Validate Input
            if not validate_input(character, character_change, starting_character, alignment, alignment_change, win, death, death_type, script_type, player_count, traveller_count):
                self.send_response(302)  # Redirect on validation failure
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(open("addgame.html", "rb").read())  # Serve index.html
                return

            # Insert Data if Valid
            insertGameData(character, character_change, starting_character, alignment, alignment_change, win, death, death_type, script_type, player_count, traveller_count)

            # Success Response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(open("confirmation.html", "rb").read())  # Serve index.html
            

        elif self.path == "/register":
            '''
            Registering an account
            '''
            global username

            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8")
            data = parse_qs(post_data)

            username = data.get("username", [""])[0]
            password = data.get("password", [""])[0]

            # Validate Input
            if not validate_register(username,password):
                # Unsuccess Response
                self.send_response(302)
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