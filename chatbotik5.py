import telebot
from telebot import types
import random
import re
import matplotlib.pyplot as plt
from io import BytesIO
import time
import requests
import json

# Инициализация бота
bot = telebot.TeleBot("7912214308:AAGd1JeeEqBNoXsn7VpQ6NUh1yAQn9m74EE")

# Конфигурация DeepSeek API
DEEPSEEK_API_KEY = "sk-26164f96ebb94b4186689d9d355ba324"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Заголовки для запросов
headers = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type": "application/json"
}

# База данных для хранения данных пользователей
user_data = {}

def clean_markdown(text):
    # Удаление заголовков (### Заголовок → Заголовок)
    text = re.sub(r'#+\s*(.*)', r'\1', text)
    # Удаление жирного и курсивного текста (**жирный** → жирный, *курсив* → курсив)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    # Удаление ссылок ([текст](URL) → текст)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    # Удаление изображений (![alt](URL) → alt (если нужно))
    text = re.sub(r'!\[(.*?)\]\(.*?\)', r'\1', text)
    # Удаление кодовых блоков (```код``` → код)
    text = re.sub(r'```.*?\n(.*?)\n```', r'\1', text, flags=re.DOTALL)
    # Удаление инлайн-кода (`код` → код)
    text = re.sub(r'`(.*?)`', r'\1', text)
    # Удаление HTML-тегов (если есть)
    text = re.sub(r'<.*?>', '', text)
    # Удаление горизонтальных линий (---, ***)
    text = re.sub(r'^[-*]{3,}$', '', text, flags=re.MULTILINE)
    # Удаление маркированных списков (- пункт → пункт)
    text = re.sub(r'^[-*+]\s+(.*)', r'\1', text, flags=re.MULTILINE)
    # Удаление нумерованных списков (1. пункт → пункт)
    text = re.sub(r'^\d+\.\s+(.*)', r'\1', text, flags=re.MULTILINE)
    # Удаление блочных цитат (> цитата → цитата)
    text = re.sub(r'^>\s*(.*)', r'\1', text, flags=re.MULTILINE)
    # Удаление таблиц (Markdown таблицы)
    text = re.sub(r'^\|.*\|$', '', text, flags=re.MULTILINE)
    # Удаление лишних пробелов и пустых строк
    text = re.sub(r'\n\s*\n', '\n', text)
    text = text.strip()
    
    return text

def send_resources(message, resource_type=None):
    chat_id = message.chat.id
    
    # Создаем интерактивную клавиатуру
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Кнопки для разных типов ресурсов
    buttons = [
        types.InlineKeyboardButton("🎬 Фильмы", callback_data="resources_films"),
        types.InlineKeyboardButton("📚 Книги", callback_data="resources_books"),
        types.InlineKeyboardButton("🧘 Техники", callback_data="resources_techniques"),
        types.InlineKeyboardButton("🆘 Экстренная помощь", callback_data="resources_emergency"),
        types.InlineKeyboardButton("🎧 Подкасты", callback_data="resources_podcasts")
    ]
    markup.add(*buttons)

    # Если тип ресурса уже указан (при повторных вызовах)
    if resource_type:
        return send_specific_resource(message, resource_type)

    # Основное сообщение с ресурсами
    resources_text = (
        "📚 **Полезные ресурсы** 📚\n\n"
        "Выбери категорию:\n\n"
        "• **Фильмы** - подборки для психологического развития\n"
        "• **Книги** - литература по самопомощи\n"
        "• **Техники** - упражнения для снятия тревоги\n"
        "• **Экстренная помощь** - контакты специалистов\n"
        "• **Подкасты** - аудиоресурсы по психологии"
    )

    bot.send_message(
        chat_id,
        resources_text,
        reply_markup=markup,
        parse_mode='markdown'
    )


