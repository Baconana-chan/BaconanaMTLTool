# Game Translation Tool

Automatic tool for translating games from Japanese to other languages using AI. Supports games on RPG Maker MV/MZ, Ren'Py, Unity, Wolf RPG Editor, KiriKiri, NScripter, Live Maker, TyranoBuilder, SRPG Studio, Lune, and Regex engines.

## Features

- 🌐 **Automatic translation** using multiple AI providers (OpenAI, Anthropic, Gemini, xAI, DeepSeek, OpenRouter, Ollama)
- 🎮 **Support for multiple game engines**:
  - **RPG Maker MV/MZ** - working with game JSON files
  - **Ren'Py** - processing .rpy scripts
  - **Unity** - localization files (JSON, CSV, XML)
  - **Wolf RPG Editor** - processing .txt and .wolf archive files
  - **KiriKiri** - handling .ks scripts and .xp3 archives
  - **NScripter** - processing .nscript, .txt, and .dat files
  - **Live Maker** - working with .lsb, .lsc, and .lm files
  - **TyranoBuilder** - processing TyranoScript .ks files
  - **SRPG Studio** - handling JSON and JS files for tactical RPGs
  - **Lune** - processing .l files (binary and text)
  - **Regex** - handling .txt files with pattern-based extraction
- 🖥️ **Convenient GUI interface** - easy to use even for beginners
- 📝 **Customizable prompts** - ability to change translation style
- 📚 **Term dictionary** - consistency of translations
- 💰 **Project cost estimation** - control of API expenses
- 🔄 **Batch processing** - efficient processing of large volumes of text
- 🌍 **Support for multiple languages** - translation to English, Russian, Spanish, French, and others
- 💾 **Automatic folder creation** - safety of your files

## Supported Formats

### RPG Maker MV/MZ
- JSON files with game data
- Automatic detection of game structure
- Preservation of original format

### Ren'Py
- .rpy scripts with dialogues and menus
- Processing of Ren'Py markup
- Creation of translation files

### Unity
- JSON localization files
- CSV translation tables
- XML localization files
- Text files with Japanese content

### Wolf RPG Editor
- .txt files with game scripts
- .wolf archive files (automatic extraction)
- Text extraction from binary formats

### KiriKiri
- .ks script files with dialogue and commands
- .xp3 archive files (automatic extraction)
- Processing of KiriKiri markup and tags

### NScripter
- .nscript files with game logic
- .txt files with dialogue
- .dat binary files with text data
- Pattern-based text extraction

### Live Maker
- .lsb binary files with dialogue
- .lsc script files
- .lm project files
- Binary text extraction with encoding detection

### TyranoBuilder
- .ks files with TyranoScript
- Processing of TyranoScript tags and commands
- Dialogue and menu extraction
- Formatting preservation

### SRPG Studio
- JSON files with game data
- JS files with scripts
- Tactical RPG data processing
- Event and dialogue extraction

### Lune
- .l files (binary and text formats)
- Text extraction with encoding detection

### Regex
- .txt files with simple text-based scripts
- Pattern-based dialogue extraction

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python main.py
# or use start.bat on Windows
```

## Installation

### Requirements
- Python 3.8+
- API key from one of the supported AI providers

### Supported AI Providers
- **OpenAI** (GPT-3.5, GPT-4, GPT-4o)
- **Anthropic** (Claude 3, Claude 3.5)
- **Google Gemini** (Gemini Pro, Gemini Flash)
- **xAI** (Grok)
- **DeepSeek** (DeepSeek Chat, DeepSeek Coder)
- **OpenRouter** (access to multiple models)
- **Ollama** (local models)

### Installation Steps

1. **Download or clone the project**

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python main.py
```

## Quick Start

### 1. API Setup

1. Open the **"⚙️ Configuration"** tab
2. Enter your **API Key** from OpenAI
3. Select the **model** (gpt-4 recommended for best quality)
4. Click **"🔍 Test API Connection"** to verify

### 2. File Selection

1. Go to the **"🌐 Translation"** tab
2. Select the **game folder** (where JSON files are located)
3. Select the **save folder** for translated files
4. Configure translation options as desired

### 3. Start Translation

1. Click **"🚀 Start Translation"**
2. Monitor progress in real time
3. Check logs on the **"📋 Log"** tab

## Detailed Guide

### API Configuration

