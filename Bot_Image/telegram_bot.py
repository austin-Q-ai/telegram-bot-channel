# Telegram library
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ContentType
from aiogram.types import ContentType, InlineKeyboardMarkup, InlineKeyboardButton
# Main Process
from sqlalchemy.orm import Session
from src.model.database import SessionLocal, engine
from src.model import crud
from src.model import models
from src.text2text import text_response
from src.text2video import video_response
from src.speech2text.speech_to_text import speech_to_text
from src.handle_issues.handle_issues import checkout_default_answer
from src.handle_issues.default_answer import ANSWER_1, ANSWER_2

import requests
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='config.env')

""" Telegram Bot Inint """
# Set Bot Token and Name
Telegram_key = os.getenv('Telegram_key')
Bot_name = os.getenv('Bot_name')

# bot config
bot = Bot(token=Telegram_key)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Bot Database Init
models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

# API Available
brain_available = True
video_available = True

# News Available
user_available = {}

# Users File
is_running = {}

# loading Cube
loading_cube ="Iphone-spinner-2.gif"

# Mode to Select the Response Method: Text, Video, Hybird
button = InlineKeyboardButton(text="Set Response Method", callback_data="Method")
button1 = InlineKeyboardButton(text="Text", callback_data="Text")
button2 = InlineKeyboardButton(text="Video", callback_data="Video")
button3 = InlineKeyboardButton(text="Hybrid", callback_data="Hybrid")

method_choose = InlineKeyboardMarkup().add(button)
method_items = InlineKeyboardMarkup().add(button1, button2, button3)

# Check out Default Answer
default_answer = checkout_default_answer()

def response_with_default_answer():
    global default_answer
    global video_available
    if not default_answer:
        default_answer = checkout_default_answer()
    video_available = default_answer
    
    return default_answer


print("\n\n===================== Start Telegram Bot =======================\n\n")

# Handle the click event of customer response method buttons
@dp.callback_query_handler(text=["Method", "Text", "Video", "Hybrid"])
async def check_button(call: types.CallbackQuery):
    id = call["from"].id
    if is_running.get(str(id)):
        # Checking which button is pressed and respond accordingly
        if call.data == "Method":
            await bot.send_message(chat_id=id, text="Please, select the response method.\n1. Text': I'll always reply with text.\n2. Video: I'll always respond with video\n3. Hybrid: I'll respond to texts and videos accordingly: text for text, voice for video.", reply_markup=method_items)
        elif call.data == "Text":
            user = crud.update_repsonse(db=db, id=id, response="Text")
            if not user:
                await bot.send_message(chat_id=id, text="Oops! Looks like there's a temporary glitch in setting the response method. Please wait a few minutes and try again by sending the message '/reset'. Apologies for any inconvenience caused!")
            else:
                await bot.send_message(chat_id=id, text="Successfully completed. I will only reply with text. If you want to reset, send the message '/reset'.")
        elif call.data == "Video":
            user = crud.update_repsonse(db=db, id=id, response="Video")
            if not user:
                await bot.send_message(chat_id=id, text="Oops! Looks like there's a temporary glitch in setting the response method. Please wait a few minutes and try again by sending the message '/reset'. Apologies for any inconvenience caused!")
            else:
                await bot.send_message(chat_id=id, text="Successfully completed. I will only reply with video. If you want to reset, send the message '/reset'.")
        elif call.data == "Hybrid":
            user = crud.update_repsonse(db=db, id=id, response="Hybrid")
            if not user:
                await bot.send_message(chat_id=id, text="Oops! Looks like there's a temporary glitch in setting the response method. Please wait a few minutes and try again by sending the message '/reset'. Apologies for any inconvenience caused!")
            else:
                await bot.send_message(chat_id=id, text="Successfully completed. I will only reply with text. If you want to reset, send the message '/reset'.")            
    else:
        pass

# Handle the "/start" command
@dp.message_handler(content_types=types.ContentType.CONTACT)
async def start_button_click(message: types.Message):
    pass


# Handle the "/start" command
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    global is_running
    global user_available
    global video_available
    global Bot_name
    is_running[str(message.chat.id)] = True
    user_available[str(message.chat.id)] = video_available
    user = crud.get_user_by_id(db=db, id=message.chat.id)
    if not user:
        if crud.create_user(db=db, id=message.chat.id):
            await bot.send_message(chat_id=message.chat.id, text=f'Hi, It\'s {Bot_name} . How is it going? I can talk to you via text or video, and you can choose the approach that suits you best. If you would like to set the response method, please click the button.', reply_markup=method_choose)
        else:
            await bot.send_message(chat_id=message.chat.id, text="I apologize, but my schedule is currently packed, and I'm unable to meet with anyone at the moment due to my busy workload.")
    elif user.response == None:
        await bot.send_message(chat_id=message.chat.id, text=f'Hi, It\'s {Bot_name} . How is it going?', reply_markup=method_choose)
    else:
        await bot.send_message(chat_id=message.chat.id, text=f'Hi, It\'s {Bot_name} . How is it going?')

# Handle the "/stop" command
@dp.message_handler(commands=["stop"])
async def stop_command(message: types.Message):
    global is_running
    is_running.pop(str(message.chat.id))
    user_available.pop(str(message.chat.id))
    await bot.send_message(chat_id=message.chat.id, text="Thank you, Nice talking to you.")