def send_specific_resource(message, resource_type):
    """Отправка конкретного типа ресурсов"""
    chat_id = message.chat.id
    
    if resource_type == "films":
        response = (
            "🎬 **Топ фильмов для психологического развития**:\n\n"
            "1. __Общество мёртвых поэтов__ (1989) - о свободе самовыражения\n"
            "2. __Хорошо быть тихоней__ (2012) - про подростковую депрессию\n"
            "3. __Головоломка__ (2015) - как работают эмоции\n"
            "4. __Чудо__ (2017) - о принятии себя\n\n"
            "📌 После просмотра можешь поделиться впечатлениями!"
        )
        
    elif resource_type == "books":
        response = (
            "📚 **Книги по самопомощи**:\n\n"
            "• __Ты сильнее, чем думаешь__ - Кевин Люк\n"
            "• __К себе нежно__ - Ольга Примаченко\n"
            "• __Тонкое искусство пофигизма__ - Марк Мэнсон\n\n"
            "💡 Могу прислать краткое содержание любой из них"
        )
        
    elif resource_type == "techniques":
        response = (
            "🧘 **Техники самопомощи**:\n\n"
            "1. **Дыхание 4-7-8** - вдох 4 сек, задержка 7, выдох 8\n"
            "2. **Метод 5-4-3-2-1** - заземление через органы чувств\n"
            "3. **Дневник благодарности** - 3 хорошие вещи каждый день\n\n"
            "Выбери технику для подробного описания:"
        )
        
    elif resource_type == "emergency":
        response = (
            "🆘 **Экстренная психологическая помощь**:\n\n"
            "• Телефон доверия: **8-800-2000-122**\n"
            "• Кризисный чат: **https://помощьрядом.рф**\n"
            "• МЧС России: **112** (скажи 'нужен психолог')\n\n"
            "Ты не один! Обратись за помощью."
        )
    elif resource_type == "podcasts":
        response = (
            "🎧 **Психологические подкасты**:\n\n"
            "1. __Психология на квадратах__ - анализ психологии через криминалистику\n"
            "2. __Подкаст 'Ты не один'__ - о психическом здоровье подростков\n"
            "3. __Brain Science__ - нейропсихология (на английском)\n\n"
            "Выбери подкаст для получения ссылок:"
        )

    # Кнопка "Назад к ресурсам"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("← Назад к ресурсам", callback_data="resources_back"))

    bot.send_message(
        chat_id,
        response,
        reply_markup=markup,
        parse_mode='markdown'
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('resources_'))
def handle_resources_callback(call):
    """Обработчик нажатий кнопок ресурсов"""
    resource_type = call.data.split('_')[1]
    
    if resource_type == "back":
        send_resources(call.message)
    else:
        send_specific_resource(call.message, resource_type)
    
    bot.answer_callback_query(call.id)

def send_welcome(message):
    chat_id = message.chat.id
    
    # Инициализация данных пользователя
    user_data[chat_id] = {
        "chat_history": [],
        "current_method": None,
        "self_char_answers": {},
        "mood_history": [],
    }
    
    # Создаем интерактивную клавиатуру
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    buttons = [
        types.KeyboardButton("📝 Записать настроение"),
        types.KeyboardButton("🧘 Техники релаксации"),
        types.KeyboardButton("🆘 Экстренная помощь"),
        types.KeyboardButton("🎬 Рекомендации фильмов"),
        types.KeyboardButton("📚 Полезные книги"),
        types.KeyboardButton("🎧 Психологические подкасты"),
        types.KeyboardButton("🙏 Упражнения на благодарность"),
        types.KeyboardButton("✨ Аффирмации"),
        types.KeyboardButton("🧠 Тренировка EQ"),
        types.KeyboardButton("🎨 Арт-терапия")
    ]
    
    markup.add(*buttons)
    
    # Приветственное сообщение с форматированием
    welcome_text = (
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        "Я - твой виртуальный психолог-помощник. Вот что я могу предложить:\n\n"
        "• **Запись настроения** - отслеживай свое эмоциональное состояние\n"
        "• **Техники релаксации** - упражнения для снижения тревоги\n"
        "• **Экстренная помощь** - контакты для критических ситуаций\n"
        "• **Психологические ресурсы** - книги, фильмы, подкасты\n"
        "• **Практики саморазвития** - аффирмации, арт-терапия, EQ-тренинг\n\n"
        "Просто выбери нужный вариант ниже или напиши мне о том, что тебя беспокоит."
    )
    
    # Отправка стикера приветствия (можно заменить на свой)
    try:
        bot.send_sticker(chat_id, "CAACAgIAAxkBAAEL...")  # ID стикера
    except:
        pass  # Если стикер не отправится - пропускаем
    
    # Отправка основного сообщения
    bot.send_message(
        chat_id,
        welcome_text,
        reply_markup=markup,
        parse_mode='markdown'
    )
    
    # Отправка быстрых кнопок (необязательно)
    quick_markup = types.InlineKeyboardMarkup()
    quick_markup.add(
        types.InlineKeyboardButton("😊 Хорошо", callback_data="mood_good"),
        types.InlineKeyboardButton("😐 Нормально", callback_data="mood_normal"),
        types.InlineKeyboardButton("😔 Плохо", callback_data="mood_bad")
    )
    
    bot.send_message(
        chat_id,
        "Как ты себя чувствуешь прямо сейчас?",
        reply_markup=quick_markup,
        parse_mode='markdown'
    )

