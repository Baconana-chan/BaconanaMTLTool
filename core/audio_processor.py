"""
Audio Processor for Transcription and Subtitle Generation
Supports multiple transcription providers and local models
"""

import os
import json
import logging
import tempfile
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import subprocess
import time

try:
    import faster_whisper
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import onnxruntime
    ONNXRUNTIME_AVAILABLE = True
except ImportError:
    ONNXRUNTIME_AVAILABLE = False

try:
    import transformers
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from .api_client import APIClient
from .models import TranscriptionResult, SubtitleSegment


class AudioProcessor:
    """Handles audio transcription and subtitle generation"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.models_dir = Path("models/faster-whisper")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Available models and their URLs
        self.faster_whisper_models = {
            "tiny": {
                "model.bin": "https://huggingface.co/guillaumekln/faster-whisper-tiny/resolve/main/model.bin",
                "config.json": "https://huggingface.co/guillaumekln/faster-whisper-tiny/resolve/main/config.json",
                "tokenizer.json": "https://huggingface.co/guillaumekln/faster-whisper-tiny/resolve/main/tokenizer.json",
                "vocabulary.txt": "https://huggingface.co/guillaumekln/faster-whisper-tiny/resolve/main/vocabulary.txt"
            },
            "base": {
                "model.bin": "https://huggingface.co/guillaumekln/faster-whisper-base/resolve/main/model.bin",
                "config.json": "https://huggingface.co/guillaumekln/faster-whisper-base/resolve/main/config.json",
                "tokenizer.json": "https://huggingface.co/guillaumekln/faster-whisper-base/resolve/main/tokenizer.json",
                "vocabulary.txt": "https://huggingface.co/guillaumekln/faster-whisper-base/resolve/main/vocabulary.txt"
            },
            "small": {
                "model.bin": "https://huggingface.co/guillaumekln/faster-whisper-small/resolve/main/model.bin",
                "config.json": "https://huggingface.co/guillaumekln/faster-whisper-small/resolve/main/config.json",
                "tokenizer.json": "https://huggingface.co/guillaumekln/faster-whisper-small/resolve/main/tokenizer.json",
                "vocabulary.txt": "https://huggingface.co/guillaumekln/faster-whisper-small/resolve/main/vocabulary.txt"
            },
            "medium": {
                "model.bin": "https://huggingface.co/guillaumekln/faster-whisper-medium/resolve/main/model.bin",
                "config.json": "https://huggingface.co/guillaumekln/faster-whisper-medium/resolve/main/config.json",
                "tokenizer.json": "https://huggingface.co/guillaumekln/faster-whisper-medium/resolve/main/tokenizer.json",
                "vocabulary.txt": "https://huggingface.co/guillaumekln/faster-whisper-medium/resolve/main/vocabulary.txt"
            },
            "large-v1": {
                "model.bin": "https://huggingface.co/guillaumekln/faster-whisper-large-v1/resolve/main/model.bin",
                "config.json": "https://huggingface.co/guillaumekln/faster-whisper-large-v1/resolve/main/config.json",
                "tokenizer.json": "https://huggingface.co/guillaumekln/faster-whisper-large-v1/resolve/main/tokenizer.json",
                "vocabulary.txt": "https://huggingface.co/guillaumekln/faster-whisper-large-v1/resolve/main/vocabulary.txt"
            },
            "large-v2": {
                "model.bin": "https://huggingface.co/guillaumekln/faster-whisper-large-v2/resolve/main/model.bin",
                "config.json": "https://huggingface.co/guillaumekln/faster-whisper-large-v2/resolve/main/config.json",
                "tokenizer.json": "https://huggingface.co/guillaumekln/faster-whisper-large-v2/resolve/main/tokenizer.json",
                "vocabulary.txt": "https://huggingface.co/guillaumekln/faster-whisper-large-v2/resolve/main/vocabulary.txt"
            },
            "anime-whisper": {
                "model.safetensors": "https://huggingface.co/litagin/anime-whisper/resolve/main/model.safetensors",
                "added_tokens.json": "https://huggingface.co/litagin/anime-whisper/resolve/main/added_tokens.json",
                "config.json": "https://huggingface.co/litagin/anime-whisper/resolve/main/config.json",
                "generation_config.json": "https://huggingface.co/litagin/anime-whisper/resolve/main/generation_config.json",
                "merges.txt": "https://huggingface.co/litagin/anime-whisper/resolve/main/merges.txt",
                "normalizer.json": "https://huggingface.co/litagin/anime-whisper/resolve/main/normalizer.json",
                "preprocessor_config.json": "https://huggingface.co/litagin/anime-whisper/resolve/main/preprocessor_config.json",
                "special_tokens_map.json": "https://huggingface.co/litagin/anime-whisper/resolve/main/special_tokens_map.json",
                "tokenizer_config.json": "https://huggingface.co/litagin/anime-whisper/resolve/main/tokenizer_config.json",
                "vocab.json": "https://huggingface.co/litagin/anime-whisper/resolve/main/vocab.json"
            }
        }
        
        # Pricing information (per hour unless specified)
        self.provider_pricing = {
            "openai-whisper": {"price": 0.006, "unit": "minute"},
            "groq-whisper-v3-large": {"price": 0.111, "unit": "hour"},
            "groq-whisper-large-v3-turbo": {"price": 0.04, "unit": "hour"},
            "assemblyai-universal-2": {"price": 0.12, "unit": "hour"},
            "nova-1": {"price": 0.0043, "unit": "minute"},
            "nova-2": {"price": 0.0043, "unit": "minute"},
            "nova-3-multilingual": {"price": 0.0052, "unit": "minute"},
            "nova-3-monolingual": {"price": 0.0043, "unit": "minute"},
            "speechmatics": {"price": 0.30, "unit": "hour"},
            "gladia": {"price": 0.612, "unit": "hour"},
            "azure-ai-speech-realtime": {"price": 1.0, "unit": "hour"},
            "azure-ai-speech-batch": {"price": 0.18, "unit": "hour"},
            "faster-whisper": {"price": 0.0, "unit": "free"},
            "anime-whisper": {"price": 0.0, "unit": "free"}
        }

    def check_dependencies(self) -> Dict[str, Dict[str, Union[bool, str]]]:
        """Check availability of all dependencies"""
        deps = {
            "faster_whisper": {
                "available": self._check_import("faster_whisper"),
                "description": "Required for local transcription models",
                "install_command": "pip install faster-whisper"
            },
            "openai": {
                "available": self._check_import("openai"),
                "description": "Required for OpenAI Whisper API",
                "install_command": "pip install openai"
            },
            "onnxruntime": {
                "available": self._check_import("onnxruntime"),
                "description": "Required for VAD (Voice Activity Detection) filter",
                "install_command": "pip install onnxruntime"
            },
            "transformers": {
                "available": self._check_import("transformers"),
                "description": "Required for Anime-Whisper and other Hugging Face models",
                "install_command": "pip install transformers torch"
            }
        }
        return deps

    def _check_import(self, module_name: str) -> bool:
        """Dynamically check if a module can be imported"""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False

    def get_missing_dependencies(self) -> List[str]:
        """Get list of missing dependencies"""
        deps = self.check_dependencies()
        missing = []
        for name, info in deps.items():
            if not info["available"]:
                missing.append(name)
        return missing

    def can_use_vad_filter(self) -> bool:
        """Check if VAD filter can be used"""
        return self._check_import("onnxruntime")

    def get_installed_models(self) -> List[str]:
        """Get list of installed faster-whisper models"""
        installed = []
        for model_name in self.faster_whisper_models.keys():
            model_path = self.models_dir / model_name
            if model_path.exists():
                # Check for different model file types
                if model_name == "anime-whisper":
                    # Anime-whisper uses .safetensors
                    if (model_path / "model.safetensors").exists():
                        installed.append(model_name)
                else:
                    # Standard faster-whisper models use .bin
                    if (model_path / "model.bin").exists():
                        installed.append(model_name)
        return installed

    def is_model_installed(self, model_name: str) -> bool:
        """Check if a specific model is installed"""
        model_path = self.models_dir / model_name
        if not model_path.exists():
            return False
        
        # Check for different model file types
        if model_name == "anime-whisper":
            return (model_path / "model.safetensors").exists()
        else:
            return (model_path / "model.bin").exists()
        return model_path.exists() and (model_path / "model.bin").exists()

    def download_model(self, model_name: str, progress_callback=None) -> bool:
        """Download a faster-whisper model"""
        if model_name not in self.faster_whisper_models:
            self.logger.error(f"Unknown model: {model_name}")
            return False
            
        model_path = self.models_dir / model_name
        model_path.mkdir(parents=True, exist_ok=True)
        
        files = self.faster_whisper_models[model_name]
        total_files = len(files)
        
        try:
            for i, (filename, url) in enumerate(files.items()):
                file_path = model_path / filename
                
                if file_path.exists():
                    self.logger.info(f"File {filename} already exists, skipping")
                    if progress_callback:
                        progress_callback(i + 1, total_files, f"Skipped {filename}")
                    continue
                
                self.logger.info(f"Downloading {filename}...")
                if progress_callback:
                    progress_callback(i, total_files, f"Downloading {filename}...")
                
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if progress_callback and total_size > 0:
                                percent = (downloaded / total_size) * 100
                                progress_callback(i, total_files, 
                                               f"Downloading {filename}... {percent:.1f}%")
                
                if progress_callback:
                    progress_callback(i + 1, total_files, f"Downloaded {filename}")
            
            self.logger.info(f"Model {model_name} downloaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error downloading model {model_name}: {e}")
            return False

    def delete_model(self, model_name: str) -> bool:
        """Delete an installed model"""
        model_path = self.models_dir / model_name
        try:
            if model_path.exists():
                import shutil
                shutil.rmtree(model_path)
                self.logger.info(f"Model {model_name} deleted successfully")
                return True
        except Exception as e:
            self.logger.error(f"Error deleting model {model_name}: {e}")
        return False

    def estimate_cost(self, audio_duration_seconds: float, provider: str) -> Dict[str, Union[float, str]]:
        """Estimate transcription cost"""
        if provider not in self.provider_pricing:
            return {"cost": 0.0, "unit": "unknown", "error": "Unknown provider"}
        
        pricing = self.provider_pricing[provider]
        
        if pricing["unit"] == "minute":
            duration_minutes = audio_duration_seconds / 60
            cost = duration_minutes * pricing["price"]
        elif pricing["unit"] == "hour":
            duration_hours = audio_duration_seconds / 3600
            cost = duration_hours * pricing["price"]
        else:
            cost = 0.0
        
        return {
            "cost": round(cost, 4),
            "unit": pricing["unit"],
            "price_per_unit": pricing["price"]
        }

    def get_audio_duration(self, file_path: str) -> float:
        """Get audio file duration in seconds using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except Exception as e:
            self.logger.warning(f"Could not get audio duration: {e}")
        return 0.0

    def transcribe_with_openai(self, audio_file: str, **kwargs) -> TranscriptionResult:
        """Transcribe audio using OpenAI Whisper API"""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available")
        
        config = self.config_manager.get_config()
        client = openai.OpenAI(api_key=config.get('api_key'))
        
        try:
            with open(audio_file, 'rb') as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    response_format="verbose_json",
                    timestamp_granularities=["segment"]
                )
            
            segments = []
            for segment in transcript.segments:
                segments.append(SubtitleSegment(
                    start=segment.start,
                    end=segment.end,
                    text=segment.text.strip()
                ))
            
            return TranscriptionResult(
                text=transcript.text,
                segments=segments,
                language=transcript.language
            )
            
        except Exception as e:
            self.logger.error(f"OpenAI transcription error: {e}")
            raise

    def transcribe_with_anime_whisper(self, audio_file: str, model_name: str = "litagin/anime-whisper",
                                     device: str = "auto", temperature: float = 0.0,
                                     word_timestamps: bool = False, progress_callback=None, **kwargs) -> TranscriptionResult:
        """Транскрипция с использованием Anime-Whisper модели через Hugging Face"""
        try:
            if not TRANSFORMERS_AVAILABLE:
                raise RuntimeError("transformers library is required for Anime-Whisper. Install with: pip install transformers torch")
            
            from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
            import torch
            
            # Определяем путь к локальной модели
            local_model_path = self.models_dir / "faster-whisper" / "anime-whisper"
            
            # Используем локальную модель если она существует, иначе загружаем из HuggingFace
            if local_model_path.exists():
                model_path = str(local_model_path)
                self.logger.info(f"Using local Anime-Whisper model: {model_path}")
            else:
                model_path = model_name
                self.logger.info(f"Using online Anime-Whisper model: {model_path}")
            
            # Определяем устройство
            if device == "auto":
                device = "cuda:0" if torch.cuda.is_available() else "cpu"
            torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            
            self.logger.info(f"Loading Anime-Whisper model on {device}")
            
            # Загружаем модель и процессор
            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_path,
                torch_dtype=torch_dtype,
                low_cpu_mem_usage=True,
                use_safetensors=True
            )
            model.to(device)
            
            processor = AutoProcessor.from_pretrained(model_path)
            
            # Создаем pipeline для транскрипции
            pipe = pipeline(
                "automatic-speech-recognition",
                model=model,
                tokenizer=processor.tokenizer,
                feature_extractor=processor.feature_extractor,
                max_new_tokens=128,
                chunk_length_s=30,
                batch_size=16,
                return_timestamps=word_timestamps,
                torch_dtype=torch_dtype,
                device=device,
            )
            
            # Подготавливаем параметры генерации
            generate_kwargs = {}
            if temperature is not None and temperature > 0:
                generate_kwargs["temperature"] = float(temperature)
            
            self.logger.info(f"Starting Anime-Whisper transcription of: {audio_file}")
            
            # Выполняем транскрипцию
            result = pipe(audio_file, generate_kwargs=generate_kwargs)
            
            # Преобразуем результат в наш формат
            segments = []
            if word_timestamps and "chunks" in result:
                for chunk in result["chunks"]:
                    timestamp = chunk.get('timestamp', [0, 0])
                    start_time = timestamp[0] if len(timestamp) > 0 else 0.0
                    end_time = timestamp[1] if len(timestamp) > 1 else start_time
                    
                    segments.append(TranscriptionSegment(
                        start=start_time,
                        end=end_time,
                        text=chunk.get('text', '').strip()
                    ))
            else:
                # Если нет временных меток, создаем один сегмент
                segments.append(TranscriptionSegment(
                    start=0.0,
                    end=0.0,
                    text=result['text'].strip()
                ))
            
            # Создаем результат
            transcription_result = TranscriptionResult(
                text=result['text'].strip(),
                segments=segments,
                language='ja',  # Anime-Whisper обычно для японского
                language_probability=0.9
            )
            
            self.logger.info("Anime-Whisper transcription completed successfully")
            return transcription_result
            
        except Exception as e:
            self.logger.error(f"Anime-Whisper transcription error: {e}")
            raise RuntimeError(f"Anime-Whisper transcription failed: {str(e)}")

    def transcribe_with_faster_whisper(self, audio_file: str, model_name: str = "base", 
                                      compute_type: str = "auto", device: str = "cpu",
                                      beam_size: int = 5, temperature: float = 0.0,
                                      vad_filter: bool = True, word_timestamps: bool = False,
                                      repetition_penalty: float = 1.0, no_repeat_ngram_size: int = 0,
                                      compression_ratio_threshold: float = 2.4, logprob_threshold: float = -1.0,
                                      condition_on_previous_text: bool = True,
                                      progress_callback=None, **kwargs) -> TranscriptionResult:
        """Transcribe audio using local faster-whisper model"""
        if not FASTER_WHISPER_AVAILABLE:
            raise ImportError("faster-whisper library not available")
        
        if not self.is_model_installed(model_name):
            raise FileNotFoundError(f"Model {model_name} is not installed")
        
        model_path = str(self.models_dir / model_name)
        
        try:
            # Initialize model with user settings
            if progress_callback:
                progress_callback(10, "Loading model...")
            
            model = faster_whisper.WhisperModel(
                model_path, 
                device=device, 
                compute_type=compute_type
            )
            
            if progress_callback:
                progress_callback(20, "Model loaded, starting transcription...")
            
            # Get audio duration for progress estimation
            start_time = time.time()
            
            # Check VAD filter availability
            if vad_filter and not self.can_use_vad_filter():
                self.logger.warning("VAD filter requested but onnxruntime not available. Disabling VAD filter.")
                vad_filter = False
            
            # Prepare transcription parameters
            transcribe_params = {
                "beam_size": beam_size,
                "vad_filter": vad_filter,
                "word_timestamps": word_timestamps,
                "repetition_penalty": repetition_penalty,
                "compression_ratio_threshold": compression_ratio_threshold,
                "logprob_threshold": logprob_threshold,
                "condition_on_previous_text": condition_on_previous_text
            }
            
            # Add no_repeat_ngram_size only if it's greater than 0
            if no_repeat_ngram_size > 0:
                transcribe_params["no_repeat_ngram_size"] = no_repeat_ngram_size
            
            # Only add temperature if it's greater than 0
            if temperature > 0:
                transcribe_params["temperature"] = temperature
            
            self.logger.info(f"Transcription parameters: {transcribe_params}")
            
            if progress_callback:
                progress_callback(25, "Starting transcription with faster-whisper...")
            
            segments, info = model.transcribe(audio_file, **transcribe_params)
            
            subtitle_segments = []
            full_text = ""
            processed_duration = 0
            
            if progress_callback:
                progress_callback(30, "Processing segments...")

            # Process segments and remove duplicates
            previous_text = ""
            duplicate_threshold = 0.8  # Similarity threshold for duplicate detection
            
            for i, segment in enumerate(segments):
                # Ensure start and end are valid numbers
                segment_start = segment.start if segment.start is not None else 0.0
                segment_end = segment.end if segment.end is not None else segment_start + 1.0
                current_text = segment.text.strip()
                
                # Skip if text is very similar to previous segment
                if previous_text and self._text_similarity(current_text, previous_text) > duplicate_threshold:
                    self.logger.debug(f"Skipping duplicate segment: '{current_text}'")
                    continue
                
                subtitle_segments.append(SubtitleSegment(
                    start=segment_start,
                    end=segment_end,
                    text=current_text
                ))
                full_text += current_text + " "
                previous_text = current_text                # Update progress based on processed audio duration
                processed_duration = segment_end
                if progress_callback and i % 10 == 0:  # Update every 10 segments
                    elapsed_time = time.time() - start_time
                    if (info.duration and info.duration > 0 and 
                        processed_duration > 0):
                        try:
                            progress_percent = min(30 + int((processed_duration / info.duration) * 60), 90)
                            remaining_duration = info.duration - processed_duration
                            if remaining_duration > 0:
                                remaining_time = (elapsed_time / processed_duration) * remaining_duration
                                progress_callback(progress_percent, f"Processing... ({elapsed_time:.1f}s elapsed, ~{remaining_time:.1f}s remaining)")
                            else:
                                progress_callback(progress_percent, f"Processing... ({elapsed_time:.1f}s elapsed)")
                        except (ZeroDivisionError, TypeError, AttributeError):
                            progress_callback(30 + min(i, 60), f"Processing segment {i+1}... ({elapsed_time:.1f}s elapsed)")
                    else:
                        progress_callback(30 + min(i, 60), f"Processing segment {i+1}... ({elapsed_time:.1f}s elapsed)")
            
            if progress_callback:
                progress_callback(95, "Finalizing transcription...")
            
            result = TranscriptionResult(
                text=full_text.strip(),
                segments=subtitle_segments,
                language=info.language
            )
            
            if progress_callback:
                total_time = time.time() - start_time
                progress_callback(100, f"Transcription completed in {total_time:.1f}s")
            
            return result
            
        except Exception as e:
            import traceback
            self.logger.error(f"Faster-whisper transcription error: {e}")
            self.logger.error(f"Error type: {type(e).__name__}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings using simple character-based comparison"""
        if not text1 or not text2:
            return 0.0
        
        # Normalize texts (remove extra spaces, convert to lowercase)
        norm_text1 = " ".join(text1.lower().split())
        norm_text2 = " ".join(text2.lower().split())
        
        if norm_text1 == norm_text2:
            return 1.0
        
        # Calculate similarity using character overlap
        set1 = set(norm_text1)
        set2 = set(norm_text2)
        
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0

    def transcribe_audio(self, audio_file: str, provider: str, **kwargs) -> TranscriptionResult:
        """Main transcription method"""
        self.logger.info(f"Starting transcription with {provider}")
        
        if provider == "openai-whisper":
            return self.transcribe_with_openai(audio_file, **kwargs)
        elif provider.startswith("faster-whisper-") or "Faster-Whisper" in provider:
            # Extract model name from provider string
            if "Faster-Whisper" in provider:
                if "Tiny" in provider:
                    model_name = "tiny"
                elif "Base" in provider:
                    model_name = "base"
                elif "Small" in provider:
                    model_name = "small"
                elif "Medium" in provider:
                    model_name = "medium"
                elif "Large-V1" in provider:
                    model_name = "large-v1"
                elif "Large-V2" in provider:
                    model_name = "large-v2"
                else:
                    model_name = "base"  # fallback
            else:
                model_name = provider.replace("faster-whisper-", "")
            return self.transcribe_with_faster_whisper(audio_file, model_name, **kwargs)
        elif "Anime-Whisper" in provider or provider.startswith("anime-whisper") or provider == "anime-whisper":
            return self.transcribe_with_anime_whisper(audio_file, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def format_time_srt(self, seconds: float) -> str:
        """Format time for SRT subtitles"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace('.', ',')

    def format_time_vtt(self, seconds: float) -> str:
        """Format time for VTT subtitles"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

    def format_time_ass(self, seconds: float) -> str:
        """Format time for ASS subtitles"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        centiseconds = int((secs % 1) * 100)
        return f"{hours:01d}:{minutes:02d}:{int(secs):02d}.{centiseconds:02d}"

    def generate_srt(self, result: TranscriptionResult) -> str:
        """Generate SRT subtitle format"""
        srt_content = ""
        for i, segment in enumerate(result.segments, 1):
            start_time = self.format_time_srt(segment.start)
            end_time = self.format_time_srt(segment.end)
            srt_content += f"{i}\n{start_time} --> {end_time}\n{segment.text}\n\n"
        return srt_content

    def generate_vtt(self, result: TranscriptionResult) -> str:
        """Generate VTT subtitle format"""
        vtt_content = "WEBVTT\n\n"
        for segment in result.segments:
            start_time = self.format_time_vtt(segment.start)
            end_time = self.format_time_vtt(segment.end)
            vtt_content += f"{start_time} --> {end_time}\n{segment.text}\n\n"
        return vtt_content

    def get_video_resolution(self, video_file: str) -> Tuple[int, int]:
        """Get video resolution using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams',
                '-select_streams', 'v:0', video_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            if 'streams' in data and len(data['streams']) > 0:
                stream = data['streams'][0]
                width = int(stream.get('width', 1920))
                height = int(stream.get('height', 1080))
                return width, height
        except Exception as e:
            self.logger.warning(f"Could not get video resolution: {e}")
        
        # Default to 1080p if detection fails
        return 1920, 1080

    def calculate_ass_font_size(self, video_height: int) -> int:
        """Calculate appropriate font size based on video resolution"""
        # Base font size for different resolutions - more granular scaling
        if video_height >= 2160:  # 4K
            return 48
        elif video_height >= 1440:  # 1440p
            return 36
        elif video_height >= 1080:  # 1080p
            return 28
        elif video_height >= 720:   # 720p
            return 20
        elif video_height >= 576:   # PAL SD
            return 18
        elif video_height >= 480:   # NTSC SD (480p)
            return 14
        elif video_height >= 360:   # 360p
            return 12
        else:  # 240p or lower
            return 10

    def generate_ass(self, result: TranscriptionResult, video_file: Optional[str] = None, 
                     auto_resolution: bool = True, manual_font_size: int = 28) -> str:
        """Generate ASS subtitle format with adaptive font sizing"""
        
        # Determine font size and resolution based on video or manual setting
        font_size = manual_font_size  # Default/manual setting
        margin_v = 15   # Default vertical margin
        play_res_x = 1920  # Default resolution
        play_res_y = 1080
        
        if auto_resolution and video_file:
            try:
                width, height = self.get_video_resolution(video_file)
                font_size = self.calculate_ass_font_size(height)
                # Scale margins proportionally - adjusted for different resolutions
                if height <= 480:
                    margin_v = max(8, int(height * 0.025))  # 2.5% for SD
                else:
                    margin_v = max(10, int(height * 0.014))  # 1.4% for HD+
                # Use actual video resolution for PlayRes
                play_res_x = width
                play_res_y = height
                self.logger.info(f"Video resolution: {width}x{height}, using font size: {font_size}, margin: {margin_v}")
            except Exception as e:
                self.logger.warning(f"Could not determine video resolution, using manual font size: {manual_font_size}")
                font_size = manual_font_size
        else:
            font_size = manual_font_size
            self.logger.info(f"Using manual font size: {font_size}")
        
        ass_content = f"""[Script Info]
Title: Generated Subtitles
ScriptType: v4.00+
PlayResX: {play_res_x}
PlayResY: {play_res_y}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        for segment in result.segments:
            start_time = self.format_time_ass(segment.start)
            end_time = self.format_time_ass(segment.end)
            text = segment.text.replace('\n', '\\N')
            ass_content += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{text}\n"
        return ass_content

    def save_subtitles(self, result: TranscriptionResult, output_path: str, format_type: str, 
                      source_file: Optional[str] = None, auto_resolution: bool = True, manual_font_size: int = 28) -> bool:
        """Save subtitles in specified format"""
        try:
            if format_type.lower() == "srt":
                content = self.generate_srt(result)
            elif format_type.lower() == "vtt":
                content = self.generate_vtt(result)
            elif format_type.lower() == "ass":
                content = self.generate_ass(result, source_file, auto_resolution, manual_font_size)
            else:
                raise ValueError(f"Unsupported subtitle format: {format_type}")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Subtitles saved to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving subtitles: {e}")
            return False

    def translate_subtitles(self, result: TranscriptionResult, target_language: str) -> TranscriptionResult:
        """Translate subtitle segments using the translation manager"""
        from .translator import TranslationManager
        
        translator = TranslationManager(self.config_manager)
        translated_segments = []
        
        for segment in result.segments:
            try:
                translated_text = translator.translate_text(segment.text, target_language)
                translated_segments.append(SubtitleSegment(
                    start=segment.start,
                    end=segment.end,
                    text=translated_text
                ))
            except Exception as e:
                self.logger.error(f"Error translating segment: {e}")
                # Keep original text if translation fails
                translated_segments.append(segment)
        
        # Combine all translated text
        full_translated_text = " ".join([seg.text for seg in translated_segments])
        
        return TranscriptionResult(
            text=full_translated_text,
            segments=translated_segments,
            language=target_language
        )
