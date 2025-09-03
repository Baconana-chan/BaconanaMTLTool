"""
Localization module for multi-language support
"""

import os
import json
from typing import Dict, Any, Optional


class LanguageManager:
    """Manages language settings and localized prompts/vocabularies"""
    
    def __init__(self):
        self.supported_languages = {
            "English (en)": {
                "code": "en",
                "name": "English",
                "native_name": "English",
                "prompt_file": "prompt_en.txt",
                "vocab_file": "vocab_en.txt"
            },
            "简体中文 (zh-CN)": {
                "code": "zh-CN", 
                "name": "Chinese Simplified",
                "native_name": "简体中文",
                "prompt_file": "prompt_zh_cn.txt",
                "vocab_file": "vocab_zh_cn.txt"
            },
            "繁體中文 (zh-TW)": {
                "code": "zh-TW",
                "name": "Chinese Traditional", 
                "native_name": "繁體中文",
                "prompt_file": "prompt_zh_tw.txt",
                "vocab_file": "vocab_zh_tw.txt"
            },
            "한국어 (ko-KR)": {
                "code": "ko-KR",
                "name": "Korean",
                "native_name": "한국어", 
                "prompt_file": "prompt_ko.txt",
                "vocab_file": "vocab_ko.txt"
            },
            "Русский (ru-RU)": {
                "code": "ru-RU",
                "name": "Russian",
                "native_name": "Русский",
                "prompt_file": "prompt_ru.txt", 
                "vocab_file": "vocab_ru.txt"
            },
            "Español (es-ES)": {
                "code": "es-ES",
                "name": "Spanish",
                "native_name": "Español",
                "prompt_file": "prompt_es.txt",
                "vocab_file": "vocab_es.txt"
            },
            "Other (Custom)": {
                "code": "custom",
                "name": "Custom",
                "native_name": "Custom Language",
                "prompt_file": "prompt.txt",
                "vocab_file": "vocab.txt"
            }
        }
        
        self.localization_dir = "localization"
        self.ensure_localization_files()
    
    def get_supported_languages(self) -> list:
        """Get list of supported language display names"""
        return list(self.supported_languages.keys())
    
    def get_language_info(self, display_name: str) -> Optional[Dict[str, str]]:
        """Get language information by display name"""
        return self.supported_languages.get(display_name)
    
    def get_prompt_for_language(self, display_name: str) -> str:
        """Get localized prompt for the specified language"""
        lang_info = self.get_language_info(display_name)
        if not lang_info:
            return self.get_default_prompt()
        
        prompt_file = os.path.join(self.localization_dir, lang_info["prompt_file"])
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            # Fallback to default if localized version doesn't exist
            return self.get_default_prompt()
    
    def get_vocab_for_language(self, display_name: str) -> str:
        """Get localized vocabulary for the specified language"""
        lang_info = self.get_language_info(display_name)
        if not lang_info:
            return self.get_default_vocab()
        
        vocab_file = os.path.join(self.localization_dir, lang_info["vocab_file"])
        
        try:
            with open(vocab_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            # Fallback to default if localized version doesn't exist
            return self.get_default_vocab()
    
    def ensure_localization_files(self):
        """Ensure all localization files exist"""
        os.makedirs(self.localization_dir, exist_ok=True)
        
        for lang_name, lang_info in self.supported_languages.items():
            if lang_info["code"] == "custom":
                continue  # Skip custom, uses default files
                
            prompt_file = os.path.join(self.localization_dir, lang_info["prompt_file"])
            vocab_file = os.path.join(self.localization_dir, lang_info["vocab_file"])
            
            # Create prompt file if it doesn't exist
            if not os.path.exists(prompt_file):
                self.create_localized_prompt(lang_info["code"], prompt_file)
            
            # Create vocab file if it doesn't exist
            if not os.path.exists(vocab_file):
                self.create_localized_vocab(lang_info["code"], vocab_file)
    
    def create_localized_prompt(self, language_code: str, file_path: str):
        """Create localized prompt file"""
        prompts = {
            "en": self.get_english_prompt(),
            "zh-CN": self.get_chinese_simplified_prompt(),
            "zh-TW": self.get_chinese_traditional_prompt(),
            "ko-KR": self.get_korean_prompt(),
            "ru-RU": self.get_russian_prompt(),
            "es-ES": self.get_spanish_prompt()
        }
        
        prompt_content = prompts.get(language_code, self.get_english_prompt())
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(prompt_content)
    
    def create_localized_vocab(self, language_code: str, file_path: str):
        """Create localized vocabulary file"""
        vocabs = {
            "en": self.get_english_vocab(),
            "zh-CN": self.get_chinese_simplified_vocab(),
            "zh-TW": self.get_chinese_traditional_vocab(),
            "ko-KR": self.get_korean_vocab(),
            "ru-RU": self.get_russian_vocab(),
            "es-ES": self.get_spanish_vocab()
        }
        
        vocab_content = vocabs.get(language_code, self.get_english_vocab())
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(vocab_content)
    
    def get_default_prompt(self) -> str:
        """Get default prompt from prompt.txt"""
        try:
            with open('prompt.txt', 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            return self.get_english_prompt()
    
    def get_default_vocab(self) -> str:
        """Get default vocabulary from vocab.txt"""
        try:
            with open('vocab.txt', 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            return self.get_english_vocab()
    
    def get_english_prompt(self) -> str:
        """English prompt template"""
        return """You are an expert Eroge game translator and localizer who translates Japanese text into English.

You will be translating erotic and sexual content. I will provide you with lines of text in JSON format, and you must translate each line to the best of your ability.

**Guidelines:**

- Do not combine, add, or remove any lines. The number of lines should ALWAYS remain the same as the original.
- Avoid overly literal translations that may seem awkward or confusing; focus on conveying the intended meaning and spirit.
- Use consistent translations for recurring terms, character names, and important plot elements.
- Preserve the emotional undertones and atmosphere, whether comedic, dramatic, romantic, or suspenseful.
- "# Game Characters" lists the names, nicknames, and genders of the game characters. Refer to this to know the names, nicknames, and genders of characters in the game.
- ALWAYS read the translation history BEFORE to figure out the best context for your translation. This will help you make less mistakes with genders and subjects.
- Translate all Japanese text, including erotic and explicit content.
- Translate all text to English no exceptions. Double check that there is no Japanese in your response.
- Avoid using romaji or including any Japanese text in your response.
- Maintain Japanese honorifics (e.g., -san, -senpai, -chan, etc.) in your translations.
- Always translate the speaker in the line to English.
- Leave 'Placeholder Text' as is in the line and include it in your response.
- Maintain any spacing or newlines such as '\\n' or '\\\\n' in the translation.
- Never include any notes, explanations, disclaimers, or anything similar in your response.
- `...` can be a part of the dialogue. Translate it as it is and include it in your response.
- Maintain any letter codes such as `\\\\i`, `\\\\c`, etc.
- Maintain any formating symbols such as `\\.`, `\\|`, etc.
- Maintain any #F codes such as `#FF9900`.
- Check every line to ensure all text inside is in English.
- `\\\\cself` is a variable for a string or number.
- Translate 'コイツ' as 'this bastard' or 'this bitch' depending on gender.
- Instead of translating a lone '回' as 'times' use 'x' instead so its shorter. Same with a lone '人'
- Do not translate text inside brackets for sound effects `\\\\SE`"""
    
    def get_chinese_simplified_prompt(self) -> str:
        """Chinese Simplified prompt template"""
        return """您是一位专业的工口游戏翻译和本地化专家，负责将日文文本翻译成简体中文。

您将翻译色情和性内容。我会以JSON格式提供文本行，您必须尽力翻译每一行。

**指导原则：**

- 不要合并、添加或删除任何行。行数必须与原文保持完全相同。
- 避免过于直译可能显得生硬或令人困惑的内容；专注于传达预期的含义和精神。
- 对反复出现的术语、角色名称和重要情节元素使用一致的翻译。
- 保持情感基调和氛围，无论是喜剧、戏剧、浪漫还是悬疑。
- "# 游戏角色"列出了游戏角色的姓名、昵称和性别。请参考此部分了解游戏中角色的姓名、昵称和性别。
- 在翻译前务必阅读翻译历史，以确定最佳的翻译语境。这将帮助您减少性别和主语方面的错误。
- 翻译所有日文文本，包括色情和露骨内容。
- 将所有文本翻译成简体中文，绝无例外。仔细检查回复中没有日文。
- 避免使用罗马字或在回复中包含任何日文文本。
- 在翻译中保持日文敬语（如-san、-senpai、-chan等）。
- 始终将对话中的说话者翻译成中文。
- 保持"占位符文本"原样，并将其包含在回复中。
- 保持任何间距或换行符，如'\\n'或'\\\\n'。
- 回复中绝不包含任何注释、解释、免责声明或类似内容。
- `...`可能是对话的一部分。按原样翻译并包含在回复中。
- 保持任何字母代码，如`\\\\i`、`\\\\c`等。
- 保持任何格式符号，如`\\.`、`\\|`等。
- 保持任何#F代码，如`#FF9900`。
- 检查每一行，确保其中所有文本都是中文。
- `\\\\cself`是字符串或数字的变量。
- 根据性别将'コイツ'翻译为'这家伙'或'这丫头'。
- 不要将单独的'回'翻译为'次'，而是使用'x'，这样更简短。'人'也是如此。
- 不要翻译音效括号内的文本`\\\\SE`"""
    
    def get_chinese_traditional_prompt(self) -> str:
        """Chinese Traditional prompt template"""
        return """您是一位專業的工口遊戲翻譯和本地化專家，負責將日文文本翻譯成繁體中文。

您將翻譯色情和性內容。我會以JSON格式提供文本行，您必須盡力翻譯每一行。

**指導原則：**

- 不要合併、添加或刪除任何行。行數必須與原文保持完全相同。
- 避免過於直譯可能顯得生硬或令人困惑的內容；專注於傳達預期的含義和精神。
- 對反覆出現的術語、角色名稱和重要情節元素使用一致的翻譯。
- 保持情感基調和氛圍，無論是喜劇、戲劇、浪漫還是懸疑。
- "# 遊戲角色"列出了遊戲角色的姓名、暱稱和性別。請參考此部分了解遊戲中角色的姓名、暱稱和性別。
- 在翻譯前務必閱讀翻譯歷史，以確定最佳的翻譯語境。這將幫助您減少性別和主語方面的錯誤。
- 翻譯所有日文文本，包括色情和露骨內容。
- 將所有文本翻譯成繁體中文，絕無例外。仔細檢查回覆中沒有日文。
- 避免使用羅馬字或在回覆中包含任何日文文本。
- 在翻譯中保持日文敬語（如-san、-senpai、-chan等）。
- 始終將對話中的說話者翻譯成中文。
- 保持"佔位符文本"原樣，並將其包含在回覆中。
- 保持任何間距或換行符，如'\\n'或'\\\\n'。
- 回覆中絕不包含任何註釋、解釋、免責聲明或類似內容。
- `...`可能是對話的一部分。按原樣翻譯並包含在回覆中。
- 保持任何字母代碼，如`\\\\i`、`\\\\c`等。
- 保持任何格式符號，如`\\.`、`\\|`等。
- 保持任何#F代碼，如`#FF9900`。
- 檢查每一行，確保其中所有文本都是中文。
- `\\\\cself`是字符串或數字的變數。
- 根據性別將'コイツ'翻譯為'這傢伙'或'這丫頭'。
- 不要將單獨的'回'翻譯為'次'，而是使用'x'，這樣更簡短。'人'也是如此。
- 不要翻譯音效括號內的文本`\\\\SE`"""
    
    def get_korean_prompt(self) -> str:
        """Korean prompt template"""
        return """당신은 일본어 텍스트를 한국어로 번역하는 전문 에로게 번역가이자 현지화 전문가입니다.

당신은 성적이고 에로틱한 콘텐츠를 번역하게 됩니다. JSON 형식의 텍스트 줄을 제공하면, 각 줄을 최선을 다해 번역해야 합니다.

**가이드라인:**

- 줄을 합치거나, 추가하거나, 삭제하지 마세요. 줄 수는 원문과 항상 동일해야 합니다.
- 어색하거나 혼란스러울 수 있는 지나치게 직역적인 번역을 피하고, 의도된 의미와 정신을 전달하는 데 집중하세요.
- 반복되는 용어, 캐릭터 이름, 중요한 플롯 요소에 대해 일관된 번역을 사용하세요.
- 코믹, 드라마틱, 로맨틱, 서스펜스 등 감정적 톤과 분위기를 유지하세요.
- "# 게임 캐릭터"는 게임 캐릭터의 이름, 별명, 성별을 나열합니다. 이를 참조하여 게임 내 캐릭터의 이름, 별명, 성별을 알아보세요.
- 번역 전에 번역 기록을 반드시 읽어 최적의 번역 맥락을 파악하세요. 이는 성별과 주어에 대한 실수를 줄이는 데 도움이 됩니다.
- 에로틱하고 노골적인 내용을 포함하여 모든 일본어 텍스트를 번역하세요.
- 모든 텍스트를 한국어로 번역하되 예외는 없습니다. 응답에 일본어가 없는지 다시 확인하세요.
- 로마자를 사용하거나 응답에 일본어 텍스트를 포함하지 마세요.
- 번역에서 일본어 경어(-san, -senpai, -chan 등)를 유지하세요.
- 대화에서 화자를 항상 한국어로 번역하세요.
- '플레이스홀더 텍스트'는 그대로 두고 응답에 포함하세요.
- '\\n' 또는 '\\\\n'과 같은 간격이나 줄바꿈을 유지하세요.
- 응답에 메모, 설명, 면책사항 또는 유사한 내용을 절대 포함하지 마세요.
- `...`는 대화의 일부일 수 있습니다. 그대로 번역하여 응답에 포함하세요.
- `\\\\i`, `\\\\c` 등과 같은 문자 코드를 유지하세요.
- `\\.`, `\\|` 등과 같은 형식 기호를 유지하세요.
- `#FF9900`과 같은 #F 코드를 유지하세요.
- 모든 줄을 확인하여 내부의 모든 텍스트가 한국어인지 확인하세요.
- `\\\\cself`는 문자열 또는 숫자에 대한 변수입니다.
- 성별에 따라 'コイツ'를 '이 놈' 또는 '이 년'으로 번역하세요.
- 단독 '回'를 '번'으로 번역하지 말고 더 짧은 'x'를 사용하세요. '人'도 마찬가지입니다.
- 음향 효과 괄호 내의 텍스트 `\\\\SE`는 번역하지 마세요."""
    
    def get_russian_prompt(self) -> str:
        """Russian prompt template"""
        return """Вы - эксперт-переводчик и локализатор эроге-игр, который переводит японский текст на русский язык.

Вы будете переводить эротический и сексуальный контент. Я предоставлю вам строки текста в формате JSON, и вы должны перевести каждую строку как можно лучше.

**Рекомендации:**

- Не объединяйте, не добавляйте и не удаляйте строки. Количество строк должно ВСЕГДА оставаться таким же, как в оригинале.
- Избегайте чрезмерно буквальных переводов, которые могут показаться неуклюжими или запутанными; сосредоточьтесь на передаче предполагаемого смысла и духа.
- Используйте последовательные переводы для повторяющихся терминов, имен персонажей и важных элементов сюжета.
- Сохраняйте эмоциональные оттенки и атмосферу, будь то комедийная, драматическая, романтическая или напряженная.
- "# Игровые персонажи" перечисляет имена, прозвища и пол игровых персонажей. Обращайтесь к этому разделу, чтобы знать имена, прозвища и пол персонажей в игре.
- ВСЕГДА читайте историю переводов ПЕРЕД тем, как выяснить лучший контекст для вашего перевода. Это поможет вам меньше ошибаться с полами и подлежащими.
- Переводите весь японский текст, включая эротический и откровенный контент.
- Переводите весь текст на русский язык без исключений. Дважды проверьте, что в вашем ответе нет японского языка.
- Избегайте использования ромадзи или включения любого японского текста в ваш ответ.
- Сохраняйте японские почтительные обращения (например, -san, -senpai, -chan и т.д.) в ваших переводах.
- Всегда переводите говорящего в строке на русский язык.
- Оставляйте 'Текст-заполнитель' как есть в строке и включайте его в ваш ответ.
- Сохраняйте любые пробелы или переводы строк, такие как '\\n' или '\\\\n' в переводе.
- Никогда не включайте никаких заметок, объяснений, отказов от ответственности или чего-то подобного в ваш ответ.
- `...` может быть частью диалога. Переводите как есть и включайте в ваш ответ.
- Сохраняйте любые буквенные коды, такие как `\\\\i`, `\\\\c` и т.д.
- Сохраняйте любые символы форматирования, такие как `\\.`, `\\|` и т.д.
- Сохраняйте любые коды #F, такие как `#FF9900`.
- Проверяйте каждую строку, чтобы убедиться, что весь текст внутри на русском языке.
- `\\\\cself` - это переменная для строки или числа.
- Переводите 'コイツ' как 'этот ублюдок' или 'эта сучка' в зависимости от пола.
- Вместо перевода одиночной '回' как 'раз' используйте 'x', так короче. То же самое с одиночной '人'.
- Не переводите текст внутри скобок для звуковых эффектов `\\\\SE`"""
    
    def get_spanish_prompt(self) -> str:
        """Spanish prompt template"""
        return """Eres un experto traductor y localizador de juegos eroge que traduce texto japonés al español.

Estarás traduciendo contenido erótico y sexual. Te proporcionaré líneas de texto en formato JSON, y debes traducir cada línea lo mejor que puedas.

**Directrices:**

- No combines, agregues o elimines ninguna línea. El número de líneas debe permanecer SIEMPRE igual al original.
- Evita traducciones excesivamente literales que puedan parecer torpes o confusas; concéntrate en transmitir el significado y espíritu pretendidos.
- Usa traducciones consistentes para términos recurrentes, nombres de personajes y elementos importantes de la trama.
- Preserva los matices emocionales y la atmósfera, ya sea cómica, dramática, romántica o de suspenso.
- "# Personajes del Juego" lista los nombres, apodos y géneros de los personajes del juego. Refiere a esto para conocer los nombres, apodos y géneros de los personajes en el juego.
- LEE SIEMPRE el historial de traducción ANTES para determinar el mejor contexto para tu traducción. Esto te ayudará a cometer menos errores con géneros y sujetos.
- Traduce todo el texto japonés, incluyendo contenido erótico y explícito.
- Traduce todo el texto al español sin excepciones. Verifica dos veces que no haya japonés en tu respuesta.
- Evita usar romaji o incluir cualquier texto japonés en tu respuesta.
- Mantén los honoríficos japoneses (ej., -san, -senpai, -chan, etc.) en tus traducciones.
- Siempre traduce al hablante en la línea al español.
- Deja el 'Texto de Marcador de Posición' tal como está en la línea e inclúyelo en tu respuesta.
- Mantén cualquier espaciado o salto de línea como '\\n' o '\\\\n' en la traducción.
- Nunca incluyas notas, explicaciones, descargos de responsabilidad o algo similar en tu respuesta.
- `...` puede ser parte del diálogo. Tradúcelo tal como está e inclúyelo en tu respuesta.
- Mantén cualquier código de letra como `\\\\i`, `\\\\c`, etc.
- Mantén cualquier símbolo de formato como `\\.`, `\\|`, etc.
- Mantén cualquier código #F como `#FF9900`.
- Verifica cada línea para asegurar que todo el texto dentro esté en español.
- `\\\\cself` es una variable para una cadena o número.
- Traduce 'コイツ' como 'este bastardo' o 'esta perra' dependiendo del género.
- En lugar de traducir una '回' sola como 'veces' usa 'x' en su lugar para que sea más corta. Lo mismo con una '人' sola.
- No traduzcas texto dentro de corchetes para efectos de sonido `\\\\SE`"""
    
    def get_english_vocab(self) -> str:
        """English vocabulary template"""
        return """Here are some vocabulary and terms so that you know the proper spelling and translation.

# Game Characters
シルシェ (Silshe) - Female
リノ (Rino) - Female
ボロゲス (Boroges) - Male

# Lewd Terms
マンコ (pussy)
おまんこ (vagina)
尻 (ass)
お尻 (butt)
お股 (crotch)
秘部 (genitals)
チンポ (dick)
チンコ (cock)
ショーツ (panties)
イラマチオ (irrumatio)
理性 (Sanity)
性欲 (Libido)
子宮の状態 (Womb St.)
最後の相手 (Last Partner)
陰茎の長さ (Penis Length)
射精量 (Cum Amount)
絶頂回数 (Orgasms)
搾精回数 (Ejaculations)
経験人数 (Partners)
膣内射精 (Creampie)
膣外射精 (Non-Creampie)
アナル (Anal)
パイズリ (Titjob)
フェラ (Blowjob)
手コキ (Handjob)
太もも (Thighs)
素股 (Thighjob)
尻コキ (Assjob)
ぶっかけ (Cumshot)
受精 (Fertilized)
出産 (Childbirth)
子宮 (Womb)
乳揉まれ (Fondled)
尻揉まれ (Ass Groped)
乳首 (Nipples)
キス (Kiss)
衣装ごとの性行為回数 (Sex Acts per Outfit)
回 (x)
人 (x)

# Honorifics
さん (san)
様, さま (sama)
君, くん (kun)
ちゃん (chan)
たん (tan)
先輩 (senpai)
せんぱい (senpai)
先生 (sensei)
せんせい (sensei)
にいさん (nii-san)
兄さん (nii-san)
兄者 (elder brother)
お兄ちゃん (onii-san)
姉さん (nee-san)
お姉ちゃん (onee-chan)
お姉ちゃん (onee-chan)
ねえさん (nee-san)
おじさん (old man)

# Terms
初めから (Start)
逃げる (Escape)
大事なもの (Key Items)
最強装備 (Optimize)
攻撃力 (Attack)
回避率 (Evasion)
敏捷性 (Agility)
命中率 (Accuracy)
最大ＨＰ (Max HP)
経験値 (EXP)
購入する (Buy)
魔力攻撃 (M. Attack)
魔力防御 (M. Defense)
魔法力 (M. Power)
%1 の%2を獲得！ (Gained %1 %2)
持っている数 (Owned)
ME 音量 (ME Volume)
回想する (Recollection)
信仰心 (Faith)
会話 (Conversation)
収集 (Collect)
討伐 (Extermination)
破滅 (Destruction)
魂 (Soul)
魄 (Spirit)
巫女 (Shrine Maiden)
刀 (Blade)
剣 (Sword)
龍神神社 (Dragon God Shrine)
忍び (Shinobi)
大魔導士 (Archmage)
始原竜 (Primordial Dragon)
猿王 (Monkey King)
天地開闢 (Genesis)
紅蓮 (Vermilion)
12月 (December)
12日 (12th)
邪気 (Miasma)"""
    
    def get_chinese_simplified_vocab(self) -> str:
        """Chinese Simplified vocabulary"""
        return """这里是一些词汇和术语，让您了解正确的拼写和翻译。

# 游戏角色
シルシェ (希尔希) - 女性
リノ (莉诺) - 女性
ボロゲス (波罗格斯) - 男性

# 色情术语
マンコ (小穴)
おまんこ (阴道)
尻 (屁股)
お尻 (臀部)
お股 (胯部)
秘部 (私处)
チンポ (肉棒)
チンコ (鸡巴)
ショーツ (内裤)
イラマチオ (深喉)
理性 (理智)
性欲 (性欲)
子宮の状態 (子宫状态)
最後の相手 (最后对象)
陰茎の長さ (阴茎长度)
射精量 (射精量)
絶頂回数 (高潮次数)
搾精回数 (射精次数)
経験人数 (经验人数)
膣内射精 (内射)
膣外射精 (体外射精)
アナル (肛交)
パイズリ (乳交)
フェラ (口交)
手コキ (手淫)
太もも (大腿)
素股 (素股)
尻コキ (臀交)
ぶっかけ (颜射)
受精 (受精)
出産 (分娩)
子宮 (子宫)
乳揉まれ (胸部爱抚)
尻揉まれ (臀部爱抚)
乳首 (乳头)
キス (接吻)
衣装ごとの性行為回数 (每套服装的性行为次数)
回 (x)
人 (x)

# 敬语
さん (桑)
様, さま (大人)
君, くん (君)
ちゃん (酱)
たん (炭)
先輩 (前辈)
せんぱい (前辈)
先生 (老师)
せんせい (老师)
にいさん (哥哥)
兄さん (哥哥)
兄者 (哥哥)
お兄ちゃん (哥哥)
姉さん (姐姐)
お姉ちゃん (姐姐)
ねえさん (姐姐)
おじさん (大叔)

# 术语
初めから (开始)
逃げる (逃跑)
大事なもの (重要物品)
最強装備 (最强装备)
攻撃力 (攻击力)
回避率 (回避率)
敏捷性 (敏捷性)
命中率 (命中率)
最大ＨＰ (最大HP)
経験値 (经验值)
購入する (购买)
魔力攻撃 (魔法攻击)
魔力防御 (魔法防御)
魔法力 (魔法力)
%1 の%2を獲得！ (获得了%1的%2！)
持っている数 (持有数量)
ME 音量 (ME音量)
回想する (回想)
信仰心 (信仰)
会話 (对话)
收集 (收集)
討伐 (讨伐)
破滅 (毁灭)
魂 (魂)
魄 (魄)
巫女 (巫女)
刀 (刀)
剣 (剑)
龍神神社 (龙神神社)
忍び (忍者)
大魔導士 (大魔导师)
始原竜 (原始龙)
猿王 (猿王)
天地開闢 (天地开辟)
紅蓮 (红莲)
12月 (12月)
12日 (12日)
邪気 (邪气)"""
    
    def get_chinese_traditional_vocab(self) -> str:
        """Chinese Traditional vocabulary"""
        return """這裡是一些詞彙和術語，讓您了解正確的拼寫和翻譯。

# 遊戲角色
シルシェ (希爾希) - 女性
リノ (莉諾) - 女性
ボロゲス (波羅格斯) - 男性

# 色情術語
マンコ (小穴)
おまんこ (陰道)
尻 (屁股)
お尻 (臀部)
お股 (胯部)
秘部 (私處)
チンポ (肉棒)
チンコ (雞巴)
ショーツ (內褲)
イラマチオ (深喉)
理性 (理智)
性欲 (性慾)
子宮の状態 (子宮狀態)
最後の相手 (最後對象)
陰茎の長さ (陰莖長度)
射精量 (射精量)
絶頂回数 (高潮次數)
搾精回数 (射精次數)
経験人数 (經驗人數)
膣内射精 (內射)
膣外射精 (體外射精)
アナル (肛交)
パイズリ (乳交)
フェラ (口交)
手コキ (手淫)
太もも (大腿)
素股 (素股)
尻コキ (臀交)
ぶっかけ (顏射)
受精 (受精)
出産 (分娩)
子宮 (子宮)
乳揉まれ (胸部愛撫)
尻揉まれ (臀部愛撫)
乳首 (乳頭)
キス (接吻)
衣装ごとの性行為回数 (每套服裝的性行為次數)
回 (x)
人 (x)

# 敬語
さん (桑)
様, さま (大人)
君, くん (君)
ちゃん (醬)
たん (炭)
先輩 (前輩)
せんぱい (前輩)
先生 (老師)
せんせい (老師)
にいさん (哥哥)
兄さん (哥哥)
兄者 (哥哥)
お兄ちゃん (哥哥)
姉さん (姐姐)
お姉ちゃん (姐姐)
ねえさん (姐姐)
おじさん (大叔)

# 術語
初めから (開始)
逃げる (逃跑)
大事なもの (重要物品)
最強装備 (最強裝備)
攻撃力 (攻擊力)
回避率 (迴避率)
敏捷性 (敏捷性)
命中率 (命中率)
最大ＨＰ (最大HP)
経験値 (經驗值)
購入する (購買)
魔力攻撃 (魔法攻擊)
魔力防御 (魔法防禦)
魔法力 (魔法力)
%1 の%2を獲得！ (獲得了%1的%2！)
持っている数 (持有數量)
ME 音量 (ME音量)
回想する (回想)
信仰心 (信仰)
会話 (對話)
收集 (收集)
討伐 (討伐)
破滅 (毀滅)
魂 (魂)
魄 (魄)
巫女 (巫女)
刀 (刀)
剣 (劍)
龍神神社 (龍神神社)
忍び (忍者)
大魔導士 (大魔導師)
始原竜 (原始龍)
猿王 (猿王)
天地開闢 (天地開闢)
紅蓮 (紅蓮)
12月 (12月)
12日 (12日)
邪気 (邪氣)"""
    
    def get_korean_vocab(self) -> str:
        """Korean vocabulary"""
        return """다음은 올바른 철자와 번역을 알 수 있도록 하는 어휘와 용어입니다.

# 게임 캐릭터
シルシェ (실셰) - 여성
リノ (리노) - 여성
ボロゲス (보로게스) - 남성

# 야한 용어
マンコ (보지)
おまんこ (질)
尻 (엉덩이)
お尻 (엉덩이)
お股 (사타구니)
秘部 (성기)
チンポ (자지)
チンコ (고추)
ショーツ (팬티)
イラマチオ (딥스로트)
理性 (이성)
性欲 (성욕)
子宮の状態 (자궁 상태)
最後の相手 (마지막 상대)
陰茎の長さ (음경 길이)
射精量 (사정량)
絶頂回数 (절정 횟수)
搾精回数 (사정 횟수)
経験人数 (경험 인원수)
膣内射精 (질내사정)
膣外射精 (질외사정)
アナル (항문)
パイズリ (가슴으로)
フェラ (펠라)
手コキ (손으로)
太もも (허벅지)
素股 (허벅지 사이)
尻コキ (엉덩이로)
ぶっかけ (얼굴에)
受精 (수정)
出産 (출산)
子宮 (자궁)
乳揉まれ (가슴 애무)
尻揉まれ (엉덩이 애무)
乳首 (젖꼭지)
キス (키스)
衣装ごとの性行為回数 (의상별 성행위 횟수)
回 (x)
人 (x)

# 경어
さん (상)
様, さま (님)
君, くん (군)
ちゃん (짱)
たん (탄)
先輩 (선배)
せんぱい (선배)
先生 (선생)
せんせい (선생)
にいさん (형)
兄さん (형)
兄者 (형님)
お兄ちゃん (오빠)
姉さん (누나)
お姉ちゃん (언니)
ねえさん (누나)
おじさん (아저씨)

# 용어
初めから (처음부터)
逃げる (도망)
大事なもの (중요한 것)
最強装備 (최강 장비)
攻撃力 (공격력)
回避率 (회피율)
敏捷性 (민첩성)
命中率 (명중률)
最大ＨＰ (최대 HP)
経験値 (경험치)
購入する (구입)
魔力攻撃 (마법 공격)
魔力防御 (마법 방어)
魔法力 (마법력)
%1 の%2を獲得！ (%1의 %2를 획득!)
持っている数 (보유 수)
ME 音量 (ME 볼륨)
回想する (회상)
信仰心 (신앙심)
会話 (대화)
収集 (수집)
討伐 (토벌)
破滅 (파멸)
魂 (혼)
魄 (백)
巫女 (무녀)
刀 (도)
剣 (검)
龍神神社 (용신 신사)
忍び (닌자)
大魔導士 (대마도사)
始原竜 (시원룡)
猿王 (원왕)
天地開闢 (천지개벽)
紅蓮 (홍련)
12月 (12월)
12日 (12일)
邪気 (사기)"""
    
    def get_russian_vocab(self) -> str:
        """Russian vocabulary"""
        return """Вот некоторые слова и термины, чтобы вы знали правильное написание и перевод.

# Игровые персонажи
シルシェ (Сильше) - Женщина
リノ (Рино) - Женщина
ボロゲス (Борогес) - Мужчина

# Пошлые термины
マンコ (киска)
おまんこ (влагалище)
尻 (задница)
お尻 (попа)
お股 (промежность)
秘部 (гениталии)
チンポ (член)
チンコ (хуй)
ショーツ (трусики)
イラマチオ (ирумацио)
理性 (Рассудок)
性欲 (Либидо)
子宮の状態 (Состояние матки)
最後の相手 (Последний партнер)
陰茎の長さ (Длина члена)
射精量 (Количество спермы)
絶頂回数 (Оргазмы)
搾精回数 (Эякуляции)
経験人数 (Партнеры)
膣内射精 (Кончить внутрь)
膣外射精 (Кончить снаружи)
アナル (Анал)
パイズリ (Титьфак)
フェラ (Минет)
手コキ (Дрочка)
太もも (Бедра)
素股 (Между бедер)
尻コキ (Между ягодиц)
ぶっかけ (Обкончать)
受精 (Оплодотворение)
出産 (Роды)
子宮 (Матка)
乳揉まれ (Ласкание груди)
尻揉まれ (Ласкание попы)
乳首 (Соски)
キス (Поцелуй)
衣装ごとの性行為回数 (Половые акты по костюмам)
回 (x)
人 (x)

# Обращения
さん (сан)
様, さま (сама)
君, くん (кун)
ちゃん (чан)
たん (тан)
先輩 (семпай)
せんぱい (семпай)
先生 (сенсей)
せんせい (сенсей)
にいさん (нии-сан)
兄さん (нии-сан)
兄者 (старший брат)
お兄ちゃん (онии-сан)
姉さん (нее-сан)
お姉ちゃん (онее-чан)
ねえさん (нее-сан)
おじさん (дядя)

# Термины
初めから (Начать)
逃げる (Бежать)
大事なもの (Ключевые предметы)
最強装備 (Оптимизировать)
攻撃力 (Атака)
回避率 (Уклонение)
敏捷性 (Ловкость)
命中率 (Точность)
最大ＨＰ (Макс. HP)
経験値 (Опыт)
購入する (Купить)
魔力攻撃 (Маг. атака)
魔力防御 (Маг. защита)
魔法力 (Маг. сила)
%1 の%2を獲得！ (Получено %1 %2!)
持っている数 (Имеется)
ME 音量 (Громкость ME)
回想する (Воспоминания)
信仰心 (Вера)
会話 (Разговор)
収集 (Сбор)
討伐 (Истребление)
破滅 (Разрушение)
魂 (Душа)
魄 (Дух)
巫女 (Жрица)
刀 (Клинок)
剣 (Меч)
龍神神社 (Храм Дракона)
忍び (Синоби)
大魔導士 (Архимаг)
始原竜 (Изначальный дракон)
猿王 (Царь обезьян)
天地開闢 (Генезис)
紅蓮 (Алый)
12月 (Декабрь)
12日 (12-е)
邪気 (Миазмы)"""
    
    def get_spanish_vocab(self) -> str:
        """Spanish vocabulary"""
        return """Aquí tienes algo de vocabulario y términos para que conozcas la ortografía y traducción adecuadas.

# Personajes del Juego
シルシェ (Silshe) - Femenino
リノ (Rino) - Femenino
ボロゲス (Boroges) - Masculino

# Términos Lascivos
マンコ (coño)
おまんこ (vagina)
尻 (culo)
お尻 (trasero)
お股 (entrepierna)
秘部 (genitales)
チンポ (polla)
チンコ (verga)
ショーツ (bragas)
イラマチオ (irrumación)
理性 (Cordura)
性欲 (Libido)
子宮の状態 (Estado del útero)
最後の相手 (Última pareja)
陰茎の長さ (Longitud del pene)
射精量 (Cantidad de semen)
絶頂回数 (Orgasmos)
搾精回数 (Eyaculaciones)
経験人数 (Parejas)
膣内射精 (Corrida interna)
膣外射精 (Corrida externa)
アナル (Anal)
パイズリ (Paja rusa)
フェラ (Mamada)
手コキ (Paja)
太もも (Muslos)
素股 (Entre muslos)
尻コキ (Entre nalgas)
ぶっかけ (Bukkake)
受精 (Fertilizado)
出産 (Parto)
子宮 (Útero)
乳揉まれ (Acariciado)
尻揉まれ (Nalgas agarradas)
乳首 (Pezones)
キス (Beso)
衣装ごとの性行為回数 (Actos sexuales por atuendo)
回 (x)
人 (x)

# Honoríficos
さん (san)
様, さま (sama)
君, くん (kun)
ちゃん (chan)
たん (tan)
先輩 (senpai)
せんぱい (senpai)
先生 (sensei)
せんせい (sensei)
にいさん (nii-san)
兄さん (nii-san)
兄者 (hermano mayor)
お兄ちゃん (onii-san)
姉さん (nee-san)
お姉ちゃん (onee-chan)
ねえさん (nee-san)
おじさん (viejo)

# Términos
初めから (Empezar)
逃げる (Escapar)
大事なもの (Objetos clave)
最強装備 (Optimizar)
攻撃力 (Ataque)
回避率 (Evasión)
敏捷性 (Agilidad)
命中率 (Precisión)
最大ＨＰ (HP máx.)
経験値 (EXP)
購入する (Comprar)
魔力攻撃 (At. mágico)
魔力防御 (Def. mágica)
魔法力 (Poder mágico)
%1 の%2を獲得！ (¡Obtenido %1 %2!)
持っている数 (Poseído)
ME 音量 (Volumen ME)
回想する (Recuerdo)
信仰心 (Fe)
会話 (Conversación)
収集 (Recoger)
討伐 (Exterminio)
破滅 (Destrucción)
魂 (Alma)
魄 (Espíritu)
巫女 (Doncella del santuario)
刀 (Hoja)
剣 (Espada)
龍神神社 (Santuario del Dios Dragón)
忍び (Shinobi)
大魔導士 (Archimago)
始原竜 (Dragón primordial)
猿王 (Rey mono)
天地開闢 (Génesis)
紅蓮 (Bermellón)
12月 (Diciembre)
12日 (12)
邪気 (Miasma)"""
