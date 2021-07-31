import config
from pytils import numeral
import datetime
import pytz
from user import User
from event import Event
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackQueryHandler

users = dict()
info_message = (f"У меня можно:\n"
                f"/info - посмотреть все команды\n"
                f"/timer - поставить таймер\n"
                f"/newnote - оставить заметку с тегом, по которому её можно будет найти\n"
                f"/newevent - создать новое мероприятие, о котором придёт напоминание в нужное время\n"
                f"/notes - получить все заметки\n"
                f"/getnote - получить заметку по тегу\n"
                f"/delnote - удалить заметку по тегу\n"
                f"/delallnotes - удалить все заметки\n"
                f"/getevent - узнать мероприятие по названию\n"
                f"/delevent - удалить мероприятие по названию\n"
                f"/events - узнать все предстоящие мероприятия\n"
                f"/todayevents - узнать мероприятия на сегодня\n"
                f"/tomorrowevents - узнать мероприятия на завтра\n"
                f"/nearevents - узнать мероприятия на несколько ближайших дней\n"
                f"/rangeevents - узнать мероприятия в определённом диапазоне\n"
                )


def create_reply_markup(tab):
    keyboard = []
    for row in tab:
        line = []
        for el in row:
            line.append(KeyboardButton(el))
        keyboard.append(line)
    return ReplyKeyboardMarkup(keyboard)


def create_inline_markup(tab):
    keyboard = []
    for row in tab:
        line = []
        for pair in row:
            line.append(InlineKeyboardButton(pair[0], callback_data=pair[1]))
        keyboard.append(line)
    return InlineKeyboardMarkup(keyboard)


def keyboard_regulate(update: Update, context):
    query = update.callback_query
    cur_callback = query.data
    chat_id = update.effective_message.chat_id
    if not (cur_callback in ("on the moment", "in 15 min", "in 30 min", "in 1 hour", "in 2 hour", "in 4 hour",
                             "in 1 day", "in 2 day", "in 1 week")):
        query.edit_message_text(update.effective_message.text)
    if cur_callback == "delete":
        users[chat_id].notes.clear()
        write_message(update, context, "Все заметки были удалены")
    elif cur_callback == "not delete":
        write_message(update, context, "Заметки не были удалены")
    elif cur_callback in ("once", "every day", "every week", "some days of week", "every month", "own period"):
        users[chat_id].per_event = cur_callback
        context.bot.send_message(
            chat_id=chat_id,
            text="Когда мне следует отправить тебе напоминание о событии?",
            reply_markup=create_inline_markup(
                [[["В момет начала", "on the moment"], ["За 15 минут", "in 15 min"], ["За 30 минут", "in 30 min"]],
                 [["За 1 час", "in 1 hour"], ["За 2 часа", "in 2 hour"], ["За 4 часа", "in 4 hour"]],
                 [["За 1 день", "in 1 day"], ["За 2 дня", "in 2 day"], ["За 1 неделю", "in 1 week"]],
                 [["Завершить выбор", "end of set remind"]]])
        )
    elif cur_callback in ("on the moment", "in 15 min", "in 30 min", "in 1 hour", "in 2 hour", "in 4 hour",
                          "in 1 day", "in 2 day", "in 1 week"):
        time_to_delta = {"on the moment": datetime.timedelta(), "in 15 min": datetime.timedelta(minutes=15),
                         "in 30 min": datetime.timedelta(minutes=30), "in 1 hour": datetime.timedelta(hours=1),
                         "in 2 hour": datetime.timedelta(hours=2), "in 4 hour": datetime.timedelta(hours=4),
                         "in 1 day": datetime.timedelta(days=1), "in 2 day": datetime.timedelta(days=2),
                         "in 1 week": datetime.timedelta(weeks=1)}
        users[chat_id].remind_list.append(time_to_delta[cur_callback])
    elif cur_callback == "end of set remind":
        period_of_event(update, context)


def write_message(update: Update, context, msg, markup=None):
    context.bot.send_message(
        chat_id=update.effective_message.chat_id,
        text=msg,
        parse_mode="Markdown",
        reply_markup=markup
    )


