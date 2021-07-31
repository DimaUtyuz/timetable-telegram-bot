class Event:
    def __init__(self, name, text, period, start, job_list, date):
        self.name = name
        self.text = text
        self.period = period
        self.start = start
        self.date = date
        self.job_list = job_list

    def to_string(self):
        return (f"Название: *{self.name}*\n"
                f"Период: {self.period}\n"
                f"Начало: {self.start}\n"
                f"_{self.text}_")