def query_deepseek(prompt, chat_history=None):
    """Запрос к DeepSeek API"""
    messages = [
        {
            "role": "system",
            "content": """Ты - эмпатичный психолог-помощник для подростков. 
            Будь поддерживающим, не осуждай, предлагай практические техники. 
            Важно: при суицидальных мыслях дай контакты экстренной помощи. При ответе используй только markdown разметку."""
        }
    ]
    
    if chat_history:
        messages.extend(chat_history)
    
    messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, data=json.dumps(data))
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"DeepSeek API error: {e}")
        return None

# Расширенная база данных ресурсов
# ... (предыдущий код остается без изменений до RESOURCES_DB)

# Расширенная база данных ресурсов
RESOURCES_DB = {
    "books": [
        {
            "id": 1,
            "title": "Ты сильнее, чем думаешь",
            "author": "Кевин Люк",
            "description": "Практическое руководство по преодолению тревоги и развитию уверенности в себе",
            "tags": ["тревожность", "уверенность", "самооценка"]
        },
        {
            "id": 2,
            "title": "К себе нежно",
            "author": "Ольга Примаченко",
            "description": "Рабочая тетрадь по самопринятию и заботе о себе",
            "tags": ["самопринятие", "депрессия", "самопомощь"]
        }
    ],
    "films": [
        {
            "id": 1,
            "title": "Общество мёртвых поэтов",
            "year": 1989,
            "description": "Фильм о важности самовыражения и поиска своего пути",
            "tags": ["самореализация", "вдохновение"]
        },
        {
            "id": 2,
            "title": "Чудо",
            "year": 2017,
            "description": "История мальчика с лицевой аномалией, который учится принимать себя",
            "tags": ["буллинг", "принятие себя"]
        }
    ],
    "techniques": [
        {
            "id": 1,
            "name": "Дыхание 4-7-8",
            "description": "Техника для быстрого снижения тревоги",
            "steps": "1. Вдохните через нос 4 секунды\n2. Задержите дыхание на 7 секунд\n3. Медленно выдохните через рот 8 секунд",
            "tags": ["тревога", "стресс"]
        },
        {
            "id": 2,
            "name": "Метод 5-4-3-2-1",
            "description": "Техника заземления при панических атаках",
            "steps": "Назовите:\n5 вещей, которые видите\n4 которые ощущаете\n3 слышите\n2 нюхаете\n1 пробуете",
            "tags": ["паника", "заземление"]
        }
    ],
    "podcasts": [
        {
            "id": 1,
            "title": "Психология на квадратах",
            "description": "Анализ психологии через призму криминалистики и социологии",
            "links": {
                "Яндекс Музыка": "https://example.com/1",
                "Spotify": "https://example.com/2"
            }
        },
        {
            "id": 2,
            "title": "Подкаст 'Ты не один'",
            "description": "О психическом здоровье подростков",
            "links": {
                "Apple Podcasts": "https://example.com/3",
                "Google Podcasts": "https://example.com/4"
            }
        },
        {
            "id": 4,
            "title": "Хорошо, что вы это сказали",
            "description": "Искренние разговоры о 'неудобных' темах",
            "links": {
                "Яндекс Музыка": "https://music.yandex.ru/album/11558002",
                "SoundCloud": "https://soundcloud.com/goodyousaidit"
            }
        },
        {
            "id": 5,
            "title": "Стыдно",
            "description": "Как перестать зависеть от мнения других",
            "links": {
                "Яндекс Музыка": "https://music.yandex.ru/album/8865119",
                "Castbox": "https://castbox.fm/channel/%D0%A1%D1%82%D1%8B%D0%B4%D0%BD%D0%BE-id2130444"
            }
        },
        {
            "id": 6,
            "title": "Это пройдет",
            "description": "Поддержка в кризисных ситуациях",
            "links": {
                "Яндекс Музыка": "https://music.yandex.ru/album/10177502",
                "Apple Podcasts": "https://podcasts.apple.com/ru/podcast/%D1%8D%D1%82%D0%BE-%D0%BF%D1%80%D0%BE%D0%B9%D0%B4%D0%B5%D1%82/id1475228816"
            }
        },
        {
            "id": 7,
            "title": "Чай с психологом",
            "description": "Разбор житейских ситуаций с психологом",
            "links": {
                "Яндекс Музыка": "https://music.yandex.ru/album/9534864",
                "Spotify": "https://open.spotify.com/show/0vRrL5f6hKwhuZl5e0q4fP"
            }
        },
        {
            "id": 8,
            "title": "Хьюстон, у нас проблемы",
            "description": "Подкаст о сложных жизненных ситуациях",
            "links": {
                "Яндекс Музыка": "https://music.yandex.ru/album/8848539"
            }
        },
        {
            "id": 9,
            "title": "Мы не договорили",
            "description": "Откровенные разговоры о недоговоренностях в отношениях",
            "links": {
                "Яндекс Музыка": "https://music.yandex.ru/album/10704202"
            }
        }
    ],
    
    "gratitude_exercises": [
        {
            "id": 3,
            "title": "Дневник благодарности",
            "steps": [
                "1. Каждый вечер записывайте 3 вещи, за которые благодарны",
                "2. Описывайте не только события, но и чувства",
                "3. Перечитывайте записи раз в неделю"
            ]
        }
    ],
        
    "affirmations": {
        "confidence": [
            "Я достоин любви и уважения",
            "Мои ошибки не определяют мою ценность"
        ],
        "anxiety": [
            "Я в безопасности здесь и сейчас",
            "Мои тревоги - просто мысли, не факты"
        ]
    },
    "emotional_intelligence": [
        {
            "id": 1,
            "title": "Игра 'Угадай эмоцию'",
            "description": "Смотрите на лица людей в фильмах без звука и угадывайте эмоции"
        }
    ],
    "art_therapy": [
        {
            "id": 1,
            "title": "Рисование эмоций",
            "description": "Изобразите свое состояние абстрактными формами и цветами"
        }
    ]
}



