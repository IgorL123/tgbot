from telethon import TelegramClient, events, Button
import logging

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

api_id = ''
api_hash = ""
bot_token = ''

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
buttons = [
    [Button.inline('Экономика и финансы', b'economy')],
    [Button.inline('Политика', b'politics')],
    [Button.inline('Технологии и наука', b'tech')],
    [Button.inline('Бизнес', b'business')],
    [Button.inline('Образование и саморазвитие', b'education')],
    [Button.inline('Искусство и мода', b'art')],
    [Button.inline('Спорт', b'sport')]
]
@bot.on(events.CallbackQuery)
async def handler(event):
    if event.data == b'economy':
        await event.answer('Успешно')


@bot.on(events.NewMessage)
async def meh(event):
    sender = await event.get_sender()
    if '/start' in event.raw_text:
        await bot.send_message(sender, "Выберете категории:", buttons=buttons)

    else:
        from_peer = await bot.get_input_entity('bitkogan')
        await bot.forward_messages(sender, 8717, from_peer)


bot.start()
bot.run_until_disconnected()