import sqlite3

#Connects to database
Connection = sqlite3.connect('botc_database.db')

#Activates cursor for connections
cursor = Connection.cursor()
print("Successfully Connected to SQLite")
        
#Creates table if it doesn't already exist
sqlite_create_table_query = '''CREATE TABLE if not exists Games (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            character text NOT NULL,
                            alignment text NOT NULL,
                            win text NOT NULL);'''
cursor.execute(sqlite_create_table_query)
Connection.commit()

def insertData(character,alignment,win):
    '''
    Inserts data into the Games table
    character (text): Player's character
    alignment (text): Player's alignment
    win (bool): Player's win status
    '''
    #Implements input validation to prevent sql injections and invalid data
    if character == None or alignment == None or win == None:
        print("Please provide all required parameters")
        return
    elif alignment not in ['Good', 'Evil']:
        print("Alignment must be either 'Good' or 'Evil'")
        return
    elif win not in ['True', 'False']:
        print("Win must be either 'True' or 'False'")
        return
    elif not isinstance(character, str):
        print("Character must be a string")
        return
    elif len(character) > 20:
        print("Character name must be less than 20 characters")
        return
    elif ['<', '>', '/', '\\', ':', '*', '?', '"', '|', '!', '@', '#', '$', '%', '^', '&', '(', ')',' '] in character:
        print("Character name must not contain special characters or spaces")
        return
    elif character.isalpha() == False:
        print("Character name must contain only letters")
        return
    
    #Capitalizes variables
    character = character.capitalize()
    alignment = alignment.capitalize()
    win = win.capitalize()

    try:
        #Paramatises insert to prevent sql injections
        sqlite_insert_with_param = """INSERT INTO Games
                        (character,alignment,win) 
                        VALUES (?, ?, ?);"""
        
        #Inserts data into table
        data = (character,alignment,win)
        cursor.execute(sqlite_insert_with_param, data)
        Connection.commit()
        print("Information successfully committed")
    except sqlite3.Error as error:
        #Prints error message if insert fails
        print("Error while inserting data into SQLite table", error)

#Closes connection
cursor.close()
Connection.close()
print("SQLite connection is closed")