def morning_message(context):
    chat_id = context.job.context
    td = datetime.date.today()
    context.bot.send_sticker(
        chat_id=chat_id,
        sticker="CAACAgIAAxkBAAECpxBhAaiGCkZAMdPRZ8gvKB3LsGfr1QACzQwAAqUhEUmzoXEZN86HmSAE"
    )
    context.bot.send_message(
        chat_id=chat_id,
        text=f"Доброе утро! Напомню о твоих планах на сегодня и завтра.\n" +
             users[chat_id].get_events_in_range(td, td + datetime.timedelta(days=1)),
        parse_mode="Markdown"
    )


def start(update: Update, context):
    chat_id = update.effective_message.chat_id
    user_name = update.effective_user.first_name
    if users.get(chat_id) is None:
        users[chat_id] = User(chat_id, user_name)
        write_message(update, context, f"Привет, {user_name}! Меня зовут *Tими Тэйбл*.\n"
                                       f"Я буду твоим помощником в планировании расписания.\n{info_message}"
                      )
        write_message(update, context, f"Для начала давай определимся с твоим часовым поясом. "
                                       f"Сколько у тебя сейчас полных часов в формате 24 часа?")
        users[chat_id].next_command = set_timezone
        print(user_name, update.effective_user.last_name, chat_id)
    else:
        write_message(update, context, f"Привет, мы с тобой уже знакомы.\n{info_message}")
        users[chat_id].next_command = info


def set_timezone(update: Update, context):
    chat_id = update.effective_message.chat_id
    try:
        user_hours = int(update.effective_message.text)
        bot_hours = datetime.datetime.now(pytz.utc).hour
        delta = (user_hours - bot_hours) % 24
        users[chat_id].timezone = datetime.timedelta(hours=delta)
        context.job_queue.run_daily(morning_message,
                                    datetime.time(hour=((8 - delta) % 24)),
                                    context=chat_id)
    except ValueError:
        write_message(update, context, f"Неверный формат ввода, давай ещё раз."
                                       f"Сколько у тебя сейчас полных часов без минут?")
        users[chat_id].next_command = set_timezone
        return
    tz = str(delta) + " UTC"
    if delta >= 0:
        tz = '+' + tz
    write_message(update, context,
                  f"Часовой пояс {tz} установлен. У тебя также есть клавиатура с несколькими запросами",
                  create_reply_markup([['Справка', 'Таймер'],
                                       ['Новая заметка', 'Все заметки'],
                                       ['Новое событие', 'Все события'],
                                       ['События на сегодня', 'События на завтра', 'Ближайшие события']])
                  )
    users[chat_id].next_command = info


def info(update: Update, context):
    write_message(update, context, info_message)
    users[update.effective_message.chat_id].next_command = info


def new_note(update: Update, context):
    chat_id = update.effective_message.chat_id
    write_message(update, context, "Напиши *Тег* заметки, а со следующего абзаца - саму заметку")
    users[chat_id].next_command = create_note


def create_note(update: Update, context):
    text = update.effective_message.text.split('\n', 1)
    chat_id = update.effective_message.chat_id
    text[0] = text[0].strip()
    text.append('Пусто')
    if users[chat_id].notes.get(text[0]) is None:
        users[chat_id].notes[text[0]] = '_' + text[1] + '_'
    else:
        write_message(update, context, f"Заметка с таким тегом уже есть\n"
                                       f"{users[chat_id].notes[text[0]]}")
        users[chat_id].next_command = info
        return
    write_message(update, context, "Заметка успешно добавлена")
    users[chat_id].next_command = info


def notes(update: Update, context):
    chat_id = update.effective_message.chat_id
    if len(users[chat_id].notes) == 0:
        write_message(update, context, "Список заметок пуст")
    else:
        msg = "Все заметки:"
        for k, v, in users[chat_id].notes.items():
            msg += "\n*Тег*: " + k + '\n' + v + '\n'
        write_message(update, context, msg)
    users[chat_id].next_command = info


def tag_note(update: Update, context):
    write_message(update, context, "Напиши *Тег* заметки")
    chat_id = update.effective_message.chat_id
    if update.effective_message.text == "/getnote":
        users[chat_id].next_command = get_tag_note
    elif update.effective_message.text == "/delnote":
        users[chat_id].next_command = del_tag_note


