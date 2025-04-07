from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from handlers.preferiti import mostra_preferiti
from utils.user import get_user_db_connection, get_user_file, create_user_db

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "info":
        await info(update, context)
    elif data == "spesa":
        await query.message.reply_text("💸 Usa il comando:\n`/spesa importo descrizione`", parse_mode='Markdown')
    elif data == "entrata":
        await query.message.reply_text("💰 Usa il comando:\n`/entrata importo descrizione`", parse_mode='Markdown')
    elif data == "preferiti":
        await mostra_preferiti(update, context)
    else:
        await query.message.reply_text("❓ Opzione non riconosciuta.")

# Comando start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    first_name = user.first_name
    
    keyboard = [
        [InlineKeyboardButton("ℹ️ Info", callback_data='info')],
        [InlineKeyboardButton("💸  Spesa", callback_data='spesa')],
        [InlineKeyboardButton("💰 Entrata", callback_data='entrata')],
        [InlineKeyboardButton("⭐ Mostra preferiti", callback_data='preferiti')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Ciao {first_name}! 👋\nScegli un'opzione:", reply_markup=reply_markup)

# Comando info
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            "Usa il comando: /spesa importo descrizione per registrare una spesa.\n"
            "Usa il comando: /entrata importo descrizione per registrare un'entrata.\n"
            "Usa il comando: /resoconto per avere un resoconto delle tue ultime spese.\n"
            "Se ti sei sbagliato usa il comando /delete per eliminare l'ultimo movimento."
        )
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            "Usa il comando: /spesa importo descrizione per registrare una spesa.\n"
            "Usa il comando: /entrata importo descrizione per registrare un'entrata.\n"
            "Usa il comando: /resoconto per avere un resoconto delle tue ultime spese.\n"
            "Se ti sei sbagliato usa il comando /delete per eliminare l'ultimo movimento."
        )

# Comando per registrare una spesa
async def spesa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    create_user_db(user_id)

    if len(context.args) < 1:
        await update.message.reply_text("❌ Usa: /spesa importo descrizione")
        return

    try:
        importo = float(context.args[0])
        descrizione = ' '.join(context.args[1:]) or 'Sconosciuto'
        connection = get_user_db_connection(user_id)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO movimenti (data, tipo, importo, descrizione) VALUES (?, ?, ?, ?)",
                       (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'spesa', -importo, descrizione))
        connection.commit()
        cursor.close()
        connection.close()
        await update.message.reply_text(f"💸 Spesa registrata: {importo}€ - {descrizione}")
    except ValueError:
        await update.message.reply_text("❌ Importo non valido, usa un numero per l'importo.")

# Comando per registrare un'entrata
async def entrata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    create_user_db(user_id)

    if len(context.args) < 1:
        await update.message.reply_text("❌ Usa: /entrata importo descrizione")
        return

    try:
        importo = float(context.args[0])
        descrizione = ' '.join(context.args[1:]) or 'Sconosciuto'
        connection = get_user_db_connection(user_id)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO movimenti (data, tipo, importo, descrizione) VALUES (?, ?, ?, ?)",
                       (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'entrata', importo, descrizione))
        connection.commit()
        cursor.close()
        connection.close()
        await update.message.reply_text(f"💰 Entrata registrata: {importo}€ - {descrizione}")
    except ValueError:
        await update.message.reply_text("❌ Importo non valido, usa un numero per l'importo.")

# Comando per eliminare l'ultimo movimento
async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    create_user_db(user_id)

    # Connessione al database
    connection = get_user_db_connection(user_id)
    cursor = connection.cursor()

    # Trova l'ultimo movimento inserito
    cursor.execute("SELECT id FROM movimenti ORDER BY data DESC LIMIT 1")
    ultimo_movimento = cursor.fetchone()

    if not ultimo_movimento:
        await update.message.reply_text("❌ Non hai ancora registrato alcun movimento.")
        cursor.close()
        connection.close()
        return

    # Elimina l'ultimo movimento
    movimento_id = ultimo_movimento[0]
    cursor.execute("DELETE FROM movimenti WHERE id = ?", (movimento_id,))
    connection.commit()

    await update.message.reply_text("✅ Ultimo movimento eliminato con successo.")
    
    cursor.close()
    connection.close()

# Comando per visualizzare il resoconto
async def resoconto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    create_user_db(user_id)

    connection = get_user_db_connection(user_id)
    cursor = connection.cursor()

    cursor.execute("SELECT tipo, importo FROM movimenti")
    movimenti = cursor.fetchall()

    if not movimenti:
        await update.message.reply_text("❌ Non hai ancora registrato alcun movimento.")
        cursor.close()
        connection.close()
        return

    spese = entrate = 0
    for movimento in movimenti:
        if movimento[0] == 'entrata':
            entrate += movimento[1]
        elif movimento[0] == 'spesa':
            spese += abs(movimento[1])

    saldo = entrate - spese
    await update.message.reply_text(
        f"📊 Resoconto:\n"
        f"Totale entrate: {entrate:.2f}€\n"
        f"Totale spese: {spese:.2f}€\n"
        f"Saldo: {saldo:.2f}€"
    )

    cursor.close()
    connection.close()
