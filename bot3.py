import os
import time
import asyncio
try:
    import telebot
    from db import *
    from chkr import chkcc
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    from telebot.async_telebot import AsyncTeleBot
except ModuleNotFoundError as e:
    module = str(e).split("'")[1]
    print('[+] Installing required module:', module)
    os.system(f'pip install {module}')
    import telebot
    from db import *
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    from telebot.async_telebot import AsyncTeleBot
    from chkr import chkcc
    import asyncio


# === Config ===
BOT_TOKEN = "7984451878:AAG4W5_xseIPB1GC7K93NbYbeGqB0bwXe3g"  # BOT_TOKEN
OWNER_ID = int("6439657046")  # TG_ID

# === Bot Initialization ===
bot = AsyncTeleBot(BOT_TOKEN, parse_mode="Markdown")

# === State Variables ===
stats = {"total": 0, "hit": 0, "dead": 0}
proxy_settings = ""
stop_flag = {"stop": False}


def set_proxy(proxy_url):
    global proxy_settings
    if proxy_url.startswith('http://') or proxy_url.startswith('https://'):
        proxy_settings = proxy_url
    else:
        proxy_settings = f"http://{proxy_url}"
    return "Proxy has been changed ✅"


def update_stats(category):
    if category in stats:
        stats[category] += 1


@bot.message_handler(commands=["stop"])
async def handle_stop(message):
    stop_flag["stop"] = True
    await bot.reply_to(message, "Process stopped!")


@bot.message_handler(commands=["start"])
async def handle_start(message):
    if not get_user(message.chat.id):
        return await bot.send_message(message.chat.id, "*Access denied ❌*")
    name = message.from_user.first_name
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("• Stripe Checker •", callback_data="0")]
    ])
    await bot.send_message(message.chat.id, f"**Hi {name}. This is ASUNA 2.0 🔥**", reply_markup=keyboard)


@bot.message_handler(commands=["rmproxy"])
async def handle_rmoxy(message):
    if not get_user(message.chat.id):
        return await bot.send_message(message.chat.id, "*Access denied ❌*")
    global proxy_settings
    proxy_settings = ""
    await bot.send_message(message.chat.id, "Proxy has been removed ✅")


@bot.message_handler(commands=["proxy"])
async def handle_proxy(message):
    if not get_user(message.chat.id):
        return await bot.send_message(message.chat.id, "*Access denied ❌*")

    parts = message.text.split(' ')
    if len(parts) < 2:
        return await bot.send_message(message.chat.id, "Error! Please provide a proxy as `User:Pass@IP:Port`")

    proxy_url = parts[1]
    result = set_proxy(proxy_url)
    await bot.send_message(message.chat.id, result)


@bot.message_handler(commands=['xprxy'])
async def handle_check_proxy(message):
    if not get_user(message.chat.id):
        return await bot.send_message(message.chat.id, "*Access denied ❌*")

    if proxy_settings:
        await bot.send_message(message.chat.id, f"Current proxy: `{proxy_settings}`")
    else:
        await bot.send_message(message.chat.id, "No proxy set. Use /proxy command to set one.")


@bot.message_handler(commands=['add'])
async def handle_add_user(message):
    if message.chat.id != OWNER_ID:
        return await bot.send_message(message.chat.id, "*Access denied ❌*")
    try:
        user_id = message.text.split(' ')[1]
        add_user(user_id)
        await bot.send_message(message.chat.id, f"User {user_id} added!")
    except IndexError:
        await bot.send_message(message.chat.id, "Error! Please provide a user ID.")


@bot.message_handler(commands=['remove'])
async def handle_remove_user(message):
    if message.chat.id != OWNER_ID:
        return await bot.send_message(message.chat.id, "*Access denied ❌*")
    try:
        user_id = message.text.split(' ')[1]
        remove_user(user_id)
        await bot.send_message(message.chat.id, f"User {user_id} removed!")
    except IndexError:
        await bot.send_message(message.chat.id, "Error! Please provide a user ID.")


async def call_checker(card):
    global proxy_settings
    try:
        card = str(card).replace('/', '|').replace(' ', '|')
        response = await chkcc(card, proxy_settings)
        result_lower = str(response).lower()

        if 'success' in result_lower or 'true' in result_lower:
            update_stats("hit")
            return f"✅ *Live* : `{card}`\n\n\n*Respo* : {response}"

        elif 'insufficient' in result_lower:
            update_stats("hit")
            return f"⚠ *{card}* — *{response}*"

        elif any(x in result_lower for x in ['failed', 'error', 'invalid', 'incorrect', 'declined']):
            update_stats("dead")
            return "Dead"

        else:
            update_stats("dead")
            return f"❌ *{response}*"

    except Exception as e:
        update_stats("dead")
        return f"Error checking card: {card}\nReason: {str(e)}"