def get_tag_note(update: Update, context):
    tag = update.effective_message.text.strip()
    chat_id = update.effective_message.chat_id
    text = users[chat_id].notes.get(tag)
    if text is None:
        write_message(update, context, f"Заметки с тегом _{tag}_ не найдено")
    else:
        write_message(update, context, text)
    users[chat_id].next_command = info


def del_tag_note(update: Update, context):
    tag = update.effective_message.text.strip()
    chat_id = update.effective_message.chat_id
    text = users[chat_id].notes.get(tag)
    if text is None:
        write_message(update, context, f"Заметки с тегом _{tag}_ не найдено")
    else:
        users[chat_id].notes.pop(tag)
        write_message(update, context, f"Удалена заметка с тегом *{tag}*\n" + text)
    users[chat_id].next_command = info


def del_all_notes(update: Update, context):
    chat_id = update.effective_message.chat_id
    context.bot.send_message(
        chat_id=chat_id,
        text="Удалить все заметки?",
        reply_markup=create_inline_markup([[["Да", "delete"], ["Нет", "not delete"]]])
    )
    users[chat_id].next_command = info


def timer(update: Update, context):
    chat_id = update.effective_message.chat_id
    write_message(update, context, f"Напиши, на сколько поставить таймер, в формате\n"
                                   f"*часы : минуты : секунды*\n"
                                   f"Со следующего абзаца можешь написать описание")
    users[chat_id].next_command = set_timer


def set_timer(update: Update, context):
    chat_id = update.effective_message.chat_id
    blocks = update.effective_message.text.split('\n', 1)
    time = blocks[0].split(':', 2)
    try:
        seconds = int(time[0]) * 3600 + int(time[1]) * 60 + int(time[2])
    except (ValueError, IndexError):
        write_message(update, context, f"Неверный формат ввода времени, не забудь ставить *двоеточие.*\n"
                                       f"Напиши, на сколько поставить таймер, в формате\n"
                                       f"*часы : минуты : секунды*\n"
                                       f"Со следующего абзаца можешь написать описание")
        users[chat_id].next_commnad = set_timer
        return
    msg = ""
    if time[0] != '0':
        msg += numeral.get_plural(int(time[0]), "час, часа, часов") + " "
    if time[1] != '0':
        msg += numeral.get_plural(int(time[1]), "минута, минуты, минут") + " "
    if time[2] != '0':
        msg += numeral.get_plural(int(time[2]), "секунда, секунды, секунд")
    if len(blocks) == 2:
        msg += ".\n_" + blocks[1] + '_'
    context.job_queue.run_once(end_of_timer, seconds, context=[chat_id, f"Прошло {msg}"])
    write_message(update, context, f"Таймер на {msg} установлен")
    users[chat_id].next_commnad = info


def end_of_timer(context):
    context.bot.send_sticker(
        chat_id=context.job.context[0],
        sticker="CAACAgIAAxkBAAECoFNg_AyLMEp5ewVuHdBYQ2gBLLd1hAACTgsAAi8P8AawBuAhEH-5zSAE"
    )
    context.bot.send_message(
        chat_id=context.job.context[0],
        text=context.job.context[1],
        parse_mode="Markdown"
    )


def new_event(update: Update, context):
    chat_id = update.effective_message.chat_id
    write_message(update, context, "Напиши название мероприятия, а в следующем абзаце можешь указать его описание.\n"
                                   "Далее мы определеимся с его частотой и временем")
    users[chat_id].next_command = create_event


def create_event(update: Update, context):
    chat_id = update.effective_message.chat_id
    blocks = update.effective_message.text.split('\n', 1)
    blocks[0] = blocks[0].strip()
    blocks.append("")
    if users[chat_id].events.get(blocks[0]) is None:
        users[chat_id].events[blocks[0]] = blocks[1]
    else:
        write_message(update, context, f"Мероприятие с таким названием уже есть\n"
                                       f"{users[chat_id].events[blocks[0]]}")
        users[chat_id].next_command = info
        return
    users[chat_id].name_event = blocks[0]
    context.bot.send_message(
        chat_id=chat_id,
        text="Теперь давай определимся со временем",
        reply_markup=create_inline_markup([[["Один раз", "once"], ["Ежедневно", "every day"]],
                                           [["Еженедельно", "every week"],
                                            ["В какие-то дни недели", "some days of week"]],
                                           [["Ежемесячно", "every month"], ["Свой период", "own period"]]])
    )
    users[chat_id].next_command = integrate_event


