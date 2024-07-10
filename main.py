import tkinter as tk
import time
import threading
import g4f
import speech_recognition as sr
from gtts import gTTS
import playsound

# Установка политики событий для селектора Windows
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Создаем глобальные переменные
messages = []
response_text = ""
chat_active = False  # Флаг активности чата

# Инициализация распознавания речи
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Функция для обработки запроса к Tars
def ask_tars(messages):
    global response_text
    response = g4f.ChatCompletion.create(
        model=g4f.models.gpt_35_turbo,
        messages=messages
    )
    response_text = response
    speak_response(response_text)  # Озвучиваем ответ Tars

# Функция для озвучивания текста
def speak_response(text):
    tts = gTTS(text=text, lang='ru')
    tts.save("response.mp3")
    playsound.playsound("response.mp3", True)

# Функция для имитации печати текста
def type_text(widget, text):
    for character in text:
        widget.insert(tk.END, character)
        time.sleep(0.05)  # регулируйте скорость печати здесь
        widget.update_idletasks()

# Функция для обработки речи и отправки сообщения
def process_speech():
    global chat_active

    while True:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Говорите...")
            audio = recognizer.listen(source)

        try:
            user_input = recognizer.recognize_google(audio, language="ru-RU")
            print(f"Вы сказали: {user_input}")

            if user_input.lower() == "пока":
                type_text(chat_history, "Tars: Пока!\n")
                speak_response('Пока!')
                chat_active = False
            elif user_input.lower() == "давай поговорим":
                type_text(chat_history, "Tars: Привет! Давай.\n")
                speak_response('Привет! Давай.')
                chat_active = True
                threading.Thread(target=ask_tars, args=(messages,)).start()
            elif chat_active:
                messages.append({"role": "user", "content": user_input})
                type_text(chat_history, f"You: {user_input}\n")
                threading.Thread(target=ask_tars, args=(messages,)).start()

        except sr.UnknownValueError:
            pass  # Ничего не делаем, просто ждем следующей попытки распознавания
        except sr.RequestError as e:
            pass

# Создаем графический интерфейс Tkinter
root = tk.Tk()
root.title("Chat with Tars")
root.geometry("480x320")
root.configure(bg="black")

# Создаем стиль для зеленого текста
style = tk.StringVar()
style.set('green')

# Создаем виджеты
chat_history = tk.Text(root, width=60, height=20, fg='green', bg='black', font=('Arial', 12))
chat_history.pack(padx=10, pady=10)

# Функция для обновления интерфейса с ответом от Tars
def update_interface():
    global response_text
    if response_text:
        response_text_without_prefix = response_text.split(": ", 1)[-1]  # Удаляем префикс "Tars: "
        type_text(chat_history, f"Tars: {response_text_without_prefix}\n")
        response_text = ""
    root.after(100, update_interface)

# Запускаем обновление интерфейса
update_interface()

# Запускаем поток для обработки речи
threading.Thread(target=process_speech).start()

# Запускаем главный цикл Tkinter
root.mainloop()
