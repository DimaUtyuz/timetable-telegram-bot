import datetime


class User:
    def __init__(self, chat_id, name):
        self.name = name
        self.chat_id = chat_id
        self.next_command = lambda a, b: print("WARNING: next command is not defined")
        self.notes = {}
        self.events = {}
        self.timezone = None
        self.name_event = None
        self.per_event = None
        self.remind_list = []

    def get_events_in_range(self, date_start, date_finish):
        i = date_start
        result = f"Мероприятия от *{date_start.strftime('%Y-%b-%d, %A')}* до " \
                 f"*{date_finish.strftime('%Y-%b-%d, %A')}* без событий с собственным периодом\n\n"
        while i <= date_finish:
            result += f"*{i.strftime('%Y-%b-%d, %A')}*\n"
            add = False
            for event in self.events.values():
                d = event.date
                per = event.period
                if ((per == "один раз") and (d == i)) or \
                        ((per == "еженедельно") and (i >= d) and (i.weekday() == d.weekday())) or \
                        ((per == "ежедневно") and (i >= d)) or \
                        ((per.find("в дни недели") != -1) and (i.weekday() in d)) or \
                        ((per.find("месяца") != -1) and (i.day() == d.day())):
                    result += f"{event.to_string()}\n\n"
                    add = True
            if not add:
                result += "_Ничего не запланировано_\n"
            i = i + datetime.timedelta(days=1)
        return result

    def get_all_events(self):
        result = "Все мероприятия\n\n"
        for event in self.events.values():
            result += event.to_string() + "\n\n"
        if len(self.events) == 0:
            result += "_Ничего не запланировано_"
        return result
