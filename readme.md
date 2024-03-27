# PurposefulAI

PurposefulAI is a versatile AI assistant application that leverages the power of OpenAI's GPT and Anthropic's Claude models (more to come!) to provide a wide range of functionalities. It has voice chat functionality and with its user-friendly interface and customizable settings, PurposefulAI aims to be your go-to companion for various tasks and queries.

## Features

- **Multi-Modal Input**: PurposefulAI supports text input, voice input, and a combination of both, allowing you to interact with the AI assistant in a way that suits your preferences. More modes will be coming, including the ability to use images etc (such as with GPT Vision).
- **Text-to-Speech (TTS)**: The application can synthesize speech from the AI's responses, enabling a more natural and immersive experience.
- **Customizable Prompts**: PurposefulAI offers a variety of pre-defined prompts that can be selected to tailor the AI's behavior and personality for different use cases, such as coding assistance, research support, creative ideation, and more.
- **AI Model Selection**: Choose between OpenAI's GPT models (including GPT-3.5-turbo, GPT-4, and various versions) or Anthropic's Claude models to suit your needs and preferences.
- **Theme Switching**: Easily switch between light and dark themes to suit your visual preferences.
- **Settings Management**: Save and load your preferred settings, including the selected prompt, AI model, TTS engine, and API key, for a seamless experience across sessions.

## Installation

1. Clone the repository:

git clone https://github.com/your-repo/PurposefulAI.git


2. Navigate to the project directory:

cd PurposefulAI


3. Install the required dependencies:

pip install -r requirements.txt


4. Obtain the necessary API keys from OpenAI and Anthropic, and keep them handy.

For Anthropic/Claude: https://console.anthropic.com/settings/keys

For OpenAI/GPT: https://platform.openai.com/api-keys
## Usage

1. Run the application:

python main.py


2. The PurposefulAI interface will open, allowing you to customize the settings and interact with the AI assistant.
3. Select the desired prompt, AI model, and input/output modes from the sidebar.
4. Enter your API key(s) in the designated field(s).
5. Start interacting with the AI assistant by typing or speaking your queries.
6. The AI's responses will be displayed in the conversation window and, if enabled, synthesized as speech.

## Contributing

Contributions are welcome! If you encounter any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

PurposefulAI utilizes the following libraries and services:

- [OpenAI GPT](https://openai.com/api/) for language model capabilities
- [Anthropic Claude](https://www.anthropic.com/) for conversational AI assistance
- [gTTS](https://github.com/pndurette/gTTS) for Google Text-to-Speech
- [pydub](https://github.com/jiaaro/pydub) for audio manipulation and playback
- [SpeechRecognition](https://github.com/Uberi/speech_recognition) for speech recognition
- [pyttsx3](https://github.com/nateshmbhat/pyttsx3) for Python Text-to-Speech
- [customtkinter](https://github.com/TomSchimansky/CustomTkinter) for the modern and customizable user interface

We express our gratitude to the developers and contributors of these projects for their valuable work.

This README provides an overview of the PurposefulAI application, its features, installation instructions, usage guidelines, and acknowledgments for the libraries and services used. It also invites contributions from the community and mentions the project's license.