def recommend_resources(user_state):
    """Интеллектуальная рекомендация ресурсов на основе состояния пользователя"""
    recommended = {"books": [], "films": [], "techniques": [], "podcasts": []}
    
    if "тревож" in user_state.lower():
        recommended["books"] = [b for b in RESOURCES_DB["books"] if "тревожность" in b["tags"]]
        recommended["techniques"] = [t for t in RESOURCES_DB["techniques"] if "тревога" in t["tags"]]
        recommended["podcasts"] = RESOURCES_DB["podcasts"][:1]  # Первый подкаст
    
    if "буллинг" in user_state.lower():
        recommended["films"] = [f for f in RESOURCES_DB["films"] if "буллинг" in f["tags"]]
        recommended["books"] = [b for b in RESOURCES_DB["books"] if "самооценка" in b["tags"]]
    
    # Если нет специфических рекомендаций - предлагаем популярное
    if not any(recommended.values()):
        recommended["books"] = RESOURCES_DB["books"][:2]
        recommended["films"] = RESOURCES_DB["films"][:2]
        recommended["techniques"] = RESOURCES_DB["techniques"][:2]
        recommended["podcasts"] = RESOURCES_DB["podcasts"][:1]
    
    return recommended

def send_resource_details(chat_id, resource_type, resource_id):
    """Отправка детальной информации о ресурсе"""
    resource = next((r for r in RESOURCES_DB[resource_type] if r["id"] == resource_id), None)
    if not resource:
        return False

    if resource_type == "books":
        text = (
            f"📖 **{resource['title']}**\n"
            f"Автор: {resource['author']}\n\n"
            f"{resource['description']}\n\n"
            "Хочешь обсудить эту книгу?"
        )
    elif resource_type == "films":
        text = (
            f"🎬 **{resource['title']}** ({resource['year']})\n\n"
            f"{resource['description']}\n\n"
            "После просмотра можешь поделиться впечатлениями!"
        )
    elif resource_type == "techniques":
        text = (
            f"🧠 **{resource['name']}**\n\n"
            f"{resource['description']}\n\n"
            f"**Как выполнять:**\n{resource['steps']}\n\n"
            "Попробуй прямо сейчас!"
        )
    elif resource_type == "podcasts":
        links_text = "\n".join([f"{platform}: {url}" for platform, url in resource["links"].items()])
        text = (
            f"🎧 **{resource['title']}**\n\n"
            f"{resource['description']}\n\n"
            f"**Ссылки для прослушивания:**\n{links_text}"
        )

    markup = types.InlineKeyboardMarkup()
    if resource_type != "techniques" and resource_type != "podcasts":
        markup.add(types.InlineKeyboardButton(
            "Обсудить", 
            callback_data=f"discuss_{resource_type}_{resource_id}"
        ))
    markup.add(types.InlineKeyboardButton(
        "← Назад", 
        callback_data=f"back_to_{resource_type}"
    ))

    bot.send_message(
        chat_id,
        text,
        reply_markup=markup,
        parse_mode='markdown'
    )
    return True