def period_of_event(update: Update, context):
    chat_id = update.effective_message.chat_id
    period = users[chat_id].per_event
    if period == "once":
        write_message(update, context, "Напиши время мероприятия в формате\n"
                                       "*день . месяц . год ; часы : минуты*"
                      )
    elif period == "every day":
        write_message(update, context, "Напиши время мероприятия в формате\n"
                                       "*день . месяц . год ; часы : минуты*"
                      )
    elif period == "every week":
        write_message(update, context, "Напиши время мероприятия в формате\n"
                                       "*день . месяц . год ; часы : минуты*"
                      )
    elif period == "some days of week":
        write_message(update, context, "Напиши время мероприятия в формате\n"
                                       "*часы : минуты*\n"
                                       "В следующей строке укажи номера дней недели *(через запятую)*, "
                                       "в которые будет мероприятие\n"
                                       "ПН-1, ВТ-2, СР-3, ЧТ-4, ПТ-5, СР-6, ВС-7"
                      )
    elif period == "every month":
        write_message(update, context, "Напиши время мероприятия в формате\n"
                                       "*день ; часы : минуты*"
                      )
    elif period == "own period":
        write_message(update, context, "Напиши время мероприятия в формате\n"
                                       "*день . месяц . год ; часы : минуты*\n"
                                       "В следующей строке укажи период в формате (без скобок)\n"
                                       "*s[период в секундах]*, или *m[период в минутах]*, или "
                                       "*h[период в часах]*, или *d[период в днях]*"
                      )


def convert_datetime(date, time):
    day = int(date.split('.', 2)[0])
    month = int(date.split('.', 2)[1])
    year = int(date.split('.', 2)[2])
    hour = int(time.split(':', 1)[0])
    minute = int(time.split(':', 1)[1])
    return datetime.datetime(year, month, day, hour, minute)


def convert_time(time):
    hour = int(time.split(':', 1)[0])
    minute = int(time.split(':', 1)[1])
    return datetime.time(hour, minute)


def convert_date(date):
    day = int(date.split('.', 2)[0])
    month = int(date.split('.', 2)[1])
    year = int(date.split('.', 2)[2])
    return datetime.date(year, month, day)


