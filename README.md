# ai-powered-video-translation-app

This application allows you to perform video translation using artificial intelligence technologies. It transcribes uploaded videos and translates them into selected languages using OpenAI's Whisper model and GPT-4.

## Features

- Video upload and audio conversion
- Automatic transcription (OpenAI Whisper)
- Translation with multi-language support (GPT-4)
- User-friendly Streamlit interface
- Option to download translation results

## Requirements

- Python 3.8+
- FFmpeg
- OpenAI API key

## Installation

1. Clone the repository:
git clone https://github.com/yourusername/ai-powered-video-translation-app.git
cd ai-powered-video-translation-app
Copy
2. Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
Copy
3. Install the required libraries:
pip install -r requirements.txt
Copy
4. Create a `.env` file and add your OpenAI API key:
OPENAI_API_KEY=your_api_key_here
Copy
5. Install FFmpeg (if not already on your system):
- Windows: https://ffmpeg.org/download.html
- macOS: `brew install ffmpeg`
- Linux: `sudo apt-get install ffmpeg`

## Usage

1. Run the application:
streamlit run app.py
Copy
2. In the web application that opens in your browser:
- Select the languages you want to translate to
- Upload a video file
- Wait for the process to complete
- View and optionally download the results

## Contributing

If you'd like to contribute to our project, please open a Pull Request. For major changes, please open an issue first to discuss the proposed change.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

Zülal Beyza Yaylı - [GitHub](https://github.com/yourusername)

Project Link: [https://github.com/yourusername/ai-powered-video-translation-app](https://github.com/yourusername/ai-powered-video-translation-app)
