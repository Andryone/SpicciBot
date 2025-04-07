from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.user import get_user_db_connection, create_user_db
from datetime import datetime

async def aggiungi_preferito(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Verifica che ci sia un messaggio
    if update.message is None:
        await update.callback_query.message.reply_text("❌ Questo comando può essere usato solo con un messaggio di testo.")
        return

    user_id = update.message.from_user.id
    create_user_db(user_id)

    if len(context.args) < 4:  # Cambia per richiedere anche il tipo
        await update.message.reply_text("❌ Usa: /aggiungi_preferito alias tipo importo descrizione")
        return

    alias = context.args[0]
    tipo = context.args[1].lower()  # Tipo può essere 'spesa' o 'entrata'
    if tipo not in ['spesa', 'entrata']:
        await update.message.reply_text("❌ Il tipo deve essere 'spesa' o 'entrata'.")
        return

    try:
        importo = float(context.args[2])
    except ValueError:
        await update.message.reply_text("❌ Importo non valido. Usa un numero per l'importo.")
        return

    descrizione = ' '.join(context.args[3:])

    connection = get_user_db_connection(user_id)
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO preferiti (alias, importo, descrizione, tipo)
        VALUES (?, ?, ?, ?)
    ''', (alias, importo, descrizione, tipo))
    connection.commit()
    cursor.close()
    connection.close()

    await update.message.reply_text(f"✅ Preferito aggiunto: {alias} - {importo}€ ({tipo})")

async def mostra_preferiti(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = None
    if update.message:
        user = update.message.from_user
        reply_markup = InlineKeyboardMarkup([[]])  # Placeholder per un eventuale reply_markup vuoto
    elif update.callback_query:
        await update.callback_query.answer()  # Rispondi al callback (obbligatorio per non far restare il bot in attesa)
        user = update.callback_query.from_user
        reply_markup = InlineKeyboardMarkup([[]])  # Placeholder per un eventuale reply_markup vuoto

    if user is None:
        print("Nessun utente trovato nell'update.")
        return

    user_id = user.id

    # Crea il database utente se non esiste
    create_user_db(user_id)

    # Ottieni i preferiti dell'utente dal database
    connection = get_user_db_connection(user_id)
    cursor = connection.cursor()
    cursor.execute('SELECT alias, importo, descrizione, tipo FROM preferiti')
    preferiti = cursor.fetchall()
    cursor.close()
    connection.close()

    # Verifica se l'utente ha preferiti salvati
    if not preferiti:
        # Se non ha preferiti, invia un messaggio
        if update.message:
            await update.message.reply_text("❌ Non hai ancora aggiunto preferiti.")
        return

    # Crea la tastiera con i preferiti
    keyboard = []
    for alias, importo, descrizione, tipo in preferiti:
        button_text = f"{alias} | {importo}€ ({tipo})"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"aggiungi_preferito_{alias}")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Rispondi con il messaggio e la tastiera
    if update.message:
        await update.message.reply_text("Scegli un preferito:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("Scegli un preferito:", reply_markup=reply_markup)

# Comando per eliminare un preferito
async def elimina_preferito(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("❌ Usa: /elimina_preferito alias")
        return

    alias = context.args[0]
    user_id = update.message.from_user.id
    create_user_db(user_id)

    connection = get_user_db_connection(user_id)
    cursor = connection.cursor()

    # Controlla se esiste il preferito con l'alias specificato
    cursor.execute('SELECT id FROM preferiti WHERE alias = ?', (alias,))
    preferito = cursor.fetchone()

    if not preferito:
        await update.message.reply_text(f"❌ Preferito con alias '{alias}' non trovato.")
        cursor.close()
        connection.close()
        return

    # Elimina il preferito dal database
    cursor.execute('DELETE FROM preferiti WHERE alias = ?', (alias,))
    connection.commit()

    await update.message.reply_text(f"✅ Preferito con alias '{alias}' eliminato con successo.")

    cursor.close()
    connection.close()

# Funzione che gestisce l'aggiunta di un movimento dai preferiti
async def aggiungi_movimento_dai_preferiti(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Estrai l'alias dal callback_data
    alias = query.data.split('_')[2]

    user_id = query.from_user.id
    create_user_db(user_id)

    connection = get_user_db_connection(user_id)
    cursor = connection.cursor()
    
    cursor.execute('SELECT alias, importo, descrizione, tipo FROM preferiti WHERE alias = ?', (alias,))
    preferito = cursor.fetchone()
    
    cursor.close()
    connection.close()

    if not preferito:
        await query.message.reply_text("❌ Preferito non trovato.")
        return

    # Decomponi la tupla con alias, importo, descrizione e tipo
    alias_preferito, importo, descrizione, tipo = preferito

    # Aggiunge il movimento al database dei movimenti
    connection = get_user_db_connection(user_id)
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO movimenti (data, tipo, importo, descrizione)
        VALUES (?, ?, ?, ?)
    ''', (datetime.now(), tipo, importo, descrizione))
    connection.commit()
    cursor.close()
    connection.close()

    await query.message.reply_text(f"✅ Movimento aggiunto: {importo}€ - {descrizione} ({tipo})")
