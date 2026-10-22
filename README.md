# Instagram Username Generator Telegram Bot

## Features
- Telegram bot with `/start` and `/generate`
- Generates username suggestions using patterns inspired by the supplied script
- Adds Instagram profile links so users can check manually
- Does not automate requests to Instagram's account-creation endpoint or claim a username is available

## Deploy
1. Create a bot with `@BotFather` in Telegram and copy its token.
2. Upload this folder to a Python worker hosting service (for example Render, Railway, or a VPS).
3. Set the environment variable `BOT_TOKEN` to your bot token in the hosting dashboard.
4. Set the start command to `python bot.py` (or use the included `Procfile` on a compatible host).
5. Deploy. You do not need to open Python on your phone or computer after deployment.

Never put your bot token in a public file or send it in chat. Availability cannot be confirmed reliably from a profile link alone.
