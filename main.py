import anthropic
import openai
import os
import pyttsx3
import speech_recognition as sr
import tempfile
import threading
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from prompts import prompts
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from tkinter import scrolledtext
from tkinter import colorchooser
import configparser
from PIL import Image, ImageTk

should_go_to_tts_engine = False
should_go_back = False

recognizer = sr.Recognizer()

recognizer.non_speech_duration = 3
recognizer.energy_threshold = 300
recognizer.phrase_threshold = 0.3

voice_chat_running = False
stop_voice_chat_flag = False

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

def process_input_gpt(input_text: str, prompt_key: str, custom_prompt: str, input_mode: str, tts_engine: str, api_key: str, model: str, temperature: float, max_tokens: int, top_p: float, frequency_penalty: float, presence_penalty: float) -> str:
    try:
        openai.api_key = api_key
        messages = [
            {"role": "system", "content": custom_prompt if prompt_key == "Custom" else prompts[prompt_key]},
            {"role": "user", "content": input_text},
        ]

        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )

        bot_response = response["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": bot_response})

        print(f"Bot's response: {bot_response}")

        return bot_response
    except Exception as e:
        print(f"Error in process_input_gpt: {e}")
        return "I'm sorry, I encountered an error while processing your request."

def process_input_claude(input_text: str, prompt_key: str, custom_prompt: str, input_mode: str, tts_engine: str, api_key: str, model: str, temperature: float, max_tokens: int) -> str:
    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=custom_prompt if prompt_key == "Custom" else prompts[prompt_key],
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
        print(f"Error in process_input_claude: {e}")
        return "I'm sorry, I encountered an error while processing your request."

def process_input_thread(user_input, prompt_key, custom_prompt, tts_engine, ai_choice, input_type, api_key, temperature, max_tokens, top_p, frequency_penalty, presence_penalty):
    conversation_text.config(state=tk.NORMAL)

    # Process user input
    formatted_user_input = format_code_blocks(user_input)
    conversation_text.insert(tk.END, f"User: {formatted_user_input}\n", ("user", "code" if "<code>\n" in formatted_user_input else None))

    if ai_choice.startswith('gpt'):
        bot_response = process_input_gpt(user_input, prompt_key, custom_prompt, input_type, tts_engine, api_key, ai_choice, temperature, max_tokens, top_p, frequency_penalty, presence_penalty)
    else:
        bot_response = process_input_claude(user_input, prompt_key, custom_prompt, input_type, tts_engine, api_key, ai_choice, temperature, max_tokens)

    # Format the bot's response
    formatted_bot_response = format_code_blocks(bot_response)
    conversation_text.insert(tk.END, f"Bot: {formatted_bot_response}\n\n", ("bot", "code" if "<code>\n" in formatted_bot_response else None))
    conversation_text.see(tk.END)
    conversation_text.config(state=tk.DISABLED)

    if input_type != 'Text Only Chat':
        threading.Thread(target=synthesize_and_play_speech, args=(bot_response, tts_engine)).start()

    user_input_entry.delete('1.0', tk.END)

def format_code_blocks(text):
    # Replace code block delimiters with appropriate tags
    formatted_text = text.replace("```", "\n```\n")  # Add newlines around code blocks
    formatted_text = formatted_text.replace("```\n", "<code>\n")  # Start code block tag
    formatted_text = formatted_text.replace("\n```\n", "\n</code>\n")  # End code block tag
    return formatted_text

def process_input(event=None):
    user_input = user_input_entry.get("1.0", "end-1c")
    prompt_key = prompt_var.get()
    custom_prompt = custom_prompt_entry.get("1.0", "end-1c")
    tts_engine = tts_var.get()
    ai_choice = ai_var.get()
    input_type = input_var.get()
    api_key = api_key_entry.get()
    temperature = float(temperature_var.get())
    max_tokens = int(max_tokens_var.get())
    top_p = float(top_p_var.get())
    frequency_penalty = float(frequency_penalty_var.get())
    presence_penalty = float(presence_penalty_var.get())

    threading.Thread(target=process_input_thread, args=(user_input, prompt_key, custom_prompt, tts_engine, ai_choice, input_type, api_key, temperature, max_tokens, top_p, frequency_penalty, presence_penalty)).start()
def save_conversation_history(conversation_history):
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("PDF Files", "*.pdf")])
    if file_path:
        if file_path.endswith(".txt"):
            with open(file_path, "w") as file:
                file.write(conversation_history)
        elif file_path.endswith(".pdf"):
            # Implement PDF export functionality here
            pass