def integrate_event(update: Update, context):
    chat_id = update.effective_message.chat_id
    period = users[chat_id].per_event
    name = users[chat_id].name_event
    txt = users[chat_id].events[name]
    text = update.effective_message.text
    delta = users[chat_id].timezone
    remind_list = users[chat_id].remind_list
    job_list = []
    try:
        if period in ("once", "every week", "every day"):
            date = text.split(';', 1)[0]
            time = text.split(';', 1)[1]
            dt = convert_datetime(date, time)
            if period == "once":
                for remind in remind_list:
                    job_list.append(context.job_queue.run_once(end_of_event, dt - delta - remind,
                                                               context=[chat_id, users[chat_id].name_event]))
                users[chat_id].events[name] = Event(name, txt, "один раз", dt.strftime("%Y-%b-%d %H:%M"), job_list,
                                                    dt.date())
            elif period == "every week":
                interval = datetime.timedelta(weeks=1)
                for remind in remind_list:
                    job_list.append(context.job_queue.run_repeating(end_of_event, interval, dt - delta - remind,
                                                                    context=[chat_id, users[chat_id].name_event]))
                users[chat_id].events[name] = Event(name, txt, "еженедельно", dt.strftime("%Y-%b-%d %H:%M, %A"),
                                                    job_list, dt.date())
            elif period == "every day":
                interval = datetime.timedelta(days=1)
                for remind in remind_list:
                    job_list.append(context.job_queue.run_repeating(end_of_event, interval, dt - delta - remind,
                                                                    context=[chat_id, users[chat_id].name_event]))
                users[chat_id].events[name] = Event(name, txt, "ежедневно", dt.strftime("%Y-%b-%d %H:%M"),
                                                    job_list, dt.date())
        elif period == "some days of week":
            time = text.split('\n', 1)[0]
            days = list(map(int, text.split('\n', 1)[1].split(',')))
            str_of_days = "в дни недели: "
            tmp_map = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
            days = tuple([x - 1 for x in days])
            for x in days:
                str_of_days += tmp_map[x] + ' '
            dt = convert_datetime("1.1.2000", time)
            for remind in remind_list:
                job_list.append(context.job_queue.run_daily(end_of_event, (dt - delta - remind).time(), days,
                                                            context=[chat_id, users[chat_id].name_event]))
            users[chat_id].events[name] = Event(name, txt, str_of_days, dt.time().strftime("%H:%M"), job_list, days)
        elif period == "every month":
            day = int(text.split(';', 1)[0])
            time = text.split(';', 1)[1]
            dt = convert_datetime("1.1.2000", time)
            for remind in remind_list:
                job_list.append(context.job_queue.run_monthly(end_of_event, (dt - delta - remind).time(), day,
                                                              context=[chat_id, users[chat_id].name_event]))
            users[chat_id].events[name] = Event(name, txt, f"{day} числа каждого месяца", dt.time().strftime("%H:%M"),
                                                job_list, datetime.date(year=0, month=0, day=day))
        elif period == "own period":
            lines = text.split('\n', 1)
            date = lines[0].split(';', 1)[0]
            time = lines[0].split(';', 1)[1]
            dt = convert_datetime(date, time)
            mode = lines[1][0]
            period = int(lines[1][1:])
            interval = None
            str_period = "каждые "
            if mode == 's':
                interval = datetime.timedelta(seconds=period)
                str_period += numeral.get_plural(period, "секунда, секунды, секунд")
            elif mode == 'm':
                interval = datetime.timedelta(minutes=period)
                str_period += numeral.get_plural(period, "минута, минуты, минут")
            elif mode == 'h':
                interval = datetime.timedelta(hours=period)
                str_period += numeral.get_plural(period, "час, часа, часов")
            elif mode == 'd':
                interval = datetime.timedelta(days=period)
                str_period += numeral.get_plural(period, "день, дня, дней")
            for remind in remind_list:
                job_list.append(context.job_queue.run_repeating(end_of_event, interval, first=dt - delta - remind,
                                                                context=[chat_id, users[chat_id].name_event]))
            users[chat_id].events[name] = Event(name, txt, str_period, dt.strftime("%Y-%b-%d %H:%M"), job_list, dt)
        write_message(update, context, "Мероприятие успешно добавлено\n" + users[chat_id].events[name].to_string())
        users[chat_id].next_command = info
    except (ValueError, IndexError):
        write_message(update, context, "Неверный формат ввода времени или даты. Обрати внимание на формат ввода")
        period_of_event(update, context)


def end_of_event(context):
    chat_id = context.job.context[0]
    name = context.job.context[1]
    context.bot.send_sticker(
        chat_id=chat_id,
        sticker="CAACAgIAAxkBAAECoKdg_Eemvpq6SkT6PQuenshQq1IWLAACSgADrWW8FIl7DV4Ij3qSIAQ"
    )
    context.bot.send_message(
        chat_id=chat_id,
        text=f"Напоминание о мероприятии\n"
             f"{users[chat_id].events[name].to_string()}",
        parse_mode="Markdown"
    )


def name_event(update: Update, context):
    write_message(update, context, "Напиши *Название* мероприятия")
    chat_id = update.effective_message.chat_id
    if update.effective_message.text == "/getevent":
        users[chat_id].next_command = get_name_event
    elif update.effective_message.text == "/delevent":
        users[chat_id].next_command = del_name_event


def get_name_event(update: Update, context):
    name = update.effective_message.text.strip()
    chat_id = update.effective_message.chat_id
    text = users[chat_id].events.get(name)
    if text is None:
        write_message(update, context, f"Мероприятия с названием _{name}_ не найдено")
    else:
        write_message(update, context, text.to_string())
    users[chat_id].next_command = info


