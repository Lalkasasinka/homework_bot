# Бот для  проверки домашних заданий

## Описание проекта
---
Homework Bot - телеграм-бот для проверки статуса домашней работы через API-сервис Практикум.Домашка.

---
## Функционал бота
---
+ Раз в 10 минут опрашивает API сервис Практикум.Домашка и проверет статус отправленной на ревью домашней работы;
+ При обновлении статуса анализирует ответ API и отправляет соответствующее уведомление в Telegram;
+ Логирует свою работу и сообщает о важных проблемах сообщением в Telegram.

Запуск бота
---
Для MacOs и Linux вместо python использовать python3

1. Клонировать репозиторий:
```
git clone https://github.com/Lalkasasinka/homework_bot.git
```

2. Cоздать и активировать виртуальное окружение:
```
cd homework_bot
python -m venv venv
```
Для Windows:
```
source venv/Scripts/activate

```
Для MacOs/Linux:
```
source venv/bin/activate
```

3. Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Импортировать токены для API-сервиса Практикум.Домашка и Telegram
```
export PRACTICUM_TOKEN=<PRACTICUM_TOKEN>
export TELEGRAM_TOKEN=<TELEGRAM_TOKEN>
export CHAT_ID=<CHAT_ID>
```

5. Запустить бота:
```
python homework.py
```

##Контакты
---
Синицын Иван
[telegram](https://t.me/sSinichka)