def load_conversation_history():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "r") as file:
            conversation_history = file.read()
            conversation_text.config(state=tk.NORMAL)
            conversation_text.delete("1.0", tk.END)
            conversation_text.insert(tk.END, conversation_history)
            conversation_text.config(state=tk.DISABLED)

def start_voice_chat():
    global voice_chat_running, stop_voice_chat_flag
    if voice_chat_running:
        print("Voice chat is already running.")
        return

    voice_chat_running = True
    stop_voice_chat_flag = False
    voice_chat_button.pack_forget()
    stop_voice_chat_button.pack(side=tk.RIGHT, padx=5)

    ai_choice = ai_var.get()
    prompt_key = prompt_var.get()
    custom_prompt = custom_prompt_entry.get("1.0", "end-1c")
    tts_engine = tts_var.get()
    api_key = api_key_entry.get()
    temperature = float(temperature_var.get())  # Get the value from temperature_var
    max_tokens = int(max_tokens_var.get())  # Get the value from max_tokens_var

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        while voice_chat_running and not stop_voice_chat_flag:
            audio = recognizer.listen(source)
            try:
                user_input = recognizer.recognize_google(audio)
                print(f"User said: {user_input}")

                conversation_text.config(state=tk.NORMAL)
                conversation_text.insert(tk.END, f"User: {user_input}\n", "user")

                if ai_choice.startswith('gpt'):
                    bot_response = process_input_gpt(user_input, prompt_key, custom_prompt, 'Voice Chat', tts_engine, api_key, ai_choice, temperature, max_tokens, top_p, frequency_penalty, presence_penalty)
                else:
                    bot_response = process_input_claude(user_input, prompt_key, custom_prompt, 'Voice Chat', tts_engine, api_key, ai_choice, temperature, max_tokens)

                conversation_text.insert(tk.END, f"Bot: {bot_response}\n\n", "bot")
                conversation_text.see(tk.END)
                conversation_text.config(state=tk.DISABLED)

                threading.Thread(target=synthesize_and_play_speech, args=(bot_response, tts_engine)).start()
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")

    stop_voice_chat_button.pack_forget()

    print("Voice chat ended.")

def stop_voice_chat():
    global voice_chat_running, stop_voice_chat_flag
    voice_chat_running = False
    stop_voice_chat_flag = True
    stop_voice_chat_button.pack_forget()
    voice_chat_button.pack(side=tk.RIGHT, padx=5)

def toggle_theme():
    if ctk.get_appearance_mode() == "Dark":
        ctk.set_appearance_mode("Light")
        theme_button.configure(text="Light Mode")
    else:
        ctk.set_appearance_mode("Dark")
        theme_button.configure(text="Dark Mode")

def toggle_sidebar():
    if sidebar_frame.winfo_viewable():
        sidebar_frame.pack_forget()
    else:
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

def save_settings():
    config = configparser.ConfigParser()
    config['Settings'] = {
        'prompt': prompt_var.get(),
        'custom_prompt': custom_prompt_entry.get("1.0", "end-1c"),
        'tts_engine': tts_var.get(),
        'ai_choice': ai_var.get(),
        'input_type': input_var.get(),
        'api_key': api_key_entry.get(),
        'theme': ctk.get_appearance_mode(),
        'font': font_var.get(),
        'background': background_var.get(),
        'temperature': temperature_var.get(),
        'max_tokens': max_tokens_var.get(),
        'top_p': top_p_var.get(),
        'frequency_penalty': frequency_penalty_var.get(),
        'presence_penalty': presence_penalty_var.get()
    }

    with open('config.cfg', 'w') as configfile:
        config.write(configfile)