def del_name_event(update: Update, context):
    name = update.effective_message.text.strip()
    chat_id = update.effective_message.chat_id
    text = users[chat_id].events.get(name)
    if text is None:
        write_message(update, context, f"Мероприятия с названием _{name}_ не найдено")
    else:
        for job in users[chat_id].events.get(name).job_list:
            job.schedule_removal()
        users[chat_id].events.pop(name)
        write_message(update, context, f"Удалено мероприятие\n" + text.to_string())
    users[chat_id].next_command = info


def events(update: Update, context):
    chat_id = update.effective_message.chat_id
    write_message(update, context, users[chat_id].get_all_events())


def today_events(update: Update, context):
    chat_id = update.effective_message.chat_id
    td = datetime.date.today()
    write_message(update, context, users[chat_id].get_events_in_range(td, td))


def tomorrow_events(update: Update, context):
    chat_id = update.effective_message.chat_id
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    write_message(update, context, users[chat_id].get_events_in_range(tomorrow, tomorrow))


def near_events(update: Update, context):
    chat_id = update.effective_message.chat_id
    write_message(update, context, "На сколько дней хочешь узнать мероприятия?")
    users[chat_id].next_command = near_days_events


def near_days_events(update: Update, context):
    chat_id = update.effective_message.chat_id
    try:
        days = int(update.effective_message.text)
        td = datetime.date.today()
        end = td + datetime.timedelta(days=days)
        write_message(update, context, users[chat_id].get_events_in_range(td, end))
    except ValueError:
        write_message(update, context, f"Неверный формат ввода количества дней, давай ещё раз.\n"
                                       f"На сколько дней хочешь узнать мероприятия?")
        users[chat_id].next_command = near_days_events
    users[chat_id].next_command = info


def range_events(update: Update, context):
    chat_id = update.effective_message.chat_id
    write_message(update, context, f"Введи начало и конец диапазона, в котором хочешь узнать мероприятия, "
                                   f"в *двух абзацах* в формате\n"
                                   f"*день . месяц . год*\n")
    users[chat_id].next_command = get_range_events


def get_range_events(update: Update, context):
    chat_id = update.effective_message.chat_id
    try:
        lines = update.effective_message.text.split('\n', 1)
        st = convert_date(lines[0])
        end = convert_date(lines[1])
        write_message(update, context, users[chat_id].get_events_in_range(st, end))
    except (ValueError, IndexError):
        write_message(update, context, f"Неверный формат ввода количества дней, давай ещё раз.\n"
                                       f"Введи начало и конец диапазона, в котором хочешь узнать мероприятия, "
                                       f"в *двух абзацах* в формате\n"
                                       f"*день . месяц . год\n")
        users[chat_id].next_command = get_range_events
    users[chat_id].next_command = info


def message(update: Update, context):
    chat_id = update.effective_message.chat_id
    users[chat_id].next_command(update, context)


def main():
    my_update = Updater(
        token=config.TOKEN
    )

    keyboard_handler = CallbackQueryHandler(callback=keyboard_regulate, pass_chat_data=True)
    my_handler = MessageHandler(Filters.all, message)

    command_list = [['start', start], ['help', info], ['newnote', new_note],
                    ['notes', notes], ['getnote', tag_note], ['delnote', tag_note],
                    ['delallnotes', del_all_notes], ['timer', timer], ['newevent', new_event],
                    ['getevent', name_event], ['delevent', name_event], ['events', events],
                    ['todayevents', today_events], ['tomorrowevents', tomorrow_events], ['nearevents', near_events],
                    ['rangeevents', range_events]]
    for command in command_list:
        my_update.dispatcher.add_handler(CommandHandler(command[0], command[1]))
    message_list = [['Справка', info], ['Новая заметка', new_note], ['Все заметки', notes],
                    ['Таймер', timer], ['Новое событие', new_event], ['Все события', events],
                    ['События на сегодня', today_events], ['События на завтра', tomorrow_events],
                    ['Ближайшие события', near_events]]
    for msg in message_list:
        my_update.dispatcher.add_handler(MessageHandler(Filters.text(msg[0]), msg[1]))

    my_update.dispatcher.add_handler(keyboard_handler)
    my_update.dispatcher.add_handler(my_handler)

    my_update.start_polling()
    my_update.idle()


if __name__ == "__main__":
    print("Bot starts work")
    main()
