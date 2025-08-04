import csv
from collections import Counter
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from config import TELEGRAM_TOKEN, DUMP_FILE

def load_data():
    data = []
    with open(DUMP_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                "phone_number": row["phone_number"].strip(),
                "name": row["name"].strip(),
                "source": row["source"].strip()
            })
    return data

def lookup_number(number, data):
    matches = [entry for entry in data if entry["phone_number"] == number]
    if not matches:
        return None

    names = [entry["name"].lower() for entry in matches]
    count = Counter(names)
    top_name, freq = count.most_common(1)[0]
    alt_names = [f"{name} ({c})" for name, c in count.items() if name != top_name]
    sources = list({entry["source"] for entry in matches})
    return {
        "top_name": top_name,
        "frequency": freq,
        "alternatives": alt_names,
        "sources": sources
    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Willkommen beim Nummern-Info-Bot!\nBitte sende eine Telefonnummer im internationalen Format (z. B. +49176...).")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()
    data = load_data()
    result = lookup_number(number, data)

    if result:
        response = f"""📞 Nummer: {number}
👤 **Name:** {result["top_name"]} ({result["frequency"]} Treffer)

📚 Weitere Namen:
• {'\n• '.join(result['alternatives']) if result['alternatives'] else 'Keine'}

🔎 Quellen: {', '.join(result['sources'])}
"""
    else:
        response = f"⚠️ Keine Infos zur Nummer **{number}** gefunden."

    await update.message.reply_markdown(response)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
