# Проект "Создание телеграм бота-планировщика"

### Содержание

#### [Описание](#описание)

#### [Заметки](#заметки)

#### [Таймер](#таймер)

#### [Мероприятия](#мероприятия)

#### [Все команды](#все-доступные-команды)

## Описание

[Timetable bot](https://t.me/your_timetable_bot "Telegram bot") - помощник в планировании расписания. 
У него можно оставить заметки, поставить таймер или установить мероприятие, напоминание о котором придёт в нужное время.
Для упрощения в использовании добавлена клавиатура внизу экрана с самыми частами командами.
Каждое утро бот присылает сообщение с мероприятиями на 2 ближайших дня.

![Команды](/screenshots/1.png?raw=true)
![Установка таймера](/screenshots/2.png?raw=true)
![Создание заметки](/screenshots/3.png?raw=true)
![Создание события](/screenshots/6.png?raw=true)
![Выбор частоты события](/screenshots/4.png?raw=true)
![Выбор времени напоминания](/screenshots/5.png?raw=true)

## Заметки

Для создания заметки нужно указать **тег** (тема заметки), можно добавить **описание**. 
Также можно посмотреть или удалить заметку по её **тегу** или все заметки.

### Команды для работы с заметками

`/newnote` - оставить заметку с тегом, по которому её можно будет найти

`/newevent` - создать новое мероприятие, о котором придёт напоминание в нужное время

`/notes` - получить все заметки

`/getnote` - получить заметку по тегу

`/delnote` - удалить заметку по тегу

`/delallnotes` - удалить все заметки

## Таймер

Для установки нужно указать время, на которое ставится таймер. 
Также дополнительно можно написать сообщение, которое отобразится вместе с уведомлением по истечению времени.

### Команды для работы с таймером

`/timer` - поставить таймер

## Мероприятия

Можно посмотреть мероприятия на сегодня, на завтра, на всё время, на указанный промежуток времени. По названию можно посмотреть или удалить мероприятие.
Для создания мероприятия нужно:

1.  Указать **название**, можно добавить **описание**.
2.  Выбрать частоту события:
	*   Один раз
	*   Ежедневно
	*   Еженедельно
	*   В определённые дни недели
	*   Ежемесячно
	*   Свой период (можно указать период между событиями в секундах, минутах, часах или днях)
3.  Выбрать время напоминания (можно несколько):
	*   В момент начала
	*   За 15 минутах
	*   За 30 минут
	*   За 1 час
	*   За 2 часа
	*   За 4 часа
	*   За 1 день
	*   За 2 дня
	*   За 1 неделю

### Команды для работы с мероприятиями

`/getevent` - узнать мероприятие по названию

`/delevent` - удалить мероприятие по названию

`/events` - узнать все предстоящие мероприятия

`/todayevents` - узнать мероприятия на сегодня

`/tomorrowevents` - узнать мероприятия на завтра

`/nearevents` - узнать мероприятия на несколько ближайших дней

`/rangeevents` - узнать мероприятия в определённом диапазоне

## Все доступные команды

`/info` - посмотреть все команды

`/timer` - поставить таймер

`/newnote` - оставить заметку с тегом, по которому её можно будет найти

`/newevent` - создать новое мероприятие, о котором придёт напоминание в нужное время

`/notes` - получить все заметки

`/getnote` - получить заметку по тегу

`/delnote` - удалить заметку по тегу

`/delallnotes` - удалить все заметки

`/getevent` - узнать мероприятие по названию

`/delevent` - удалить мероприятие по названию

`/events` - узнать все предстоящие мероприятия

`/todayevents` - узнать мероприятия на сегодня

`/tomorrowevents` - узнать мероприятия на завтра

`/nearevents` - узнать мероприятия на несколько ближайших дней

`/rangeevents` - узнать мероприятия в определённом диапазоне