def load_settings():
    config = configparser.ConfigParser()
    config.read('config.cfg')

    if 'Settings' in config:
        settings = config['Settings']
        prompt_var.set(settings.get('prompt', ''))
        custom_prompt_entry.delete('1.0', tk.END)
        custom_prompt_entry.insert(tk.END, settings.get('custom_prompt', ''))
        tts_var.set(settings.get('tts_engine', ''))
        ai_var.set(settings.get('ai_choice', ''))
        input_var.set(settings.get('input_type', ''))
        api_key_entry.insert(0, settings.get('api_key', ''))
        theme = settings.get('theme', 'Dark')
        ctk.set_appearance_mode(theme)
        theme_button.configure(text=f"{theme} Theme")
        font_var.set(settings.get('font', 'Arial'))
        change_font(None)
        background_var.set(settings.get('background', 'Default'))
        change_background(None)
        temperature_var.set(settings.get('temperature', '0.7'))
        max_tokens_var.set(settings.get('max_tokens', '2048'))
        top_p_var.set(settings.get('top_p', '1.0'))
        frequency_penalty_var.set(settings.get('frequency_penalty', '1.0'))
        presence_penalty_var.set(settings.get('presence_penalty', '0.0'))

def change_font(event):
    selected_font = font_var.get()
    conversation_text.configure(font=(selected_font, 20))
    user_input_entry.configure(font=(selected_font, 20))

def toggle_custom_prompt(event=None):
    if prompt_var.get() == "Custom":
        custom_prompt_entry.pack(fill=tk.X, padx=5, pady=5)
    else:
        custom_prompt_entry.pack_forget()

def save_custom_prompt():
    custom_prompt = custom_prompt_entry.get("1.0", "end-1c")
    if custom_prompt.strip():
        prompt_name = tk.simpledialog.askstring("Save Custom Prompt", "Enter a name for the custom prompt:")
        if prompt_name:
            prompts[prompt_name] = custom_prompt
            prompt_dropdown['values'] = list(prompts.keys()) + ["Custom"]
            prompt_var.set(prompt_name)
            custom_prompt_entry.delete('1.0', tk.END)
            custom_prompt_entry.pack_forget()

def change_background(event):
    background = background_var.get()
    if background == "Default":
        conversation_text.configure(bg="#222222")
        user_input_entry.configure(bg="#222222")
    elif background == "Custom":
        color = colorchooser.askcolor(title="Choose Custom Background Color")
        if color[1]:
            conversation_text.configure(bg=color[1])
            user_input_entry.configure(bg=color[1])
    else:
        conversation_text.configure(bg=background)
        user_input_entry.configure(bg=background)

advanced_settings_window = None

def show_advanced_settings(root):
    global advanced_settings_window

    if advanced_settings_window is None or not advanced_settings_window.winfo_exists():
        advanced_settings_window = ctk.CTkToplevel(root)
        advanced_settings_window.title("Advanced Settings")
        advanced_settings_window.geometry("300x400")  # Set the width to 400 pixels and height to 300 pixels
        advanced_settings_window.transient(root)  # Make the window a transient window of the main app

        temperature_label = ctk.CTkLabel(advanced_settings_window, text="Temperature:")
        temperature_label.pack(anchor=tk.W, padx=5, pady=5)
        temperature_entry = ctk.CTkEntry(advanced_settings_window, textvariable=temperature_var)
        temperature_entry.pack(fill=tk.X, padx=5, pady=5)

        max_tokens_label = ctk.CTkLabel(advanced_settings_window, text="Max Tokens:")
        max_tokens_label.pack(anchor=tk.W, padx=5, pady=5)
        max_tokens_entry = ctk.CTkEntry(advanced_settings_window, textvariable=max_tokens_var)
        max_tokens_entry.pack(fill=tk.X, padx=5, pady=5)

        top_p_label = ctk.CTkLabel(advanced_settings_window, text="Top P:")
        top_p_label.pack(anchor=tk.W, padx=5, pady=5)
        top_p_entry = ctk.CTkEntry(advanced_settings_window, textvariable=top_p_var)
        top_p_entry.pack(fill=tk.X, padx=5, pady=5)

        frequency_penalty_label = ctk.CTkLabel(advanced_settings_window, text="Frequency Penalty:")
        frequency_penalty_label.pack(anchor=tk.W, padx=5, pady=5)
        frequency_penalty_entry = ctk.CTkEntry(advanced_settings_window, textvariable=frequency_penalty_var)
        frequency_penalty_entry.pack(fill=tk.X, padx=5, pady=5)

        presence_penalty_label = ctk.CTkLabel(advanced_settings_window, text="Presence Penalty:")
        presence_penalty_label.pack(anchor=tk.W, padx=5, pady=5)
        presence_penalty_entry = ctk.CTkEntry(advanced_settings_window, textvariable=presence_penalty_var)
        presence_penalty_entry.pack(fill=tk.X, padx=5, pady=5)

        advanced_settings_window.lift()  # Bring the window to the foreground
    else:
        advanced_settings_window.lift()  # Bring the window to the foreground