#### OpenAI API
- **API URL**: Leave empty for official OpenAI API
- **API Key**: Your OpenAI key (get at https://platform.openai.com/)
- **Organization**: Organization ID (optional)
- **Model**: Recommended `gpt-4` or `gpt-3.5-turbo`

#### Alternative APIs
For using other APIs (e.g., text-generation-webui):
- **API URL**: Specify your API URL (e.g., `http://localhost:5000/v1`)
- **API Key**: Any text (for compatibility)
- **Model**: Model name according to API documentation

### Translation Settings

- **Target Language**: Translation language (default English)
- **Timeout**: API response wait time (30-300 seconds)
- **File Threads**: Number of files for simultaneous processing
- **Threads per File**: Threads per file (recommended 1 for free APIs)
- **Batch Size**: Batch size for translation (1-50 lines)

### Text Formatting

- **Dialogue Width**: Dialogue width (characters)
- **List Width**: List width
- **Note Width**: Note width

### API Cost

- **Input Cost**: Cost of input tokens (per 1K)
- **Output Cost**: Cost of output tokens (per 1K)
- **Frequency Penalty**: Penalty for repetitions (0.0-2.0)

### Advanced Settings

#### Custom Prompts
You can change the translation prompt:
1. Go to the **"🔧 Advanced"** tab
2. Edit the prompt in the **"📝 Custom Translation Prompt"** section
3. Save changes

#### Term Dictionary
For translation consistency:
1. Add terms to the **"📚 Custom Vocabulary"** section
2. Use format: `japanese_term (english_translation)`

#### File Filters
- **Include Patterns**: File patterns to include (e.g., `*.json`)
- **Exclude Patterns**: Patterns to exclude (e.g., `System.json`)

## Supported File Types

### RPG Maker MV/MZ
- **Map files**: `Map001.json`, `Map002.json`, etc.
- **CommonEvents**: `CommonEvents.json`
- **Troops**: `Troops.json`
- **System exclusions**: Automatically skips system files

### Automatic Detection
The tool automatically:
- Finds JSON files in the specified folder
- Identifies files with Japanese text
- Skips system files without translatable content

## Security

### Automatic Backups
- Creates copies of original files with `.backup` extension
- Can be disabled in translation settings

### Integrity Check
- JSON structure validation after translation
- Preservation of formatting and special characters

## Troubleshooting

### API Errors
- **Check API key**: Ensure the key is correct
- **Rate limits**: Reduce number of threads
- **Timeouts**: Increase wait time

### File Issues
- **Encoding**: Tool automatically detects encoding
- **Access rights**: Ensure read/write permissions
- **Disk space**: Check available space

### Translation Quality
- **Use GPT-4**: Best translation quality
- **Customize prompt**: Adapt to your content
- **Add terms**: Use dictionary for consistency

## Usage Examples

### Basic Scenario
1. Unpack RPG Maker game
2. Find `data` folder with JSON files
3. Specify this folder as source
4. Create folder for translated files
5. Start translation

### Batch Processing
For processing multiple games:
1. Create script with settings
2. Use API client directly
3. Automate the process

## API Reference

### Main Classes

#### `ConfigManager`
Application configuration management
```python
config = ConfigManager()
config.set_value('api_key', 'your-key')
config.save_config()
```

#### `APIClient`
Client for working with translation APIs
```python
client = APIClient(config)
result = client.translate_batch({'text': 'こんにちは'})
```

#### `FileProcessor`
JSON file processing
```python
processor = FileProcessor()
texts = processor.extract_translatable_text(data)
```

#### `TranslationManager`
Translation process management
```python
manager = TranslationManager(config, input_dir, output_dir)
manager.start()
```

## License

MIT License - see LICENSE file for details.

---

## 📊 Project Capabilities

✅ **Game engine support**: RPG Maker MV/MZ, Ren'Py, Unity, Wolf RPG Editor, KiriKiri, NScripter, Live Maker, TyranoBuilder, SRPG Studio, Lune, Regex  
✅ **Multiple AI providers**: OpenAI, Anthropic, Gemini, xAI, DeepSeek, OpenRouter, Ollama  
✅ **Intelligent project detection**: Automatic game type recognition  
✅ **Cost estimation**: Expense calculation before starting translation  
✅ **Batch processing**: Efficient work with large volumes  
✅ **Customizable prompts**: Control of quality and translation style  
✅ **Multilingual**: Support for multiple target languages  
✅ **GUI interface**: Ease of use for all users  

## 🎯 Perfect for:

- 🎮 **Game developers** - localizing their projects across multiple engines
- 🌍 **Translators** - automating routine tasks for various game formats
- 👥 **Mod communities** - creating fan translations for popular and niche games
- 🔧 **Technical specialists** - integration into workflows for different game engines
- 📚 **Visual novel enthusiasts** - translating games from RPG Maker, Ren'Py, and other engines
- ⚔️ **Tactical RPG fans** - working with SRPG Studio and similar engines

## Support

If you have questions or issues:
1. Check the "Troubleshooting" section
2. Review logs on the Log tab
3. Create an issue in the GitHub repository

## Acknowledgments

🙏 **Special thanks to [DazedAnon](https://gitgud.io/DazedAnon/DazedMTLTool)** for:
- Idea of automatic game translation with AI
- Basic prompts and dictionaries for quality translation
- Inspiration for creating this tool

Also thanks to:
- All AI providers for API access
- Visual novel translation community
- Game engine developers
- Open source community

---

**Note**: This tool is intended for personal use. Respect copyrights and game licenses.
