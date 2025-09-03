# BaconanaMTL Tool - Advanced Game Translation Suite

🚀 **Professional-grade automatic translation tool** for games and visual novels using cutting-edge AI technology. Supports **13+ game engines** with intelligent content detection, **7+ AI providers** with automatic fallback, and **advanced light novel processing** with content-aware filtering.

## ✨ Key Features

### 🤖 **Multi-Provider AI Engine**
- **Priority-based provider management** with automatic fallback
- **7+ AI Providers**: OpenAI, Anthropic, Gemini, xAI, DeepSeek, OpenRouter, Ollama
- **Cloud AI Integration**: HuggingFace Transformers, vLLM, Google Colab, Kaggle
- **Smart cost optimization** with provider switching and rate limit handling
- **Manual model selection** for HuggingFace with 1000+ models

### 🎮 **Universal Game Engine Support**
- **RPG Maker MV/MZ** - JSON game data with structure preservation
- **Ren'Py** - Visual novel scripts (.rpy) with markup handling
- **Unity** - Localization files (JSON, CSV, XML) with asset detection
- **Wolf RPG Editor** - Scripts and archives with binary extraction
- **KiriKiri** - Engine scripts (.ks) and archives (.xp3)
- **NScripter** - Game scripts (.nscript, .txt, .dat) with pattern matching
- **Live Maker** - Binary files (.lsb, .lsc, .lm) with encoding detection
- **TyranoBuilder** - TyranoScript processing with tag preservation
- **SRPG Studio** - Tactical RPG data (JSON, JS) with event extraction
- **Lune** - Binary formats (.l) with text extraction
- **Regex** - Custom pattern-based processing for any text format

### 📚 **Advanced Light Novel Processing**
- **Dedicated Light Novel tab** with specialized interface
- **Smart content detection**: Eroge/adult content classification
- **SFW/NSFW model filtering** - automatic model compatibility checking
- **Intelligent text chunking** with sentence boundary detection
- **Multiple output formats**: Text, EPUB, JSON with metadata preservation
- **Chapter-aware processing** with structure analysis
- **Cost estimation** with detailed token analysis

### � **Professional Features**
- **Provider Management System**: Configure multiple AI sources with priorities
- **Automatic failover**: Seamless switching when providers fail
- **Real-time monitoring**: Provider status, rate limits, and performance tracking
- **Customizable prompts** with content-aware templates
- **Term dictionaries** for translation consistency
- **Batch processing** with intelligent load balancing
- **Cost estimation** with detailed breakdown by provider and model
- **Project auto-detection** with engine-specific optimizations

## 📂 Supported Formats & Engines

### 🎮 **Game Engines** (Auto-Detection)

#### **RPG Maker MV/MZ**
- 📄 **Files**: JSON game data files (`Map001.json`, `CommonEvents.json`, etc.)
- 🔍 **Detection**: Automatic game structure recognition
- ⚙️ **Features**: Format preservation, system file filtering, batch processing

#### **Ren'Py** (Visual Novels)
- 📄 **Files**: `.rpy` script files with dialogues and menus
- 🔍 **Detection**: Ren'Py project structure and syntax
- ⚙️ **Features**: Markup handling, translation file creation, character preservation

#### **Unity** (Multi-platform Games)
- 📄 **Files**: JSON, CSV, XML localization files
- 🔍 **Detection**: Unity project assets and localization structure
- ⚙️ **Features**: Asset reference preservation, multiple format support

#### **Wolf RPG Editor**
- 📄 **Files**: `.txt` scripts, `.wolf` archive files
- 🔍 **Detection**: Wolf project structure and file patterns
- ⚙️ **Features**: Binary extraction, encoding detection, archive processing

#### **KiriKiri** (Visual Novel Engine)
- 📄 **Files**: `.ks` script files, `.xp3` archive files
- 🔍 **Detection**: KiriKiri syntax and command structure
- ⚙️ **Features**: Archive extraction, tag preservation, command parsing

#### **NScripter** (Visual Novel Engine)
- 📄 **Files**: `.nscript`, `.txt`, `.dat` files
- 🔍 **Detection**: NScripter command patterns and syntax
- ⚙️ **Features**: Pattern-based extraction, binary text processing

