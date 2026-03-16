import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

TOKEN = "8783119872:AAEhWqeQi-WBeNMq3WexW7rP1HmvFXwABow"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

scheduler = AsyncIOScheduler()
scheduler.start()

jobs = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Telegram Scheduler Bot\n\n"
        "Commands:\n"
        "/schedule YYYY-MM-DD HH:MM message\n"
        "/list\n"
        "/cancel job_id"
    )


async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        date = context.args[0]
        time = context.args[1]
        message = " ".join(context.args[2:])

        schedule_time = datetime.strptime(
            f"{date} {time}", "%Y-%m-%d %H:%M"
        )

        chat_id = update.effective_chat.id

        job = scheduler.add_job(
            send_message,
            "date",
            run_date=schedule_time,
            args=[context, chat_id, message]
        )

        jobs[job.id] = job

        await update.message.reply_text(
            f"✅ Scheduled!\nJob ID: {job.id}"
        )

    except:
        await update.message.reply_text(
            "❌ Usage:\n/schedule 2026-03-20 18:30 Hello World"
        )


async def send_message(context, chat_id, message):
    await context.bot.send_message(
        chat_id=chat_id,
        text=message
    )


async def list_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not jobs:
        await update.message.reply_text("No scheduled posts.")
        return

    text = "📅 Scheduled Posts:\n"

    for job_id, job in jobs.items():
        text += f"\nID: {job_id}\nTime: {job.next_run_time}\n"

    await update.message.reply_text(text)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    job_id = context.args[0]

    if job_id in jobs:
        jobs[job_id].remove()
        del jobs[job_id]
        await update.message.reply_text("❌ Job Cancelled")
    else:
        await update.message.reply_text("Job ID not found")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("schedule", schedule))
app.add_handler(CommandHandler("list", list_jobs))
app.add_handler(CommandHandler("cancel", cancel))

print("Bot running...")

app.run_polling()
