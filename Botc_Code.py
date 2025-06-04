import sqlite3
import http.server
import socketserver
import urllib.parse
import pandas as pd
import csv
import json

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
    elif not username:
        print("Username is not set")
        return False
    elif not isinstance(character, str) or findCharacterType(character) is None:
        print("Invalid character value")
        return False
    elif character_change not in ["True", "False"]:
        print("Invalid character change value")
        return False
    elif not isinstance(starting_character, str) or (findCharacterType(starting_character) is None and starting_character != "None"):
        print("Invalid starting character")
        return False
    elif alignment not in ["Good", "Evil"]:
        print("Invalid alignment value")
        return False
    elif alignment_change not in ["True", "False"]:
        print("Invalid alignment change value")
        return False
    elif win not in ["True", "False"]:
        print("Invalid win value")
        return False
    elif death not in ["True", "False"]:
        print("Invalid death value")
        return False
    elif death_type not in ["Day", "Night","None"]:
        print("Invalid death type")
        return False
    elif script_type not in ["tb", "bmr", "snv", "custom"]:
        print("Invalid script type")
        return False
    elif player_count < 5 or player_count > 15:
        print("Invalid player count")
        return False
    elif traveller_count < 0:
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

def updateGameData(character, character_change, starting_character, alignment, alignment_change, win, death, death_type, script_type, player_count, traveller_count, row_id):
    '''
    Update valid data into the Games table
    '''
    try:
        update_query = """UPDATE Games SET character=?, character_change=?, starting_character=?, alignment=?, alignment_change=?, win=?, death=?, death_type=?, script_type=?, player_count=?, traveller_count=? WHERE id=?"""
        cursor.execute(update_query, (character, character_change, starting_character, alignment, alignment_change, win, death, death_type, script_type, player_count, traveller_count, row_id))
        Connection.commit()
        print("Information successfully updated")
    except sqlite3.Error as error:
        print("Error while updating data into SQLite table:", error)

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
            if character in row:  # Checks if the string exists in any row
                return row[0]
    return None

def deleteRow(table, id):
    '''
    Deletes a row from a given SQL table
    '''
    try: 
        query = f"DELETE FROM {table} WHERE id = ?"
        cursor.execute(query, (id,))
        Connection.commit()
        print(f"Row {id} deleted")
    except:
        print(f"Failed to delete row {id}")

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
    
            df['Edit'] = df.index.map(lambda i: f'<button onclick="editRow({df.loc[i,"id"]});">Edit</button>')
            df['Delete'] = df.index.map(lambda i: f'<button onclick="deleteRow({df.loc[i,"id"]});">Delete</button>')

            html_table = df.to_html(index=False, escape=False, header=True, justify='center', border=0, classes='table table-striped')
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    .table-striped th:first-child,
                    .table-striped td:first-child {{
                        display: none;
                    }}
                </style>
            </head>
            <body>
                {html_table}
            </body>
            </html>
            """
            with open("updated_content.html", "w") as file:
                file.write(html_content)
        
        elif self.path.startswith("/get_game_data"):
            parsed_url = urllib.parse.urlparse(self.path)
            query_components = urllib.parse.parse_qs(parsed_url.query)
            game_id = query_components.get("id", [None])[0]

            if game_id:
                query = "SELECT * FROM Games WHERE id = ?"
                cursor.execute(query, (game_id,))
                row = cursor.fetchone()

                if row:
                    # Convert row to dictionary using column names
                    column_names = [desc[0] for desc in cursor.description]
                    row_dict = dict(zip(column_names, row))

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(row_dict).encode("utf-8"))
                else:
                    self.send_error(404, "Game data not found")
            else:
                self.send_error(400, "Invalid request: Missing game ID")


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
            data = urllib.parse.parse_qs(post_data)
            character = data.get("character", [""])[0] # What character were you playing
            character_change = data.get("character_change", [""])[0] # Did your character change
            alignment = data.get("alignment", [""])[0] # What alignment were you
            alignment_change = data.get("alignment_change", [""])[0] # Did your alignment change
            win = data.get("win", [""])[0] # Did you win?
            death = data.get("death", [""])[0] # Did you die?
            script_type = data.get("script_type", [""])[0] # What script were you playing
            player_count = int(data.get("player_count", [""])[0]) # How many non-traveller players were there
            traveller_count = int(data.get("traveller_count", [""])[0]) # How many travellers were there  
        
            if character_change == "False":
                starting_character = "None"
            else:
                starting_character = data.get("starting_character", [""])[0] # If you did change character, what character did you start as
            
            print(starting_character)
                
            
            if death == "False":
                death_type = "None"
            else:
                death_type = data.get("death_type", [""])[0] # If you did die, when did you die
            
            # Validate Input
            if not validate_input(character, character_change, starting_character, alignment, alignment_change, win, death, death_type, script_type, player_count, traveller_count):
                self.send_response(302)  # Redirect on validation failure
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(open("addgame.html", "rb").read())  # Serve index.html
                return
            
            row_id = data.get("row_id", [None])[0] # Check if editing an existing row

            print(row_id)

            if row_id:
                # Update Data if Valid
                print("Updating Game Data")
                updateGameData(character, character_change, starting_character, alignment, alignment_change, win, death, death_type, script_type, player_count, traveller_count, row_id)                
            else:
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
            data = urllib.parse.parse_qs(post_data)

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
            data = urllib.parse.parse_qs(post_data)

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
                
        elif self.path == "/delete":
            '''
            Deleting a logged game
            '''
            
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)  # Read request data
            
            # Parse JSON data
            data = json.loads(post_data.decode("utf-8"))
            row_id = data.get("id")

            if row_id:
                cursor.execute("DELETE FROM Games WHERE id = ?", (row_id,))
                Connection.commit()
        
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