#### **Live Maker** (Adventure Game Engine)
- 📄 **Files**: `.lsb`, `.lsc`, `.lm` binary files
- 🔍 **Detection**: Live Maker binary signatures
- ⚙️ **Features**: Binary text extraction, encoding detection, project files

#### **TyranoBuilder** (Visual Novel Creator)
- 📄 **Files**: TyranoScript `.ks` files
- 🔍 **Detection**: TyranoScript syntax and structure
- ⚙️ **Features**: Tag preservation, dialogue extraction, formatting

#### **SRPG Studio** (Tactical RPG Maker)
- 📄 **Files**: JSON data files, JS script files
- 🔍 **Detection**: SRPG Studio project structure
- ⚙️ **Features**: Event extraction, tactical RPG data handling

#### **Lune** (Multi-purpose Engine)
- 📄 **Files**: `.l` files (binary and text formats)
- 🔍 **Detection**: Lune file signatures and structure
- ⚙️ **Features**: Binary text extraction, format detection

#### **Regex** (Custom Pattern Processing)
- 📄 **Files**: `.txt` files with custom patterns
- 🔍 **Detection**: User-defined regex patterns
- ⚙️ **Features**: Flexible pattern matching, custom extraction rules

## 🎯 Detailed Setup Guide

### 🔧 Provider Configuration (Recommended)

The **Provider Management System** offers enterprise-grade reliability with automatic failover:

#### Setting Up Multiple Providers

1. **Open Providers Tab**: Go to "🔄 Providers" 
2. **Add Primary Provider**: Click "➕ Add Provider"
   - **Name**: `OpenAI-Primary`
   - **Type**: OpenAI
   - **API Key**: Your OpenAI key
   - **Priority**: `1` (highest)
3. **Add Backup Provider**: Add another provider
   - **Name**: `Anthropic-Backup`
   - **Type**: Anthropic  
   - **API Key**: Your Claude key
   - **Priority**: `2` (fallback)
4. **Test All**: Click "🧪 Test All Providers"

#### Provider Priority Examples

```
Priority 1: OpenAI (GPT-4) - Primary for quality
Priority 2: Anthropic (Claude) - Backup for reliability  
Priority 3: DeepSeek - Cost-effective fallback
Priority 4: Ollama (Local) - Offline fallback
```

### 📚 Light Novel Translation

For visual novels, light novels, and books:

1. **Open Light Novel Tab**: Click "📚 Light Novel"
2. **Select File**: Choose your `.txt`, `.epub`, or text file
3. **Content Check**: Tool automatically detects adult content
4. **Model Filtering**: SFW/NSFW models filtered automatically
5. **Estimate Costs**: Get detailed cost breakdown
6. **Choose Format**: Text, EPUB, or JSON output
7. **Start Translation**: Monitor with real-time progress

#### Content Policy System
- **🟢 SFW Models**: GPT-4, Claude (strict filtering)
- **🟡 Mixed Models**: Gemini, DeepSeek (moderate filtering) 
- **🔴 NSFW-Friendly**: xAI Grok, OpenRouter, Ollama (relaxed filtering)

### 🌐 Game Translation  

For games and interactive content:

1. **Auto-Detection**: Tool recognizes engine automatically
2. **Select Project**: Choose game folder (contains data files)
3. **Output Directory**: Select where to save translations  
4. **Engine Settings**: Customize per detected engine
5. **Start Translation**: Batch processing with progress monitoring

### ☁️ Cloud AI Integration

Access advanced models and cloud platforms:

#### HuggingFace Integration
- **Browse Models**: 1000+ transformer models available
- **Manual Selection**: Enter model ID directly  
- **Custom Endpoints**: Use your own inference endpoints

#### Google Colab/Kaggle
- **Generate Setup**: Get pre-configured notebook code
- **GPU Acceleration**: Free GPU for faster translation
- **Large Models**: Run models too big for local hardware

### ⚙️ Legacy Configuration

For single-provider setup (backward compatibility):

#### OpenAI Setup
- **API URL**: Leave empty for official OpenAI
- **API Key**: Get from https://platform.openai.com/
- **Organization**: Optional organization ID
- **Model**: `gpt-4` (recommended) or `gpt-3.5-turbo`