def start_new_chat():
    conversation_text.config(state=tk.NORMAL)
    conversation_text.delete("1.0", tk.END)
    conversation_text.config(state=tk.DISABLED)
    user_input_entry.delete("1.0", tk.END)

def save_window_position(root):
    config = configparser.ConfigParser()

    # Get the current window position
    window_x = root.winfo_x()
    window_y = root.winfo_y()

    config['WindowPosition'] = {
        'x': str(window_x),
        'y': str(window_y)
    }

    with open('window_position.ini', 'w') as configfile:
        config.write(configfile)

def load_window_position(root):
    config = configparser.ConfigParser()
    config.read('window_position.ini')

    if 'WindowPosition' in config:
        window_position = config['WindowPosition']
        window_x = int(window_position.get('x', 0))
        window_y = int(window_position.get('y', 0))
        root.geometry(f"+{window_x}+{window_y}")


def create_main_window():
    global user_input_entry, prompt_var, tts_var, ai_var, input_var, conversation_text, api_key_entry, voice_chat_button, stop_voice_chat_button, theme_button, sidebar_frame, custom_prompt_entry, font_var, prompt_dropdown, background_var, temperature_var, max_tokens_var, top_p_var, frequency_penalty_var, presence_penalty_var

    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()
    root.title("PurposefulAI")
    root.geometry("1024x768")
    root.iconbitmap("icon.ico")  # Set the application icon

    load_window_position(root)

    def on_closing():
        save_window_position(root)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

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
    prompt_options = list(prompts.keys()) + ["Custom"]
    prompt_dropdown = ctk.CTkComboBox(sidebar_frame, variable=prompt_var, values=prompt_options, command=toggle_custom_prompt)
    prompt_dropdown.pack(fill=tk.X, padx=5, pady=5)

    custom_prompt_entry = ctk.CTkTextbox(sidebar_frame, height=100)
    custom_prompt_entry.pack(fill=tk.X, padx=5, pady=5)
    custom_prompt_entry.pack_forget()

    save_prompt_button = ctk.CTkButton(sidebar_frame, text="Save Custom Prompt", command=save_custom_prompt)
    save_prompt_button.pack(anchor=tk.W, padx=5, pady=5)

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

    api_key_label = ctk.CTkLabel(sidebar_frame, text="Enter your API key:")
    api_key_label.pack(anchor=tk.W, padx=5, pady=5)

    api_key_entry = ctk.CTkEntry(sidebar_frame, show="*")
    api_key_entry.pack(fill=tk.X, padx=5, pady=5)

    input_label = ctk.CTkLabel(sidebar_frame, text="Input type:")
    input_label.pack(anchor=tk.W, padx=5, pady=5)

    input_var = tk.StringVar()
    input_dropdown = ctk.CTkComboBox(sidebar_frame, variable=input_var, values=['Voice Chat', 'Text Input, Voice Output', 'Text Only Chat'])
    input_dropdown.pack(fill=tk.X, padx=5, pady=5)

    font_label = ctk.CTkLabel(sidebar_frame, text="Choose a font:")
    font_label.pack(anchor=tk.W, padx=5, pady=5)

    font_var = tk.StringVar()
    font_dropdown = ctk.CTkComboBox(sidebar_frame, variable=font_var, values=['Arial', 'Verdana', 'Segoe UI', 'Times New Roman', 'Courier New'], command=change_font)
    font_dropdown.pack(fill=tk.X, padx=5, pady=5)

    background_label = ctk.CTkLabel(sidebar_frame, text="Choose a background:")
    background_label.pack(anchor=tk.W, padx=5, pady=5)

    background_var = tk.StringVar()
    background_dropdown = ctk.CTkComboBox(sidebar_frame, variable=background_var, values=['Default', 'Black', 'White', 'Gray', 'Blue', 'Custom'], command=change_background)
    background_dropdown.pack(fill=tk.X, padx=5, pady=5)

    advanced_settings_button = ctk.CTkButton(sidebar_frame, text="Advanced Settings", command=lambda: show_advanced_settings(root))
    advanced_settings_button.pack(anchor=tk.W, padx=5, pady=5)

    temperature_var = tk.StringVar(value="0.7")
    max_tokens_var = tk.StringVar(value="2048")
    top_p_var = tk.StringVar(value="1.0")
    frequency_penalty_var = tk.StringVar(value="1.0")
    presence_penalty_var = tk.StringVar(value="0.0")

    # Create a toggle button for switching themes
    theme_button = ctk.CTkSwitch(sidebar_frame, text="Dark Theme", command=toggle_theme)
    theme_button.pack(anchor=tk.W, padx=5, pady=5)

    # Create a button to save settings
    save_button = ctk.CTkButton(sidebar_frame, text="Save Settings", command=save_settings)
    save_button.pack(anchor=tk.W, padx=5, pady=5)

    # Create a toggle button for the sidebar
    sidebar_button = ctk.CTkButton(output_frame, text="Toggle Sidebar", command=toggle_sidebar)
    sidebar_button.pack(anchor=tk.NE, padx=5, pady=5)

    conversation_label = ctk.CTkLabel(output_frame, text="Conversation Log:", font=("Segoe UI", 17, "bold"))
    conversation_label.pack(fill=tk.X)

    conversation_text = scrolledtext.ScrolledText(output_frame, height=15, font=("Segoe UI", 20), bg="#333333", fg="white", state=tk.DISABLED, padx=10, pady=10)
    conversation_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    conversation_text.tag_configure("code",  font=("Courier New", 20), foreground="green", background="black")

    conversation_text.tag_configure("user", foreground="light green")
    conversation_text.tag_configure("bot", foreground="light blue")

    user_input_label = ctk.CTkLabel(output_frame, text="User Input:", font=("Segoe UI", 17, "bold"))
    user_input_label.pack(fill=tk.X)

    user_input_entry = scrolledtext.ScrolledText(output_frame, height=5, font=("Segoe UI", 20), bg="#333333", fg="white", padx=10, pady=10)
    user_input_entry.pack(pady=10, padx=10, fill=tk.BOTH)

    button_frame = ctk.CTkFrame(output_frame)
    button_frame.pack(pady=5, fill=tk.X)

    submit_button = ctk.CTkButton(button_frame, text="Submit", command=process_input)
    submit_button.pack(side=tk.RIGHT, padx=5)

    save_conversation_button = ctk.CTkButton(button_frame, text="Save Conversation", command=lambda: save_conversation_history(conversation_text.get("1.0", tk.END)))
    save_conversation_button.pack(side=tk.RIGHT, padx=5)

    load_conversation_button = ctk.CTkButton(button_frame, text="Load Conversation", command=load_conversation_history)
    load_conversation_button.pack(side=tk.RIGHT, padx=5)

    new_chat_button = ctk.CTkButton(button_frame, text="New Chat", command=start_new_chat)
    new_chat_button.pack(side=tk.RIGHT, padx=5)

    voice_chat_button = ctk.CTkButton(button_frame, text="Start Voice Chat", fg_color="green", command=lambda: threading.Thread(target=start_voice_chat).start())
    voice_chat_button.pack(side=tk.RIGHT, padx=5)

    stop_voice_chat_button = ctk.CTkButton(button_frame, text="Stop Voice Chat", command=stop_voice_chat, fg_color="red")

    load_settings()

    user_input_entry.bind("<Return>", process_input)
    user_input_entry.focus_set()

    root.mainloop()

def main():
    # Create the splash screen
    splash_root = tk.Tk()
    splash_root.title("PurposefulAI")
    splash_root.geometry("1280x720")  # Adjust the size as needed
    splash_root.overrideredirect(True)
    splash_frame = tk.Frame(splash_root, bg="black", bd=1)  # Set the desired border color here
    splash_frame.pack(expand=True, fill="both")

    # Load and display the logo image inside the custom frame
    logo_image = Image.open("logo11.png")
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(splash_frame, image=logo_photo, bg="black")  # Set the background color to match the border
    logo_label.pack(expand=True)

    # Center the splash screen
    splash_root.update()
    screen_width = splash_root.winfo_screenwidth()
    screen_height = splash_root.winfo_screenheight()
    x = (screen_width - 1280) // 2
    y = (screen_height - 720) // 2
    splash_root.geometry(f"+{x}+{y}")

    # Update the splash screen
    splash_root.update()

    # Function to destroy the splash screen and create the main window
    def create_main_window_delayed():
        splash_root.destroy()
        create_main_window()

    # Schedule the creation of the main window after a delay
    splash_root.after(2000, create_main_window_delayed)

    splash_root.mainloop()

if __name__ == "__main__":
    main()