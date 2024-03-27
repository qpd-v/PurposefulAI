import anthropic
import asyncio
import keyboard
import openai
import os
import pyttsx3
import queue
import speech_recognition as sr
import tempfile
import threading
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from prompts import prompts

import tkinter as tk
import customtkinter as ctk
from tkinter import ttk
from tkinter import scrolledtext
import configparser

should_go_to_tts_engine = False
should_go_back = False

recognizer = sr.Recognizer()

recognizer.non_speech_duration = 3
recognizer.energy_threshold = 300
recognizer.phrase_threshold = 0.3

voice_chat_running = False

def speak_with_pyttsx3(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def synthesize_and_play_speech(text, tts_engine):
    if tts_engine == "Google Text-to-Speech":
        tts = gTTS(str(text), lang="en", slow=False)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)

        audio = AudioSegment.from_file(temp_file.name, format="mp3")
        play(audio)

        temp_file.close()
        os.unlink(temp_file.name)
    elif tts_engine == "Python Text-to-Speech":
        speak_with_pyttsx3(text)

def process_input_gpt(input_text: str, prompt_key: str, input_mode: str, tts_engine: str, api_key: str, model: str) -> str:
    openai.api_key = api_key
    messages = [
        {"role": "system", "content": prompts[prompt_key]},
        {"role": "user", "content": input_text},
    ]

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=1,
        presence_penalty=0,
    )

    bot_response = response["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": bot_response})

    print(f"Bot's response: {bot_response}")

    return bot_response

def process_input_claude(input_text: str, prompt_key: str, input_mode: str, tts_engine: str, api_key: str, model: str) -> str:
    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=model,
            max_tokens=2048,
            temperature=0.7,
            system=prompts[prompt_key],
            messages=[{"role": "user", "content": input_text}]
        )

        bot_response = message.content
        if isinstance(bot_response, str):
            bot_response = bot_response.strip()
        elif isinstance(bot_response, list):
            bot_response = "".join(block.text for block in bot_response)

        print(f"Bot's response: {bot_response}")
        return bot_response
    except Exception as e:
        print(f"Error: {e}")
        return "I'm sorry, I encountered an error while processing your request."

def process_input(event=None):
    user_input = user_input_entry.get("1.0", "end-1c")
    prompt_key = prompt_var.get()
    tts_engine = tts_var.get()
    ai_choice = ai_var.get()
    input_type = input_var.get()
    api_key = api_key_entry.get()

    conversation_text.config(state=tk.NORMAL)
    conversation_text.insert(tk.END, f"User: {user_input}\n")

    if ai_choice.startswith('gpt'):
        bot_response = process_input_gpt(user_input, prompt_key, input_type, tts_engine, api_key, ai_choice)
    else:
        bot_response = process_input_claude(user_input, prompt_key, input_type, tts_engine, api_key, ai_choice)

    conversation_text.insert(tk.END, f"Bot: {bot_response}\n\n")
    conversation_text.see(tk.END)
    conversation_text.config(state=tk.DISABLED)

    if input_type != 'Text Only Chat':
        threading.Thread(target=synthesize_and_play_speech, args=(bot_response, tts_engine)).start()

    user_input_entry.delete('1.0', tk.END)