#### Alternative Provider Setup  
- **API URL**: Provider endpoint (e.g., `http://localhost:5000/v1`)
- **API Key**: Provider-specific key or placeholder
- **Model**: Model name per provider documentation

### 🔧 Advanced Configuration

#### Custom Prompts
Adapt translation style for specific content:

```
For eroge content: Focus on emotional nuance and adult themes
For RPGs: Emphasize game terminology and character voices  
For technical content: Prioritize accuracy over style
```

#### Term Dictionaries
Maintain consistency across translations:

```
主人公 (protagonist)
魔王 (demon lord)  
勇者 (hero)
ギルド (guild)
```

#### Performance Tuning
- **File Threads**: Number of files processed simultaneously
- **Batch Size**: Lines translated per API call  
- **Rate Limits**: Delay between requests
- **Memory Usage**: Buffer size for large files

## 🛠️ Troubleshooting

### Provider Issues
- **No Providers Available**: Configure at least one provider in "🔄 Providers" tab
- **All Providers Failed**: Check API keys and internet connection
- **Rate Limiting**: Lower priority providers will automatically take over
- **API Quota Exceeded**: Provider fallback system will switch to alternatives

### Translation Quality
- **Poor Quality**: Use GPT-4 or Claude-3.5-sonnet for best results
- **Inconsistent Terms**: Add key terms to custom vocabulary
- **Wrong Style**: Customize prompts in "🔧 Advanced" tab
- **Adult Content Blocked**: Use xAI Grok, OpenRouter, or Ollama for NSFW content

### Performance Issues
- **Slow Translation**: Reduce file threads or use faster models
- **Memory Usage**: Lower batch size or close other applications
- **Connection Timeouts**: Increase timeout in provider settings
- **Large Files**: Use Light Novel tab for better chunking

### File Problems
- **Encoding Errors**: Tool automatically detects encoding - try different file
- **Access Denied**: Run as administrator or check file permissions
- **Corrupted Output**: Enable automatic backups in settings
- **Missing Translations**: Check logs for API errors or rate limits

## 🎯 Use Cases & Examples

### **📚 Visual Novel Translation**
Perfect for translating Japanese visual novels and eroge:
- **Content-aware processing** with eroge detection
- **NSFW model filtering** for appropriate AI selection  
- **Chapter-based organization** preserving story structure
- **Multiple output formats** for different reading preferences

**Example workflow:**
1. Load `.txt` visual novel file in Light Novel tab
2. Tool detects eroge content and suggests compatible models
3. Configure xAI Grok or Ollama for unrestricted translation
4. Export as EPUB for e-reader or text for further editing

### **🎮 Game Localization**
Streamline professional game localization:
- **Multi-engine support** for diverse game projects
- **Batch processing** for large translation volumes
- **Quality assurance** with term dictionaries and custom prompts
- **Provider redundancy** ensuring deadline reliability

**Example workflow:**
1. Point tool at RPG Maker game folder
2. Configure multiple providers (OpenAI primary, Claude backup)
3. Customize prompts for game-specific terminology
4. Start batch translation with automatic failover

### **🏢 Enterprise Translation**
Scale translation operations with professional features:
- **Provider load balancing** across multiple API accounts
- **Cost optimization** with tiered provider priorities
- **Monitoring and logging** for process transparency
- **Failure recovery** with automatic retry mechanisms

## 📊 Performance & Reliability

### **🔄 Provider Management Benefits**
- **99.9% Uptime**: Automatic failover ensures continuous operation
- **Cost Optimization**: Route to cheaper providers when quality permits
- **Rate Limit Handling**: Intelligent backoff prevents API blocking
- **Load Distribution**: Balance requests across multiple accounts

### **⚡ Translation Speed**
- **Parallel Processing**: Multiple files and API calls simultaneously
- **Smart Chunking**: Optimal batch sizes for each provider
- **Local Caching**: Avoid re-translating unchanged content
- **Progress Monitoring**: Real-time updates with detailed logging

### **🛡️ Data Safety**
- **Automatic Backups**: Original files preserved with `.backup` extension
- **Format Validation**: JSON structure verification after translation
- **Encoding Detection**: Automatic handling of various text encodings
- **Error Recovery**: Graceful handling of translation failures

## 🌟 Advanced Features

