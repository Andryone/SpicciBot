import os
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from handlers.commands import start,info,spesa,entrata,delete,resoconto,buttons
from handlers.preferiti import aggiungi_preferito, mostra_preferiti, elimina_preferito, aggiungi_movimento_dai_preferiti

# Carica il token dal file .env
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Inizializzazione dell'app Telegram
app = ApplicationBuilder().token(TOKEN).build()

# Aggiungi gli handler
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("info", info))
app.add_handler(CommandHandler("spesa", spesa))
app.add_handler(CommandHandler("entrata", entrata))
app.add_handler(CommandHandler("delete", delete))
app.add_handler(CommandHandler("resoconto", resoconto))

# Aggiungi gli handler
app.add_handler(CommandHandler("aggiungi_preferito", aggiungi_preferito))
app.add_handler(CommandHandler("mostra_preferiti", mostra_preferiti))
app.add_handler(CommandHandler("elimina_preferito", elimina_preferito))

app.add_handler(CallbackQueryHandler(aggiungi_movimento_dai_preferiti, pattern="^aggiungi_preferito_"))

app.add_handler(CallbackQueryHandler(buttons))

try:
    print('Avvio bot...')
    app.run_polling()
except Exception as e:
    print(f"Errore durante l'esecuzione del bot: {e}")
