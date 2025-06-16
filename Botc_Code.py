import sqlite3
import http.server
import socketserver
import urllib.parse
import pandas as pd
import csv
import json
import matplotlib.pyplot as plt    

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
        
        elif self.path == "/run_function.html":  # Directs to tablegame.html and sets up database
            query = "SELECT * FROM Games WHERE username = ? ORDER BY id DESC"
            df = pd.read_sql_query(query, Connection, params=(username,))

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
        
        elif self.path == "/get_info.html": # Gets facts and figures for showdata.html
            query = "SELECT * FROM Games WHERE username = ?" #Sanatising using paramaters WRITE IN THINGY
            df = pd.read_sql_query(query, Connection, params=(username,))

            totalGames = int(df.shape[0])
            totalGoodGames = int(df[df["alignment"] == "Good"].shape[0])
            totalEvilGames = totalGames - totalGoodGames

            totalWins = int(df[df["win"] == "True"].shape[0])
            totalGoodWins = int(df[(df["alignment"] == "Good") & (df["win"] == "True")].shape[0])
            totalEvilWins = totalWins - totalGoodWins

            startingGoodGames = int(df[(df["alignment"] == "Good") & (df["alignment_change"] == "False")].shape[0]) + int(df[(df["alignment"] == "Evil") & (df["alignment_change"] == "True")].shape[0])
            startingEvilGames = totalGames - startingGoodGames

            goodTeamWins = totalGoodWins + (totalEvilGames - totalEvilWins)
            evilTeamWins = totalGames - goodTeamWins
            
            df["character_type"] = df["character"].apply(findCharacterType)
            
            totalTownsfolkGames = int(df[df["character_type"] == "Townsfolk"].shape[0])
            totalOutsiderGames = int(df[df["character_type"] == "Outsider"].shape[0])
            totalMinionGames = int(df[df["character_type"] == "Minion"].shape[0])
            totalDemonGames = int(df[df["character_type"] == "Demon"].shape[0])
            totalTravellerGames = int(df[df["character_type"] == "Traveller"].shape[0])

            totalTownsfolkWins = int(df[(df["character_type"] == "Townsfolk") & (df["win"] == "True")].shape[0])
            totalOutsiderWins = int(df[(df["character_type"] == "Outsider") & (df["win"] == "True")].shape[0])
            totalMinionWins = int(df[(df["character_type"] == "Minion") & (df["win"] == "True")].shape[0])
            totalDemonWins = int(df[(df["character_type"] == "Demon") & (df["win"] == "True")].shape[0])
            totalTravellerWins = int(df[(df["character_type"] == "Traveller") & (df["win"] == "True")].shape[0])

            df["starting_character_type"] = df["starting_character"].apply(findCharacterType)

            startingTownsfolkGames = int(df[df["starting_character_type"] == "Townsfolk"].shape[0])
            startingOutsiderGames = int(df[df["starting_character_type"] == "Outsider"].shape[0])
            startingMinionGames = int(df[df["starting_character_type"] == "Minion"].shape[0])
            startingDemonGames = int(df[df["starting_character_type"] == "Demon"].shape[0])
            startingTravellerGames = int(df[df["starting_character_type"] == "Traveller"].shape[0])

            charactersPlayed = df["character"].value_counts()
            startingCharactersPlayed = df["starting_character"].value_counts()
            
            totalTBGames = int(df[df["script_type"] == "tb"].shape[0])
            totalBMRGames = int(df[df["script_type"] == "bmr"].shape[0])
            totalSNVGames = int(df[df["script_type"] == "snv"].shape[0])
            totalCustomGames = int(df[df["script_type"] == "custom"].shape[0])

            TBGamesWon = int(df[(df["script_type"] == "tb") & (df["win"] == "True")].shape[0])
            BMRGamesWon = int(df[(df["script_type"] == "bmr") & (df["win"] == "True")].shape[0])
            SNVGamesWon = int(df[(df["script_type"] == "snv") & (df["win"] == "True")].shape[0])
            CustomGamesWon = int(df[(df["script_type"] == "custom") & (df["win"] == "True")].shape[0])

            totalDeadGames = int(df[df["death"] == "True"].shape[0])
            totalAliveGames = totalGames - totalDeadGames
            dayDeadGames = int(df[df["death_type"] == "Day"].shape[0])
            nightDeadGames = int(df[df["death_type"] == "Night"].shape[0])

            deadGamesWon = int(df[(df["death"] == "True") & (df["win"] == "True")].shape[0])
            aliveGamesWon = totalWins - deadGamesWon

            teamColours = ["blue", "red"]
            
            # Pie chart for Good vs Evil games
            labels = ["Good Games", "Evil Games"]
            sizes = [totalGoodGames, totalEvilGames]
            plt.figure(figsize=(6, 6))
            plt.pie(sizes, labels=labels, autopct="%1.1f%%", colors=teamColours)
            plt.title("Good vs Evil Games")
            plt.tight_layout()
            plt.savefig("graphs/good_vs_evil_games.png")  # Save as image

            # Pie chart for Starting Good vs Starting Evil games
            labels = ["Starting Good Games", "Starting Evil Games"]
            sizes = [startingGoodGames, startingEvilGames]
            plt.figure(figsize=(6, 6))
            plt.pie(sizes, labels=labels, autopct="%1.1f%%", colors=teamColours)
            plt.title("Starting Good vs Starting Evil Games")
            plt.tight_layout()
            plt.savefig("graphs/starting_good_vs_starting_evil_games.png")  # Save as image

            # Pie chart for Good Team Wins vs Evil Team Wins
            labels = ["Good Team Wins", "Evil Team Wins"]
            sizes = [goodTeamWins, evilTeamWins]
            plt.figure(figsize=(6, 6))
            plt.pie(sizes, labels=labels, autopct="%1.1f%%", colors=teamColours)
            plt.title("Good Team Wins vs Evil Team Wins")
            plt.tight_layout()
            plt.savefig("graphs/good_team_wins_vs_evil_team_wins.png")  # Save as image

            # Bar chart for Wins/Losses as Good vs Wins/Losses
            data = {'Team': ['Good Team', 'Evil Team'],
                    'Wins': [totalGoodWins, totalEvilWins],
                    'Losses': [(totalGoodGames - totalGoodWins), (totalEvilGames - totalEvilWins)]}
            df2 = pd.DataFrame(data)
            fig, ax = plt.subplots()
            df2.set_index('Team').plot(kind='bar', ax=ax)
            ax.set_title('Wins and Losses: Playing as Good vs Playing as Evil')
            ax.set_xlabel('Teams')
            ax.set_ylabel('Number of Games')
            plt.xticks(rotation=0)
            plt.legend(title='Results')
            plt.tight_layout()
            plt.savefig("graphs/wins_losses_alignment.png") # Save as image

            # Define a color map for character types
            characterTypeColours = {
                "Townsfolk": "blue",
                "Outsider": "skyblue",
                "Minion": "orange",
                "Demon": "red",
                "Traveller": "purple"
            }
            
            character_labels = ["Townsfolk", "Outsider", "Minion", "Demon", "Traveller"]
            pie_colours = []
            for label in character_labels:
                pie_colours.append(characterTypeColours[label]) 
            
            # Pie chart for character types played
            character_counts = [totalTownsfolkGames, totalOutsiderGames, totalMinionGames, totalDemonGames, totalTravellerGames]
            plt.figure(figsize=(6, 6))
            plt.pie(character_counts, labels=character_labels, colors=pie_colours, autopct='%1.1f%%', startangle=90)
            plt.title("Character Type Distribution")
            plt.tight_layout()
            plt.savefig("graphs/character_type_distribution.png")  # Save as image

            # Pie chart for starting character types
            starting_character_counts = [startingTownsfolkGames, startingOutsiderGames, startingMinionGames, startingDemonGames, startingTravellerGames]
            plt.figure(figsize=(6, 6))
            plt.pie(starting_character_counts, labels=character_labels, colors=pie_colours, autopct='%1.1f%%', startangle=90)
            plt.title("Starting Character Type Distribution")
            plt.tight_layout()
            plt.savefig("graphs/starting_character_type_distribution.png")  # Save as image

            #Bar chart for character types win/losses
            data = {'Team': character_labels,
                    'Wins': [totalTownsfolkWins,totalOutsiderWins,totalMinionWins,totalDemonWins,totalTravellerWins],
                    'Losses': [(totalTownsfolkGames - totalTownsfolkWins),(totalOutsiderGames - totalOutsiderWins),(totalMinionGames - totalMinionWins),(totalDemonGames - totalDemonWins),(totalTravellerGames- totalTravellerWins)]}
            df2 = pd.DataFrame(data)
            fig, ax = plt.subplots()
            df2.set_index('Team').plot(kind='bar', ax=ax)
            ax.set_title('Wins and Losses: Playing as different character types')
            ax.set_xlabel('Character Types')
            ax.set_ylabel('Number of Games')
            plt.xticks(rotation=0)
            plt.legend(title='Results')
            plt.tight_layout()
            plt.savefig("graphs/wins_losses_character_type.png") # Save as image

            # Pie chart for changes in alignment/character
            labels = ["No Changes", "Character Changed", "Alignment Change", "Character and Alignment Changed"]
            sizes = [int(df[(df["alignment_change"] == "False") & (df["character_change"] == "False")].shape[0]), int(df[(df["alignment_change"] == "False") & (df["character_change"] == "True")].shape[0]),int(df[(df["alignment_change"] == "True") & (df["character_change"] == "False")].shape[0]),int(df[(df["alignment_change"] == "True") & (df["character_change"] == "True")].shape[0])]
            plt.figure(figsize=(6, 6))
            plt.pie(sizes, labels=labels, autopct="%1.1f%%", colors=["green","purple","yellow","gray"])
            plt.title("Character/Alignment Change")
            plt.tight_layout()
            plt.savefig("graphs/character_alignment_change.png")  # Save as image

            #Dynamically generates bar colours based on the character types of the characters
            bar_colours = [characterTypeColours.get(findCharacterType(character), "gray") for character in charactersPlayed.index]
            
            # Bar chart for characters played
            plt.figure(figsize=(10, 6))
            plt.bar(charactersPlayed.index, charactersPlayed.values, color=bar_colours)
            plt.xticks(rotation=90)  # Rotate labels for readability
            plt.xlabel("Character")
            plt.ylabel("Number of Games")
            plt.title("Character Frequency Distribution")
            plt.tight_layout()
            plt.savefig("graphs/character_frequency.png")  # Save as image

            # Bar chart for starting characters
            plt.figure(figsize=(10, 6))
            plt.bar(startingCharactersPlayed.index, startingCharactersPlayed.values, color=bar_colours)
            plt.xticks(rotation=90)  # Rotate labels for readability
            plt.xlabel("Starting Character")
            plt.ylabel("Number of Games")
            plt.title("Starting Character Frequency Distribution")
            plt.tight_layout()
            plt.savefig("graphs/starting_character_frequency.png")  # Save as image

            # Defines script labels and colours
            script_labels = ["Trouble Brewing","Bad Moon Rising","Sects and Violets","Custom"]
            script_colours = ["red","yellow","purple","gray"]
            
            #Pie chart for script played
            sizes = [totalTBGames,totalBMRGames,totalSNVGames,totalCustomGames]
            plt.figure(figsize=(6, 6))
            plt.pie(sizes, labels=script_labels, autopct="%1.1f%%", colors=script_colours)
            plt.title("Scripts Played")
            plt.tight_layout()
            plt.savefig("graphs/scripts_played.png")  # Save as image

            #Bar chart for script win/losses
            data = {'script': script_labels,
                    'Wins': [TBGamesWon,BMRGamesWon,SNVGamesWon,CustomGamesWon],
                    'Losses': [(totalTBGames-TBGamesWon),(totalBMRGames - BMRGamesWon),(totalSNVGames - SNVGamesWon),(totalCustomGames - CustomGamesWon)]}
            df2 = pd.DataFrame(data)
            fig, ax = plt.subplots()
            df2.set_index('script').plot(kind='bar', ax=ax)
            ax.set_title('Wins and Losses: Playing different scripts')
            ax.set_xlabel('Script')
            ax.set_ylabel('Number of Games')
            plt.xticks(rotation=0)
            plt.legend(title='Results')
            plt.tight_layout()
            plt.savefig("graphs/wins_losses_scripts.png") # Save as image

            #Pie chart for alive/day_death/night_death
            labels = ["Survived","Died at Day","Died at Night"]
            sizes = [totalAliveGames,dayDeadGames,nightDeadGames]
            plt.figure(figsize=(6, 6))
            plt.pie(sizes, labels=labels, autopct="%1.1f%%", colors=script_colours)
            plt.title("Games survived vs Died at Day vs Died at Night")
            plt.tight_layout()
            plt.savefig("graphs/death_type.png")  # Save as image

            #Bar chart for dead/alive win/loss
            data = {'death_status': ["Alive", "Dead"],
                    'Wins': [aliveGamesWon,deadGamesWon],
                    'Losses': [(totalAliveGames-aliveGamesWon),(totalDeadGames-deadGamesWon)]}
            df2 = pd.DataFrame(data)
            fig, ax = plt.subplots()
            df2.set_index('death_status').plot(kind='bar', ax=ax)
            ax.set_title('Wins and Losses: Alive vs Dead')
            ax.set_xlabel('Alive or Dead')
            ax.set_ylabel('Number of Games')
            plt.xticks(rotation=0)
            plt.legend(title='Results')
            plt.tight_layout()
            plt.savefig("graphs/wins_losses_death_status.png") # Save as image

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

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