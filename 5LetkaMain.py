import telebot
import os

TOKEN = ''

bot = telebot.TeleBot(TOKEN)

# Если нет папки "users", создаём эту папку
if not(os.path.exists('users')):
    os.mkdir('users')

keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)  # Клавиатура для основных функций
keyboard1.row('/new_item', '/all', '/delete', '/help')

keyboard2 = telebot.types.ReplyKeyboardMarkup(True, True)  # Клавиатура для ответа на наличие фото
keyboard2.row('Да', 'Нет')

def rightDirectory(message):
    # Проверяем, что мы находимся в нужной директории и что вообще такая директория существует
    directory = os.getcwd()
    if not (str(message.from_user.id) in directory):
        directory = os.getcwd() + f'\\users\\{message.from_user.first_name}_{message.from_user.last_name}_{message.from_user.id}'
    if not (os.path.exists(directory)):
        os.mkdir(directory)
    os.chdir(directory)
    return directory


@bot.message_handler(commands=['start'])
def start_handler(message):
    # Приветствуем пользователя, выводим клавиатуру с осн. функ.
    bot.send_message(message.from_user.id, "Здравствуй, товарищ! Готов начать новую пятелетку? Вот наш функционал:"
                                           "\n/new_item - добавить новую задачу"
                                           "\n/all - посмотреть все задачи"
                                           "\n/delete - удалить задачу (необходимо знать её номер)"
                                           "\n/help - помощь", reply_markup=keyboard1)
    directory = rightDirectory(message)
    # Проверяем, что в папке пользователя существует файл с данными его списка и если нет, то его создаём
    if not(os.path.exists('data.txt')):
        f = open('data.txt', 'w')
        f.close()


@bot.message_handler(commands=['new_item'])
def startMessage(message):
    # Просим пользователя ввести задачу, переходим к step-у с описанием
    msg = bot.reply_to(message, "Введите задачу")
    bot.register_next_step_handler(msg, descript)

def descript(message):
    # Запоминаем task, спрашиваем пользователя о фото, переходим к step-у с условием
    try:
        global task
        task = message.text
        msg = bot.reply_to(message, "Прикрепить фотокарточку?", reply_markup=keyboard2)
        bot.register_next_step_handler(msg, condition)
    except Exception as e:
        bot.reply_to(message, 'Что-то пошло не так...')

def condition(message):
    # В зависимости от ответа переходим либо в step для получения фотографии, либо просто в добавление задачи
    try:
        answer = message.text
        if answer == "Да":
            msg = bot.reply_to(message, "Отлично, отправьте фото")
            bot.register_next_step_handler(msg, getPhoto)
        else:
            addTask(message)
    except Exception as e:
        bot.reply_to(message, 'Что-то пошло не так...', reply_markup = keyboard1)

def getPhoto(message):
    # Получаем фото и сохраняем
    try:
        photo = message.photo[-1]
        file_id = photo.file_id
        file_path = bot.get_file(file_id).file_path
        downloaded_file = bot.download_file(file_path)
        downloaded_file = bot.download_file(file_path)
        name = file_id + ".jpg"
        directory = rightDirectory(message)
        new_file = open(directory + '/' + name, mode='wb')
        new_file.write(downloaded_file)
        new_file.close()
        addTask(message, namephoto=name)
    except Exception as e:
        msg = bot.reply_to(message, 'Что-то пошло не так... Попробуйте ещё раз отправить фото')
        bot.register_next_step_handler(msg, getPhoto)

def addTask(message, namephoto = ''):
    # Открываем файл с данными, находим последний ID и заносим нашу задачу с ID+1
    # в формате {ID}|{task}|{namephoto = '' (по умолчанию)}
    try:
        directory = rightDirectory(message)
        if not(os.stat('data.txt').st_size == 0):
            f = open('data.txt', 'r', encoding='utf8')
            lines = f.readlines()
            f.close()
            f = open('data.txt', 'a', encoding='utf8')
            lastID = lines[-1].split('|')[0]
            f.write(f'{int(lastID) + 1}|{task}|{namephoto}\n')
            f.close()
        else:
            f = open('data.txt', 'a', encoding='utf8')
            f.write(f'1|{task}|{namephoto}\n')
            f.close()
        bot.send_message(message.chat.id, "Задача добавлена!", reply_markup = keyboard1)

    except Exception as e:
        bot.reply_to(message, 'Что-то пошло не так...', reply_markup = keyboard1)


@bot.message_handler(commands=['all'])
def print(message):
    # Читаем файл с данными
    try:
        directory = rightDirectory(message)
        f = open('data.txt', 'r', encoding='utf8')
        file = [x.split('|') for x in f.read().split('\n')]
        for i in file:
            if i == ['']:  # Обрабатываем случай, когда список пустой
                # или .splt('\n') добавляет лишний элемент в виде ['']
                break
            bot.send_message(message.chat.id, '. '.join(i[:2]))
            if i[2] != '':  # Если есть фото, то выводим
                photo = open(i[2], 'rb')
                bot.send_photo(message.from_user.id, photo)
                photo.close()
        f.close()
    except Exception as e:
        bot.reply_to(message, 'Что-то пошло не так...', reply_markup = keyboard1)

@bot.message_handler(commands=['delete'])
def startMessage(message):
    # Выводим сообщение, переходим к step-у с удалением
    msg = bot.send_message(message.from_user.id, "Введите номер задачи, которую Вы хотите удалить. Если передумали, то введите '0' (без апострофов)")
    bot.register_next_step_handler(msg, delete)
def delete(message):
    number = message.text
    if number == '0':
        # Выходим из удаления, если пользователь передумал
        bot.send_message(message.from_user.id, "Хорошо, возвращаемся в основное меню", reply_markup=keyboard1)
    else:
        try:
            number = int(number)  # если пользователь пришлёт не число, то нас перекинет в except
            directory = rightDirectory(message)
            f = open('data.txt', 'r', encoding='utf8')
            file = [x.split('|') for x in f.read().split('\n')]
            file = file[:-1]  # обрабатываем случай, когда .split() добавляет лишний элемент
            s = ''
            j = 0  # отражает новую нумерацию после удаления
            for i in file:
                if i[0] == str(number):
                    # Убираем фото
                    if i[2] != '':
                        os.remove(i[2])
                else:
                    j += 1
                    s += str(j) + '|' + '|'.join(i[1:]) + '\n'
            f = open('data.txt', 'w', encoding='utf8')
            f.write(s)
            f.close()
            bot.send_message(message.from_user.id, "Задача успешно удалена!", reply_markup=keyboard1)
        except Exception as e:
            msg = bot.reply_to(message, 'Некорректный ввод - попробуйте ещё раз')
            bot.register_next_step_handler(msg, delete)

@bot.message_handler(commands=['help'])
def help_handler(message):
    bot.send_message(message.from_user.id, "/start - идентификация пользователя"
                                           "\n/new_item - добавить новую задачу"
                                           "\n/all - посмотреть список задач"
                                           "\n/delete - удалить задачу (необходимо знать номер)", reply_markup = keyboard1)


bot.polling()