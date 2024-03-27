![Purposeful-AI-Logo](https://github.com/qpd-v/PurposefulAI/assets/124479925/af9a048d-7863-4077-ba33-3ebb0c559a6a)

# PurposefulAI v1.0

PurposefulAI is a versatile AI assistant application that leverages the power of OpenAI's GPT and Anthropic's Claude models (more to come!) to provide a wide range of functionalities. 

It has voice chat functionality and a user-friendly interface with customizable settings. 


Dark Mode:
![Screenshot---DARK](https://github.com/qpd-v/PurposefulAI/assets/124479925/04cc1af1-2659-4e40-8e33-262027d5d19d)

Light Mode:
![Screenshot---LIGHT](https://github.com/qpd-v/PurposefulAI/assets/124479925/e174a8a8-31ad-4f00-a06c-9a3102297b4a)


## Version 1 Features

- **Multi-Modal Input**: PurposefulAI supports text input, voice input, and a combination of both, allowing you to interact with the AI assistant in a way that suits your preferences. More modes will be coming, including the ability to use images etc (such as with GPT Vision).
- **Text-to-Speech (TTS)**: The application can synthesize speech from the AI's responses, enabling a more natural and immersive experience.
- **Customizable Prompts**: PurposefulAI offers a variety of pre-defined prompts that can be selected to tailor the AI's behavior and personality for different use cases, such as coding assistance, research support, creative ideation, and more.
- **AI Model Selection**: Choose between OpenAI's GPT models (including GPT-3.5-turbo, GPT-4, and various versions) or Anthropic's Claude models to suit your needs and preferences.
- **Theme Switching**: Easily switch between light and dark themes to suit your visual preferences.
- **Settings Management**: Save and load your preferred settings, including the selected prompt, AI model, TTS engine, and API key, for a seamless experience across sessions.

# Instructions

## Easy Install:

1. Download and run "**Install Purposeful AI.bat**"
2. Once that is complete, run "**Launch Purposeful AI.bat**"

## Regular Install:


Clone the repository:

    git clone https://github.com/qpd-v/PurposefulAI.git


Navigate to the project directory:

    cd PurposefulAI


Install the required dependencies:

    pip install -r requirements.txt

# Usage

Run Purposeful AI by double-clicking: 

    Launch Purposeful AI.bat 

Or, from terminal/command line:

    python main.py
* * *
Obtain the necessary API keys from OpenAI or Anthropic, and keep them handy. Settings can be saved within the program once added.

    
For Anthropic/Claude:
    
        https://console.anthropic.com/settings/keys

For OpenAI/GPT: 
    
        https://platform.openai.com/api-keys




The PurposefulAI interface will open, allowing you to customize the settings and interact with the AI assistant.


Select the desired prompt, AI model, and input/output modes from the sidebar.


Enter your API key(s) in the designated field(s).


Start interacting with the AI assistant by typing or speaking your queries, depending on the mode.

The AI's responses will be displayed in the conversation window and, if enabled, synthesized as speech.

    Mode 1: "Voice Chat"
    -Enables voice chat mode. 
    -User can speak to the bot and receive a response.
    -Text will still be displayed in the conversation box.

    Mode 2: "Text Input, Voice Output"
    -Enables user to type a message and receive a voice response.
    
    Mode 3: "Text Only Chat"
    -No voice response, only text.


## Contributing

Contributions are welcome! If you encounter any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. 

If you use this code, please give credit to Purposeful AI.

## Acknowledgments

PurposefulAI utilizes the following libraries and services:

- [OpenAI GPT](https://openai.com/api/) for language model capabilities
- [Anthropic Claude](https://www.anthropic.com/) for conversational AI assistance
- [gTTS](https://github.com/pndurette/gTTS) for Google Text-to-Speech
- [pydub](https://github.com/jiaaro/pydub) for audio manipulation and playback
- [SpeechRecognition](https://github.com/Uberi/speech_recognition) for speech recognition
- [pyttsx3](https://github.com/nateshmbhat/pyttsx3) for Python Text-to-Speech
- [customtkinter](https://github.com/TomSchimansky/CustomTkinter) for the modern and customizable user interface

We express our deep gratitude to the developers and contributors of these projects for their valuable work
 and services.
