import os 
import sqlite3

PATH = '/Users/andrea/Desktop/Spicci_Bot/db'

def get_user_file(user_id):
    return os.path.join(PATH, f'{user_id}_movimenti.csv')

# Funzione per creare la connessione al database per ogni utente
def get_user_db_connection(user_id):
    db_path = os.path.join(PATH, f'{user_id}_movimenti.db')
    return sqlite3.connect(db_path)

# Crea la tabella dei movimenti nel database
def create_movements_table(user_id):
    connection = get_user_db_connection(user_id)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            tipo TEXT NOT NULL,
            importo REAL NOT NULL,
            descrizione TEXT NOT NULL
        )
    ''')
    connection.commit()
    cursor.close()
    connection.close()

# Crea la tabella dei preferiti nel database
def create_favorites_table(user_id):
    connection = get_user_db_connection(user_id)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preferiti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alias TEXT NOT NULL,
            importo REAL NOT NULL,
            descrizione TEXT NOT NULL,
            tipo TEXT NOT NULL  -- Aggiungi il tipo (spesa o entrata)
        )
    ''')
    connection.commit()
    cursor.close()
    connection.close()

# Funzione per creare il database e le tabelle per un utente se non esistono
def create_user_db(user_id):
    create_movements_table(user_id)
    create_favorites_table(user_id)