def send_resource_list(chat_id, resource_type):
    """Отправка списка ресурсов определенного типа"""
    resources = RESOURCES_DB.get(resource_type, [])
    if not resources:
        bot.send_message(chat_id, "Ресурсы временно недоступны")
        return

    markup = types.InlineKeyboardMarkup()
    for r in resources[:5]:  # Ограничиваем 5 элементами
        btn_text = ""
        if resource_type == "books":
            btn_text = f"{r['title']} - {r['author']}"
        elif resource_type == "films":
            btn_text = f"{r['title']} ({r['year']})"
        elif resource_type == "techniques":
            btn_text = f"{r['name']}"
        elif resource_type == "podcasts":
            btn_text = f"{r['title']}"
            
        markup.add(types.InlineKeyboardButton(
            btn_text,
            callback_data=f"show_{resource_type}_{r['id']}"
        ))

    type_names = {
        "books": "📚 Книги по психологии",
        "films": "🎬 Фильмы для развития",
        "techniques": "🧘 Психологические техники",
        "podcasts": "🎧 Психологические подкасты"
    }

    bot.send_message(
        chat_id,
        f"{type_names[resource_type]}:\nВыбери для подробного описания:",
        reply_markup=markup,
        parse_mode='markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('show_'))
def handle_show_resource(call):
    """Обработка запроса на просмотр ресурса"""
    _, resource_type, resource_id = call.data.split('_')
    send_resource_details(call.message.chat.id, resource_type, int(resource_id))
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('back_to_'))
def handle_back_to_list(call):
    """Возврат к списку ресурсов"""
    resource_type = call.data.split('_')[2]
    send_resource_list(call.message.chat.id, resource_type)
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.text in ["📚 Книги", "🎬 Фильмы", "🧘 Техники", "🎧 Психологические подкасты"])
def handle_resource_request(message):
    """Обработка запросов на получение ресурсов"""
    resource_types = {
        "📚 Книги": "books",
        "🎬 Фильмы": "films",
        "🧘 Техники": "techniques",
        "🎧 Психологические подкасты": "podcasts"
    }
    send_resource_list(message.chat.id, resource_types[message.text])

# Новые команды для дополнительных функций
@bot.message_handler(func=lambda m: m.text == "🙏 Упражнения на благодарность")
def send_gratitude_exercises(message):
    exercise = random.choice(RESOURCES_DB["gratitude_exercises"])
    
    bot.send_message(
        message.chat.id,
        f"🙏 {exercise['title']}:\n\n" + "\n".join(exercise["steps"])
    )