def start_voice_chat():
    global voice_chat_running
    if voice_chat_running:
        print("Voice chat is already running.")
        return

    voice_chat_running = True
    voice_chat_button.pack_forget()
    stop_voice_chat_button.pack(side=tk.LEFT, padx=5)

    ai_choice = ai_var.get()
    prompt_key = prompt_var.get()
    tts_engine = tts_var.get()
    api_key = api_key_entry.get()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        while voice_chat_running:
            audio = recognizer.listen(source)
            try:
                user_input = recognizer.recognize_google(audio)
                print(f"User said: {user_input}")

                conversation_text.config(state=tk.NORMAL)
                conversation_text.insert(tk.END, f"User: {user_input}\n")

                if ai_choice.startswith('gpt'):
                    bot_response = process_input_gpt(user_input, prompt_key, 'Voice Chat', tts_engine, api_key, ai_choice)
                else:
                    bot_response = process_input_claude(user_input, prompt_key, 'Voice Chat', tts_engine, api_key, ai_choice)

                conversation_text.insert(tk.END, f"Bot: {bot_response}\n\n")
                conversation_text.see(tk.END)
                conversation_text.config(state=tk.DISABLED)

                threading.Thread(target=synthesize_and_play_speech, args=(bot_response, tts_engine)).start()
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")

    stop_voice_chat_button.pack_forget()
    voice_chat_button.pack(side=tk.LEFT, padx=5)
    print("Voice chat ended.")

def stop_voice_chat():
    global voice_chat_running
    voice_chat_running = False

def toggle_theme():
    if ctk.get_appearance_mode() == "Dark":
        ctk.set_appearance_mode("Light")
        theme_button.configure(text="Light Theme")
    else:
        ctk.set_appearance_mode("Dark")
        theme_button.configure(text="Dark Theme")

def toggle_sidebar():
    if sidebar_frame.winfo_viewable():
        sidebar_frame.pack_forget()
    else:
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

def save_settings():
    config = configparser.ConfigParser()
    config['Settings'] = {
        'prompt': prompt_var.get(),
        'tts_engine': tts_var.get(),
        'ai_choice': ai_var.get(),
        'input_type': input_var.get(),
        'api_key': api_key_entry.get(),
        'theme': ctk.get_appearance_mode()
    }

    with open('config.cfg', 'w') as configfile:
        config.write(configfile)

def load_settings():
    config = configparser.ConfigParser()
    config.read('config.cfg')

    if 'Settings' in config:
        settings = config['Settings']
        prompt_var.set(settings.get('prompt', ''))
        tts_var.set(settings.get('tts_engine', ''))
        ai_var.set(settings.get('ai_choice', ''))
        input_var.set(settings.get('input_type', ''))
        api_key_entry.insert(0, settings.get('api_key', ''))
        theme = settings.get('theme', 'Dark')
        ctk.set_appearance_mode(theme)
        theme_button.configure(text=f"{theme} Theme")

