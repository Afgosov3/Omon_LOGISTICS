from django.core.management.base import BaseCommand
import asyncio
import os
from aiogram import Bot, Dispatcher
from telegram_bot.handlers.user_handlers import router as user_router
from telegram_bot.handlers.driver_handlers import router as driver_router
from telegram_bot.handlers.customer_handlers import router as customer_router

class Command(BaseCommand):
    help = 'Run the Telegram bot'

    def handle(self, *args, **options):
        # We need to run async code from sync handle method

        async def main():
            token = os.getenv("BOT_TOKEN")
            if not token:
                self.stdout.write(self.style.ERROR("BOT_TOKEN not found!"))
                return

            try:
                bot = Bot(token=str(token))
                dp = Dispatcher()

                # Register routers
                dp.include_router(user_router)
                dp.include_router(driver_router)
                dp.include_router(customer_router)

                self.stdout.write(self.style.SUCCESS("Bot started polling..."))
                await dp.start_polling(bot)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Bot error: {e}"))

        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            self.stdout.write("Bot stopped.")

