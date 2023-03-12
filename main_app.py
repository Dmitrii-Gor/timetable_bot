from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, KeyboardButtonColor, Text, CtxStorage, BaseStateGroup
from SHEETS import Sheets
import days
import os


bot = Bot(token=os.getenv('TOKEN'))


user_keyboard = (
    Keyboard(inline=True)
        .add(Text("Всё"), color=KeyboardButtonColor.PRIMARY)
)

ctx = CtxStorage()  # Хранилище для FSM


class SetParams(BaseStateGroup):
    DAY_TABLE = 0
    USER_ID = 1
    SCHEDULE = 2
    DAY_GET_TABLE = 3


@bot.on.message(lev='Добавить расписание')
async def add_schedule(message: Message):
    ctx.set('user_id', message.from_id)
    await message.answer('Напишите день недели (пишите название дня целиком)')
    await bot.state_dispenser.set(message.peer_id, SetParams.DAY_TABLE)


@bot.on.message(state=SetParams.DAY_TABLE)
async def day_info(message: Message):
    if message.from_id == ctx.get('user_id'):
        if message.text.lower() in days.days:
            ctx.set('day', message.text)
            await bot.state_dispenser.set(message.peer_id, SetParams.SCHEDULE)
            return 'Начинайте писать своё расписание. Если есть пары по разным неделям, просто укажите "Чётная неделя: пара" "Нечетная неделя: пара" одним сообщением'
        else:
            return 'Попробуйте написать день недели ещё раз. Если вы указали воскресенье, то не стоит, в этот день нужно отдыхать'


@bot.on.message(state=SetParams.SCHEDULE)
async def schedule_update(message: Message):
    sheets_class = Sheets(doc='my new sheet', user_id=message.peer_id)
    if message.from_id == ctx.get('user_id'):
        if 'Всё' not in message.text:
            text = message.text
            one_line_text = text.replace('\n', ' ')
            with open(f"{ctx.get('user_id')}.txt", "a", encoding='utf-8') as file:
                file.write(f"{one_line_text}\n")
            await message.answer('Пишите дальше, либо нажмите на кнопку', keyboard=user_keyboard)
        else:
            with open(f"{ctx.get('user_id')}.txt", "r", encoding='utf-8') as file:
                list_on_info = []
                for iteration in file:
                    list_on_info.append(iteration)
                sheets_class.update_sheet_info(day_of_week=ctx.get('day'), cells_list=list_on_info)
            os.remove(f'{message.from_id}.txt')
            await message.answer('Расписание сохранено, если хотите продолжить, опять напишите "Добавить расписание"')
            await bot.state_dispenser.delete(message.peer_id)


@bot.on.message(lev='Бот расписание')
async def add_schedule(message: Message):
    await message.answer('Напишите день недели (все дни писать целиком)')
    await bot.state_dispenser.set(message.peer_id, SetParams.DAY_GET_TABLE)


@bot.on.message(state=SetParams.DAY_GET_TABLE)
async def day_info(message: Message):
    sheets_class = Sheets(doc='my new sheet', user_id=message.peer_id)
    lower_msg = message.text.lower()
    if lower_msg in days.days:
        info = sheets_class.show_table_info(day_of_week=lower_msg)
        for list_of_lists in info:
            for information in list_of_lists:
                await message.answer(f'{information}')
        await bot.state_dispenser.delete(message.peer_id)
    else:
        return 'Введите день недели правильно'


bot.run_forever()