def main():
    global user_input_entry, prompt_var, tts_var, ai_var, input_var, conversation_text, api_key_entry, voice_chat_button, stop_voice_chat_button, theme_button, sidebar_frame

    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("PurposefulAI")
    root.geometry("1024x768")

    main_frame = ctk.CTkFrame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Create and pack the frames
    sidebar_frame = ctk.CTkFrame(main_frame)
    sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    output_frame = ctk.CTkFrame(main_frame)
    output_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Create and pack the input elements in the sidebar
    prompt_label = ctk.CTkLabel(sidebar_frame, text="Choose a set of prompts:")
    prompt_label.pack(anchor=tk.W, padx=5, pady=5)

    prompt_var = tk.StringVar()
    prompt_dropdown = ctk.CTkComboBox(sidebar_frame, variable=prompt_var, values=list(prompts.keys()))
    prompt_dropdown.pack(fill=tk.X, padx=5, pady=5)

    tts_label = ctk.CTkLabel(sidebar_frame, text="Choose a text-to-speech engine:")
    tts_label.pack(anchor=tk.W, padx=5, pady=5)

    tts_var = tk.StringVar()
    tts_dropdown = ctk.CTkComboBox(sidebar_frame, variable=tts_var, values=['Google Text-to-Speech', 'Python Text-to-Speech'])
    tts_dropdown.pack(fill=tk.X, padx=5, pady=5)

    ai_label = ctk.CTkLabel(sidebar_frame, text="Which AI do you want to use?")
    ai_label.pack(anchor=tk.W, padx=5, pady=5)

    ai_var = tk.StringVar()
    ai_dropdown = ctk.CTkComboBox(sidebar_frame, variable=ai_var, values=[
        'gpt-3.5-turbo',
        'gpt-3.5-turbo-16k',
        'gpt-4',
        'gpt-4-0613',
        'gpt-4-32k-0613',
        'gpt-4-32k',
        'gpt-4-0125-preview',
        'gpt-4-turbo-preview',
        'gpt-4-1106-preview',
        'gpt-4-vision-preview',
        'gpt-4-1106-vision-preview',
        '-----------------------',
        'claude-3-opus-20240229',
        'claude-3-sonnet-20240229',
        'claude-3-haiku-20240307',
        'claude-2.1',
        'claude-2.0',
        'claude-1.3',
        'claude-instant-1.2',
        'claude-instant-1.1',
        'claude-instant-v1',
        'claude-instant-v1-100k',
        'claude-v1',
        'claude-v1-100k'
    ])
    ai_dropdown.pack(fill=tk.X, padx=5, pady=5)

    api_key_label = ctk.CTkLabel(sidebar_frame, text="Enter the API key:")
    api_key_label.pack(anchor=tk.W, padx=5, pady=5)

    api_key_entry = ctk.CTkEntry(sidebar_frame, show="*")
    api_key_entry.pack(fill=tk.X, padx=5, pady=5)

    input_label = ctk.CTkLabel(sidebar_frame, text="Input type:")
    input_label.pack(anchor=tk.W, padx=5, pady=5)

    input_var = tk.StringVar()
    input_dropdown = ctk.CTkComboBox(sidebar_frame, variable=input_var, values=['Voice Chat', 'Text Input, Voice Output', 'Text Only Chat'])
    input_dropdown.pack(fill=tk.X, padx=5, pady=5)

    # Create a toggle button for switching themes
    theme_button = ctk.CTkSwitch(sidebar_frame, text="Dark Theme", command=toggle_theme)
    theme_button.pack(anchor=tk.W, padx=5, pady=5)

    # Create a button to save settings
    save_button = ctk.CTkButton(sidebar_frame, text="Save Settings", command=save_settings)
    save_button.pack(anchor=tk.W, padx=5, pady=5)

    # Create a toggle button for the sidebar
    sidebar_button = ctk.CTkButton(output_frame, text="Toggle Sidebar", command=toggle_sidebar)
    sidebar_button.pack(anchor=tk.NE, padx=5, pady=5)

    conversation_label = ctk.CTkLabel(output_frame, text="Conversation:", font=("Arial", 18, "bold"))
    conversation_label.pack(fill=tk.X)

    conversation_text = scrolledtext.ScrolledText(output_frame, height=15, font=("Arial", 18), bg="#333333", fg="white", state=tk.DISABLED)
    conversation_text.pack(pady=5, fill=tk.BOTH, expand=True)

    user_input_label = ctk.CTkLabel(output_frame, text="User Input:", font=("Arial", 18, "bold"))
    user_input_label.pack(fill=tk.X)

    user_input_entry = scrolledtext.ScrolledText(output_frame, height=5, font=("Arial", 18), bg="#333333", fg="white")
    user_input_entry.pack(pady=5, fill=tk.BOTH)

    button_frame = ctk.CTkFrame(output_frame)
    button_frame.pack(pady=5, fill=tk.X)

    submit_button = ctk.CTkButton(button_frame, text="Submit", command=process_input)
    submit_button.pack(side=tk.LEFT, padx=5)

    voice_chat_button = ctk.CTkButton(button_frame, text="Start Voice Chat", command=lambda: threading.Thread(target=start_voice_chat).start())
    voice_chat_button.pack(side=tk.LEFT, padx=5)

    stop_voice_chat_button = ctk.CTkButton(button_frame, text="Stop Voice Chat", command=stop_voice_chat)

    load_settings()

    user_input_entry.bind("<Return>", process_input)
    user_input_entry.focus_set()

    root.mainloop()

if __name__ == "__main__":
    main()