@bot.message_handler(commands=['chk'])
async def handle_single_check(message):
    if not get_user(message.chat.id):
        return await bot.send_message(message.chat.id, "*Access denied FOOL ❌*")

    try:
        global proxy_settings
        card = message.text.split(None, 1)[1]
        card = str(card).replace('/', '|').replace(' ', '|')
        response = await chkcc(card, proxy_settings)
        res_text = str(response).lower()

        if any(word in res_text for word in ['success', 'insufficient', 'true', 'done']):
            return await bot.send_message(
                message.chat.id,
                f"✅ *Live* : `{card}`\n*Respo* : {response}"
            )
        elif any(word in res_text for word in ['declined']):
            return await bot.send_message(
                message.chat.id,
                f"❌ {response}"
            )
        elif any(word in res_text for word in ['failed', 'error', 'invalid']):
            return await bot.send_message(
                message.chat.id,
                f"⚠ {response}"
            )
        else:
            return await bot.send_message(
                message.chat.id,
                f"❌ *{response}*"
            )

    except IndexError:
        return await bot.send_message(message.chat.id, "Error! Please provide a card.")
    except Exception as e:
        return await bot.send_message(message.chat.id, f"❌ An error occurred: `{str(e)}`")


@bot.message_handler(content_types=["document"])
async def handle_file_upload(message):
    if not get_user(message.chat.id):
        return await bot.send_message(message.chat.id, "*Access denied ❌*")

    user_name = message.from_user.first_name
    notify = await bot.send_message(message.chat.id, '**__⚡ Processing...__**')
    file_info = await bot.get_file(message.document.file_id)
    file_data = await bot.download_file(file_info.file_path)

    with open("combos.txt", "wb") as f:
        f.write(file_data)

    with open("combos.txt", "r") as f:
        cards = [line.strip() for line in f if line.strip()]
        stats.update({"total": len(cards), "hit": 0, "dead": 0})
        checked = 0

        for card in cards:
            if stop_flag["stop"]:
                break

            result = await call_checker(card)
            checked += 1

            if result and 'Live' in result:
                with open("hits.txt", "a", encoding="utf-8") as hitfile:
                    hitfile.write(f"{card}|{result}\n")
            
            progress_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"• {card} •", callback_data="0")],
                [InlineKeyboardButton(f"• Hit ✅ : [ {stats['hit']} ] •", callback_data="0"),
                 InlineKeyboardButton(f"• Dead ❌ : [ {stats['dead']} ] •", callback_data="0")],
                [InlineKeyboardButton(f"• Checked ☑️ : [ {checked} ] •", callback_data="0"),
                 InlineKeyboardButton(f"• Total 🔥 : [ {stats['total']} ] •", callback_data="0")]
            ])

            try:
                await bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=notify.message_id,
                    text=f"HELLO {user_name}, PLEASE BE PATIENT COMRADE.",
                    reply_markup=progress_markup
                )
            except:
                pass

            await asyncio.sleep(1)

    await asyncio.sleep(2)

    summary_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Done ✅", callback_data="0")]])
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=notify.message_id,
        text=f'*_Stripe Checker_\n\nHit ✅:* `{stats["hit"]}` *| Dead ❌:* `{stats["dead"]}` *| Total🔥:* `{stats["total"]}`\n\n\n*@mayberetarded*',
        reply_markup=summary_markup
    )

    if os.path.exists('hits.txt'):
        with open('hits.txt', 'rb') as hits_file:
            await bot.send_document(message.chat.id, hits_file)
        os.remove("hits.txt")
    if os.path.exists("combos.txt"):
        os.remove("combos.txt")

    stats.update({"total": 0, "hit": 0, "dead": 0})
    stop_flag["stop"] = False


@bot.callback_query_handler(func=lambda call: True)
async def handle_callback(call):
    await bot.answer_callback_query(call.id, text="Processing...")


# === Bot Runner ===
if __name__ == "__main__":
    async def mainxc():
        try:
            print("Script Working!\n  by @mayberetarded")
            await bot.infinity_polling()
        except KeyboardInterrupt:
            print("Script Stopped by User!")
        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            print("Restarting in 5 seconds...")
            await asyncio.sleep(5)
            await mainxc()
    
    asyncio.run(mainxc())