@bot.message_handler(func=lambda m: m.text == "✨ Аффирмации")
def send_affirmation(message):
    category = "confidence" if random.random() > 0.5 else "anxiety"
    affirmation = random.choice(RESOURCES_DB["affirmations"][category])
    
    bot.send_message(
        message.chat.id,
        f"✨ Аффирмация дня:\n\n{affirmation}\n\n"
        "Повторите 5 раз вслух и запишите в заметки"
    )

@bot.message_handler(func=lambda m: m.text == "🧠 Тренировка EQ")
def send_eq_exercise(message):
    exercise = random.choice(RESOURCES_DB["emotional_intelligence"])
    
    bot.send_message(
        message.chat.id,
        f"🧠 Упражнение '{exercise['title']}':\n\n{exercise['description']}"
    )

@bot.message_handler(func=lambda m: m.text == "🎨 Арт-терапия")
def send_art_task(message):
    task = random.choice(RESOURCES_DB["art_therapy"])
    
    bot.send_message(
        message.chat.id,
        f"🎨 Арт-терапевтическое задание:\n\n{task['title']}\n\n{task['description']}\n\n"
        "Пришлите фото результата, если хотите получить обратную связь"
    )

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        send_welcome(message)
        return
    
    current_method = user_data[chat_id].get("current_method")
    
    # Если активен тест самохарактеристики
    if current_method == "self_characteristics":
        questions = list(self_characteristics.keys())
        answered = user_data[chat_id]["self_char_answers"].keys()
        
        for q in questions:
            if q not in answered:
                user_data[chat_id]["self_char_answers"][q] = message.text
                send_next_self_test_question(chat_id)
                return
    
    # Экстренные случаи
    if any(word in message.text.lower() for word in ["умру", "покончу", "суицид", "убить себя"]):
        send_emergency_help(message)
        return
    
    # Подготовка истории диалога для контекста
    chat_history = user_data[chat_id].get("chat_history", [])
    
    # Запрос к DeepSeek API
    bot.send_chat_action(chat_id, 'typing')  # Показываем "печатает"
    
    # Добавляем системный контекст при необходимости
    context = ""
    if current_method == "problem_situation":
        context = "Пользователь описывает проблемную ситуацию. Помоги разобраться, задавая уточняющие вопросы."
    
    response = query_deepseek(f"{context}\n{message.text}", chat_history)
    
    if not response:
        response = "Извини, я временно не могу ответить. Попробуй позже."

    response = clean_markdown(response)
    
    # Сохраняем диалог в историю (последние 5 сообщений)
    chat_history.append({"role": "user", "content": message.text})
    chat_history.append({"role": "assistant", "content": response})
    user_data[chat_id]["chat_history"] = chat_history[-5:]  # Ограничиваем историю
    
    # Отправляем ответ
    bot.send_message(chat_id, response, parse_mode='markdown')
    
    # Если в ответе есть рекомендация техник - покажем пример
    if "дыхание" in response.lower():
        bot.send_message(chat_id, "Попробуй технику 4-7-8:\n1. Вдох 4 сек\n2. Задержка 7 сек\n3. Выдох 8 сек")
    
    # Если обнаружена депрессия - предложим ресурсы
    if any(word in response.lower() for word in ["депрессия", "тревожность", "буллинг", "стресс"]):
        recommended = recommend_resources(response.lower())
        if recommended["books"] or recommended["films"] or recommended["techniques"] or recommended["podcasts"]:
            markup = types.InlineKeyboardMarkup(row_width=2)
            buttons = []
            
            if recommended["books"]:
                buttons.append(types.InlineKeyboardButton("📚 Книги", callback_data="back_to_books"))
            if recommended["films"]:
                buttons.append(types.InlineKeyboardButton("🎬 Фильмы", callback_data="back_to_films"))
            if recommended["techniques"]:
                buttons.append(types.InlineKeyboardButton("🧘 Техники", callback_data="back_to_techniques"))
            if recommended["podcasts"]:
                buttons.append(types.InlineKeyboardButton("🎧 Подкасты", callback_data="back_to_podcasts"))
            
            markup.add(*buttons)
            
            bot.send_message(
                chat_id,
                "Возможно, тебе будут полезны эти ресурсы:",
                reply_markup=markup,
                parse_mode='markdown'
            )

bot.infinity_polling()