# Handle the "/reset" command
@dp.message_handler(commands=["reset"])
async def reset_commnad(message: types.Message):
    if is_running.get(str(message.chat.id)):
        await bot.send_message(chat_id=message.chat.id, text="Please, select the response method.\n1. Text': I'll always reply with text.\n2. Video: I'll always respond with video\n3. Hybrid: I'll respond to texts and videos accordingly: text for text, voice for video.", reply_markup=method_items)
    else:
        pass

# Handle incoming messages
@dp.message_handler()
async def handle_message(message: types.Message):
    print("\n-/-/-/-/-/-/-/-/-/-/-/- New Message -/-/-/-/-/-/-/-/-/-/-/-\n")
    global is_running
    global brain_available
    global video_available
    # user question
    text = message.text 
    print("User Question: ", text)
    # checkout this conversation is started
    if is_running.get(str(message.chat.id)):
        # Send loading cube
        with open(loading_cube, "rb") as f:
            cube = await bot.send_animation(chat_id=message.chat.id, animation = f, duration=0)
        # Making the answer - HongYu APIs
        print("---------------------- making answer ------------------------")
        user = crud.get_user_by_id(db=db, id=message.chat.id)  # Find user with chat.id
        answer = text_response.get_response(chat_id=user.chat_id, text=text)  # request and receive to the HongYu API
        print("Answer: ", answer)
        # Check out user response method
        if answer == ANSWER_1: # The answer is default answer : handle errors
            brain_available = False
            await bot.delete_message(chat_id=message.chat.id, message_id=cube.message_id)
            if response_with_default_answer():
                with open("default_answer/answer_1.mp4", "rb") as f:
                    await bot.send_video(chat_id=message.chat.id, video = f, duration=0)
            else:
                await bot.send_message(chat_id=message.chat.id, text=answer)
        else:
            if user.response =="Text" or user.response == "Hybrid":
                await bot.delete_message(chat_id=message.chat.id, message_id=cube.message_id)
                await bot.send_message(chat_id=message.chat.id, text=answer)
            else:
                print("---------------------- Genearting Video ------------------------")
                result = video_response.get_video_response(text=answer)
                if result == ANSWER_2:
                    video_available = False
                await bot.delete_message(chat_id=message.chat.id, message_id=cube.message_id)
                if video_available:
                    user_available[str(message.chat.id)] = video_available
                    await bot.send_video(chat_id=message.chat.id, video = result, duration=0)
                elif video_available != user_available[str(message.chat.id)]:
                    user_available[str(message.chat.id)] = video_available
                    await bot.send_message(chat_id=message.chat.id, text=answer +"\n"+ result)
                else:
                    await bot.send_message(chat_id=message.chat.id, text=answer)
    else:
        pass
    print("-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-")

# Handle the voice message
@dp.message_handler(content_types=['voice'])
async def handle_voice(message: types.Message):
    global is_running
    global brain_available
    global video_available
    print("\n-/-/-/-/-/-/-/-/-/-/-/- New Message -/-/-/-/-/-/-/-/-/-/-/-\n")

    os.makedirs("voice_message", exist_ok=True)
    voice_message = f'voice_message/{message.chat.id}.ogg'
    file_id = message.voice.file_id
    # Get the file path from Telegram servers
    file_path = await bot.get_file(file_id)
    file_path = file_path.file_path
    file = requests.get("https://api.telegram.org/file/bot{0}/{1}".format(Telegram_key, file_path))
    # Save the file to disk
    with open(voice_message, "wb") as f:
        f.write(file.content)
    
    print("------------------ Voice to Text ---------------------")
    text = speech_to_text(message.chat.id)
    print("User Question: ", text)

    if is_running.get(str(message.chat.id)):
        with open(loading_cube, "rb") as f:
            cube = await bot.send_animation(chat_id=message.chat.id, animation = f, duration=0)
        print(cube)
        print("---------------------- making answer ------------------------")
        user = crud.get_user_by_id(db=db, id=message.chat.id)  # Find user with chat.id
        answer = text_response.get_response(chat_id=user.chat_id, text=text)  # request and receive to the HongYu API
        print("Answer: ", answer)
        # Check out user response method
        if answer == ANSWER_1: # The answer is default answer : handle errors
            brain_available = False
            await bot.delete_message(chat_id=message.chat.id, message_id=cube.message_id)
            if response_with_default_answer():
                with open("default_answer/answer_1.mp4", "rb") as f:
                    await bot.send_video(chat_id=message.chat.id, video = f, duration=0)
            else:
                await bot.send_message(chat_id=message.chat.id, text=answer)
        else:
            if user.response =="Text" or user.response == "Hybrid":
                await bot.delete_message(chat_id=message.chat.id, message_id=cube.message_id)
                await bot.send_message(chat_id=message.chat.id, text=answer)
            else:
                print("---------------------- Genearting Video ------------------------")
                result = video_response.get_video_response(text=answer)
                if result == ANSWER_2:
                    video_available = False
                await bot.delete_message(chat_id=message.chat.id, message_id=cube.message_id)
                if video_available:
                    user_available[str(message.chat.id)] = video_available
                    await bot.send_video(chat_id=message.chat.id, video = result, duration=0)
                elif video_available != user_available[str(message.chat.id)]:
                    user_available[str(message.chat.id)] = video_available
                    await bot.send_message(chat_id=message.chat.id, text=answer +"\n"+ result)
                else:
                    await bot.send_message(chat_id=message.chat.id, text=answer)
    else:
        pass
    print("-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-")


if __name__ == "__main__":
    
    dp.register_message_handler(start_button_click, content_types=ContentType.CONTACT)
    executor.start_polling(dp)