### **🤖 AI Model Selection**
- **Quality Tiers**: GPT-4 > Claude-3.5 > Gemini > GPT-3.5 > Local models
- **Content Compatibility**: SFW vs NSFW model classification
- **Cost Optimization**: Balance quality vs expense based on content
- **Performance Scaling**: From laptop-local to datacenter-cloud

### **📝 Content Processing**
- **Intelligent Chunking**: Sentence-boundary aware text segmentation
- **Context Preservation**: Maintain narrative flow across chunks
- **Format Detection**: Automatic recognition of dialogue, narration, UI text
- **Encoding Handling**: Support for Japanese, Chinese, Korean text encodings

### **🔧 Customization**
- **Prompt Engineering**: Fine-tune translation style and approach
- **Term Dictionaries**: Ensure consistency across large projects
- **File Filtering**: Include/exclude specific files or patterns
- **Output Formatting**: Customize translated file structure and naming

## 📈 What's New in v2.0

### 🚀 **Major Features**
- ✨ **Provider Management System**: Multi-provider setup with automatic failover
- ✨ **Light Novel Specialization**: Dedicated interface for visual novels
- ✨ **Cloud AI Integration**: HuggingFace, Colab, Kaggle support
- ✨ **Content Policy System**: SFW/NSFW model compatibility checking
- ✨ **Smart Text Chunking**: Sentence-aware processing for better context

### 🛠️ **Improvements**
- 🔧 Enhanced error handling and recovery
- 🔧 Real-time provider monitoring and status
- 🔧 Improved cost estimation with detailed breakdowns
- 🔧 Better file format detection and processing
- 🔧 Streamlined UI with tabbed organization

### 🐛 **Bug Fixes**
- 🔧 Fixed encoding issues with non-ASCII text
- 🔧 Resolved memory leaks in large file processing
- 🔧 Improved stability with unstable network connections
- 🔧 Better handling of rate limits and API errors

## 🤝 Community & Support

### **📚 Documentation**
- **Built-in Help**: Comprehensive documentation tab in application
- **README Guide**: Detailed setup and usage instructions
- **API Reference**: Technical documentation for developers
- **Video Tutorials**: Coming soon on YouTube

### **💬 Community**
- **GitHub Issues**: Bug reports and feature requests
- **Discord Server**: Real-time community support (coming soon)
- **Reddit Community**: r/TranslationTools discussions
- **Twitter Updates**: @BaconanaMTL for news and updates

### **🔧 Professional Support**
- **Enterprise Consulting**: Custom integration and setup
- **Priority Support**: Dedicated technical assistance
- **Custom Development**: Bespoke features for specific needs
- **Training Services**: Team onboarding and best practices

## 📄 License & Legal

**MIT License** - Open source with commercial use permitted.

### **Important Notes**
- 🔒 **Respect Copyrights**: Only translate content you own or have permission for
- 🔒 **API Compliance**: Follow AI provider terms of service
- 🔒 **Content Policies**: Some providers restrict adult or sensitive content
- 🔒 **Data Privacy**: Translation data is sent to AI providers - review their privacy policies

### **Disclaimer**
This tool is for personal and educational use. Users are responsible for:
- Compliance with copyright laws
- Adherence to AI provider terms of service  
- Respect for content creator rights
- Appropriate use of translated content

---

## 🙏 Acknowledgments

### **Special Thanks**
🎯 **[DazedAnon](https://gitgud.io/DazedAnon/DazedMTLTool)** - Original inspiration and concept  
🤖 **AI Provider Teams** - OpenAI, Anthropic, Google, xAI, DeepSeek for API access  
🎮 **Game Engine Developers** - For creating the engines we support  
👥 **Translation Community** - Beta testing and feedback  
🔧 **Open Source Contributors** - Code improvements and bug reports  

### **Technology Stack**
- **Python 3.8+** with PyQt5 for GUI
- **Requests** for HTTP API communication  
- **TikToken** for accurate token counting
- **Chardet** for encoding detection
- **JSON/XML/CSV** parsers for various game formats

---

<div align="center">

**🌟 Star this project if it helped you! 🌟**

**Made with ❤️ by the Baconana team**

*Translating games, one neural network at a time* 🤖🎮

</div>
