"""
Project Estimator for translation cost and time estimation
Supports RPG Maker, Ren'Py, Unity, Wolf RPG Editor, KiriKiri, NScripter projects, and Light Novels
"""

import os
import json
import datetime
from typing import Dict, List, Any, Optional, Tuple
from core.file_processor import FileProcessor
from core.renpy_processor import RenpyProcessor
from core.unity_processor import UnityProcessor
from core.wolf_processor import WolfProcessor
from core.kirikiri_processor import KiriKiriProcessor
from core.nscripter_processor import NScripterProcessor
from core.livemaker_processor import LiveMakerProcessor
from core.tyranobuilder_processor import TyranoBuilderProcessor
from core.srpg_studio_processor import SRPGStudioProcessor
from core.lune_processor import LuneProcessor
from core.regex_processor import RegexProcessor
from core.lightnovel_processor import LightNovelProcessor
from core.models import ModelDatabase


class ProjectEstimator:
    """Estimates translation costs and requirements for game projects"""
    
    def __init__(self):
        self.file_processor = FileProcessor()
        self.renpy_processor = RenpyProcessor()
        self.unity_processor = UnityProcessor()
        self.wolf_processor = WolfProcessor()
        self.kirikiri_processor = KiriKiriProcessor()
        self.nscripter_processor = NScripterProcessor()
        self.livemaker_processor = LiveMakerProcessor()
        self.tyranobuilder_processor = TyranoBuilderProcessor()
        self.srpg_studio_processor = SRPGStudioProcessor()
        self.lune_processor = LuneProcessor()
        self.regex_processor = RegexProcessor()
        self.lightnovel_processor = LightNovelProcessor()
        self.model_db = ModelDatabase()
    
    def estimate_project(self, input_dir: str, model_name: str) -> Dict[str, Any]:
        """
        Estimate translation costs and requirements for a project
        
        Args:
            input_dir: Project root directory
            model_name: Model to use for cost calculation
            
        Returns:
            Dictionary with estimation results
        """
        
        # Detect project type
        is_lightnovel = self._detect_lightnovel_project(input_dir)
        is_renpy = self.renpy_processor.detect_renpy_project(input_dir)
        is_unity = self.unity_processor.detect_unity_project(input_dir)
        is_wolf = self.wolf_processor.detect_wolf_project(input_dir)
        is_kirikiri = self.kirikiri_processor.detect_kirikiri_project(input_dir)
        is_nscripter = self.nscripter_processor.detect_nscripter_project(input_dir)
        is_livemaker = len(self.livemaker_processor.find_livemaker_files(input_dir)) > 0
        is_tyranobuilder = len(self.tyranobuilder_processor.find_tyranobuilder_files(input_dir)) > 0
        is_srpg_studio = len(self.srpg_studio_processor.find_srpg_studio_files(input_dir)) > 0
        is_lune = len(self.lune_processor.find_lune_files(input_dir)) > 0
        is_regex = len(self.regex_processor.find_regex_files(input_dir)) > 0
        
        if is_lightnovel:
            project_type = "Light Novel"
        elif is_renpy:
            project_type = "Ren'Py"
        elif is_unity:
            project_type = "Unity"
        elif is_wolf:
            project_type = "Wolf RPG Editor"
        elif is_kirikiri:
            project_type = "KiriKiri"
        elif is_nscripter:
            project_type = "NScripter"
        elif is_livemaker:
            project_type = "Live Maker"
        elif is_tyranobuilder:
            project_type = "TyranoBuilder"
        elif is_srpg_studio:
            project_type = "SRPG Studio"
        elif is_lune:
            project_type = "Lune"
        elif is_regex:
            project_type = "Regex"
        else:
            project_type = "RPG Maker"
        
        # Get model info for pricing
        model_info = self.model_db.get_model_info(model_name)
        if not model_info:
            raise ValueError(f"Unknown model: {model_name}")
        
        pricing = self.model_db.get_model_pricing(model_name)
        
        # Find files to process
        if is_lightnovel:
            files_to_process = self._find_lightnovel_files(input_dir)
        elif is_renpy:
            files_to_process = self.renpy_processor.find_rpy_files(input_dir)
        elif is_unity:
            files_to_process = self.unity_processor.find_unity_text_files(input_dir)
        elif is_wolf:
            files_to_process = self.wolf_processor.find_wolf_text_files(input_dir)
        elif is_kirikiri:
            files_to_process = self.kirikiri_processor.find_kirikiri_text_files(input_dir)
        elif is_nscripter:
            files_to_process = self.nscripter_processor.find_nscripter_text_files(input_dir)
        elif is_livemaker:
            files_to_process = self.livemaker_processor.find_livemaker_files(input_dir)
        elif is_tyranobuilder:
            files_to_process = self.tyranobuilder_processor.find_tyranobuilder_files(input_dir)
        elif is_srpg_studio:
            files_to_process = self.srpg_studio_processor.find_srpg_studio_files(input_dir)
        elif is_lune:
            files_to_process = self.lune_processor.find_lune_files(input_dir)
        elif is_regex:
            files_to_process = self.regex_processor.find_regex_files(input_dir)
        else:
            files_to_process = self._find_json_files(input_dir)
        
        # Analyze each file
        file_details: List[Dict[str, Any]] = []
        total_japanese_strings = 0
        total_input_tokens = 0
        total_output_tokens = 0
        translatable_files = 0
        
        for file_path in files_to_process:
            try:
                if is_lightnovel:
                    file_stats = self._get_lightnovel_file_stats(file_path)
                elif is_renpy:
                    file_stats = self.renpy_processor.get_file_stats(file_path)
                elif is_unity:
                    file_stats = self.unity_processor.get_file_stats(file_path)
                else:
                    file_stats = self.file_processor.get_file_stats(file_path)
                
                if file_stats.get('needs_translation', False):
                    translatable_files += 1
                    japanese_strings = file_stats.get('japanese_text_entries', 0) or file_stats.get('japanese_strings', 0)
                    estimated_tokens = file_stats.get('estimated_tokens', 0) or file_stats.get('input_tokens', 0)
                    
                    # Estimate input and output tokens
                    input_tokens = estimated_tokens
                    output_tokens = int(estimated_tokens * 1.2)  # Output usually slightly longer
                    
                    total_japanese_strings += japanese_strings
                    total_input_tokens += input_tokens
                    total_output_tokens += output_tokens
                    
                    rel_path = os.path.relpath(file_path, input_dir)
                    
                    file_details.append({
                        'file_path': file_path,
                        'relative_path': rel_path,
                        'japanese_strings': japanese_strings,
                        'estimated_input_tokens': input_tokens,
                        'estimated_output_tokens': output_tokens,
                        'file_size': file_stats.get('file_size', 0)
                    })
                    
            except Exception as e:
                # Log error but continue with other files
                print(f"Error analyzing {file_path}: {e}")
                continue
        
        # Sort files by token count (descending)
        file_details.sort(key=lambda x: x['estimated_input_tokens'] + x['estimated_output_tokens'], reverse=True)
        
        # Calculate costs
        input_cost = (total_input_tokens / 1000) * pricing['input_cost']
        output_cost = (total_output_tokens / 1000) * pricing['output_cost']
        total_cost = input_cost + output_cost
        
        # Estimate time requirements
        estimated_time = self._estimate_translation_time(
            total_input_tokens + total_output_tokens, 
            model_name, 
            translatable_files
        )
        
        return {
            'project_type': project_type,
            'model_name': model_name,
            'summary': {
                'total_files_found': len(files_to_process),
                'translatable_files': translatable_files,
                'total_japanese_strings': total_japanese_strings,
                'estimated_input_tokens': total_input_tokens,
                'estimated_output_tokens': total_output_tokens,
                'estimated_cost': {
                    'input_cost': input_cost,
                    'output_cost': output_cost,
                    'total_cost': total_cost
                },
                'estimated_time_minutes': estimated_time,
                'model_name': model_name,
                'pricing_per_1k': {
                    'input': pricing['input_cost'],
                    'output': pricing['output_cost']
                }
            },
            'file_details': file_details[:20],  # Top 20 files
            'model_info': {
                'provider': model_info.get('provider', 'Unknown'),
                'context_length': model_info.get('context_window', 0),
                'supports_caching': model_info.get('supports_caching', False)
            }
        }
    
    def _find_json_files(self, input_dir: str) -> List[str]:
        """Find JSON files for RPG Maker projects"""
        import glob
        
        json_files: List[str] = []
        
        # Common RPG Maker file patterns
        patterns = [
            "**/*.json",
            "**/Map*.json",
            "**/data/*.json"
        ]
        
        # Exclude system files that shouldn't be translated
        exclude_patterns = [
            "System.json",
            "Tilesets.json",
            "Animations.json",
            "States.json",
            "Skills.json",
            "Items.json",
            "Weapons.json",
            "Armors.json",
            "Enemies.json",
            "Troops.json",
            "Classes.json",
            "Actors.json"
        ]
        
        for pattern in patterns:
            search_path = os.path.join(input_dir, pattern)
            found_files = glob.glob(search_path, recursive=True)
            
            for file_path in found_files:
                filename = os.path.basename(file_path)
                
                # Skip excluded files
                if any(exclude in filename for exclude in exclude_patterns):
                    continue
                
                # Only add if not already in list
                if file_path not in json_files:
                    json_files.append(file_path)
        
        return sorted(json_files)
    
    def _estimate_translation_time(self, total_tokens: int, model_name: str, file_count: int) -> int:
        """Estimate translation time in minutes"""
        
        # Base processing speeds (tokens per minute)
        if 'gpt-4' in model_name.lower():
            tokens_per_minute = 800  # GPT-4 is slower but higher quality
        elif 'gpt-3.5' in model_name.lower():
            tokens_per_minute = 1500
        elif 'claude' in model_name.lower():
            tokens_per_minute = 1000
        elif 'gemini' in model_name.lower():
            tokens_per_minute = 1200
        elif 'grok' in model_name.lower():
            tokens_per_minute = 1000
        elif 'deepseek' in model_name.lower():
            tokens_per_minute = 1800
        else:
            tokens_per_minute = 1000  # Default conservative estimate
        
        # Base time calculation
        base_minutes = total_tokens / tokens_per_minute
        
        # Add overhead for:
        # - API rate limits
        # - Network latency
        # - Error handling and retries
        # - File processing overhead
        overhead_factor = 1.5
        
        # Add extra time for file count (setup overhead per file)
        file_overhead_seconds = file_count * 2  # 2 seconds per file
        file_overhead_minutes = file_overhead_seconds / 60
        
        total_minutes = (base_minutes * overhead_factor) + file_overhead_minutes
        
        return max(1, int(total_minutes))
    
    def get_quick_estimate(self, input_dir: str) -> Dict[str, Any]:
        """Get a quick estimate without detailed analysis"""
        
        # Detect project type
        is_renpy = self.renpy_processor.detect_renpy_project(input_dir)
        project_type = "Ren'Py" if is_renpy else "RPG Maker"
        
        # Quick file count
        if is_renpy:
            files = self.renpy_processor.find_rpy_files(input_dir)
        else:
            files = self._find_json_files(input_dir)
        
        # Very rough estimates
        estimated_strings = len(files) * 50  # Rough average
        estimated_tokens = estimated_strings * 20  # Rough token estimate
        
        return {
            'project_type': project_type,
            'total_files': len(files),
            'estimated_strings': estimated_strings,
            'estimated_tokens': estimated_tokens,
            'note': 'This is a quick estimate. Use full estimation for accurate results.'
        }
    
    def generate_estimate_report(self, estimate: Dict[str, Any]) -> str:
        """Generate a detailed text report from estimation results"""
        
        summary = estimate['summary']
        project_type = estimate['project_type']
        
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""
EROGE TRANSLATION TOOL - PROJECT ESTIMATION REPORT
{'=' * 60}

PROJECT INFORMATION:
  Type: {project_type}
  Model: {summary['model_name']}
  Analysis Date: {current_time}

FILE ANALYSIS:
  Total files found: {summary['total_files_found']:,}
  Files needing translation: {summary['translatable_files']:,}
  Japanese text entries: {summary['total_japanese_strings']:,}

TOKEN ESTIMATION:
  Input tokens: {summary['estimated_input_tokens']:,}
  Output tokens: {summary['estimated_output_tokens']:,}
  Total tokens: {summary['estimated_input_tokens'] + summary['estimated_output_tokens']:,}

COST ESTIMATION:
  Model pricing (per 1K tokens):
    Input: ${summary['pricing_per_1k']['input']:.4f}
    Output: ${summary['pricing_per_1k']['output']:.4f}
  
  Estimated costs:
    Input cost: ${summary['estimated_cost']['input_cost']:.4f}
    Output cost: ${summary['estimated_cost']['output_cost']:.4f}
    Total cost: ${summary['estimated_cost']['total_cost']:.4f}

TIME ESTIMATION:
  Estimated translation time: {summary['estimated_time_minutes']} minutes
  ({summary['estimated_time_minutes'] // 60}h {summary['estimated_time_minutes'] % 60}m)

MODEL INFORMATION:
  Provider: {estimate['model_info']['provider']}
  Context length: {estimate['model_info']['context_length']:,} tokens
  Supports caching: {estimate['model_info']['supports_caching']}

TOP FILES BY TOKEN COUNT:
"""
        
        # Add top files
        for i, file_detail in enumerate(estimate['file_details'][:10], 1):
            tokens = file_detail['estimated_input_tokens'] + file_detail['estimated_output_tokens']
            report += f"  {i:2}. {file_detail['relative_path']}\n"
            report += f"      Japanese strings: {file_detail['japanese_strings']:,}\n"
            report += f"      Estimated tokens: {tokens:,}\n\n"
        
        report += f"""
IMPORTANT NOTES:
• These are estimates based on analysis of text content
• Actual costs may vary based on:
  - Text complexity and context requirements
  - API pricing changes
  - Translation quality settings
  - Caching and optimization features
• Consider running a small test batch first
• Monitor API usage during translation

RECOMMENDATIONS:
• For large projects (>$10 cost), consider using cheaper models for initial pass
• Use GPT-4 or Claude for higher quality on important dialogue
• Enable API caching if available to reduce costs
• Process files in batches to manage costs
"""
        
        return report
    
    def _detect_lightnovel_project(self, input_dir: str) -> bool:
        """Detect if directory contains light novel files"""
        import glob
        
        light_novel_extensions = ['.txt', '.docx', '.pdf', '.epub']
        
        for ext in light_novel_extensions:
            pattern = os.path.join(input_dir, f"*{ext}")
            files = glob.glob(pattern)
            if files:
                # Check if any file can be processed
                for file_path in files:
                    if self.lightnovel_processor.can_process(file_path):
                        return True
        
        return False
    
    def _find_lightnovel_files(self, input_dir: str) -> List[str]:
        """Find light novel files in directory"""
        import glob
        
        light_novel_files = []
        light_novel_extensions = ['.txt', '.docx', '.pdf', '.epub']
        
        for ext in light_novel_extensions:
            pattern = os.path.join(input_dir, f"*{ext}")
            files = glob.glob(pattern)
            for file_path in files:
                if self.lightnovel_processor.can_process(file_path):
                    light_novel_files.append(file_path)
        
        return light_novel_files
    
    def _get_lightnovel_file_stats(self, file_path: str) -> Dict[str, Any]:
        """Get statistics for a light novel file"""
        try:
            # Extract text from file
            extracted_data = self.lightnovel_processor.extract_text(file_path)
            
            if "error" in extracted_data:
                return {
                    'japanese_strings': 0,
                    'input_tokens': 0,
                    'output_tokens': 0,
                    'needs_translation': False,
                    'error': extracted_data['error']
                }
            
            # Get translatable content
            translatable_content = self.lightnovel_processor.get_translatable_content(extracted_data)
            
            if not translatable_content:
                return {
                    'japanese_strings': 0,
                    'input_tokens': 0,
                    'output_tokens': 0,
                    'needs_translation': False
                }
            
            # Count tokens
            japanese_strings = len(translatable_content)
            total_chars = sum(len(item["original"]) for item in translatable_content)
            
            # Estimate tokens (rough approximation: 1 token ≈ 3-4 characters for Japanese)
            input_tokens = total_chars // 3
            # Output tokens are typically similar for translation
            output_tokens = input_tokens
            
            return {
                'japanese_strings': japanese_strings,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'needs_translation': japanese_strings > 0,
                'chapters': len(extracted_data.get("chapters", [])),
                'metadata': extracted_data.get("metadata", {})
            }
            
        except Exception as e:
            return {
                'japanese_strings': 0,
                'input_tokens': 0,
                'output_tokens': 0,
                'needs_translation': False,
                'error': str(e)
            }

    def estimate_lightnovel_cost(self, file_path: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate translation cost for a light novel file
        
        Args:
            file_path: Path to the light novel file
            config: Translation configuration
            
        Returns:
            Dictionary with cost estimation details
        """
        try:
            # Extract text from file
            extracted_data = self.lightnovel_processor.extract_text(file_path)
            
            if "error" in extracted_data:
                return {
                    'error': extracted_data['error'],
                    'file_name': os.path.basename(file_path),
                    'total_cost': 0,
                    'translatable_sections': 0
                }
            
            # Get translatable content
            translatable_content = self.lightnovel_processor.get_translatable_content(extracted_data)
            
            if not translatable_content:
                return {
                    'file_name': os.path.basename(file_path),
                    'format': extracted_data.get('metadata', {}).get('format', 'unknown'),
                    'file_size_mb': os.path.getsize(file_path) / (1024 * 1024),
                    'chapters': len(extracted_data.get('chapters', [])),
                    'translatable_sections': 0,
                    'total_characters': 0,
                    'japanese_characters': 0,
                    'input_tokens': 0,
                    'output_tokens': 0,
                    'total_cost': 0,
                    'estimated_minutes': 0,
                    'api_calls': 0,
                    'model': config.get('model', 'unknown'),
                    'use_specialized_prompt': config.get('lightnovel_use_specialized_prompt', True),
                    'use_specialized_vocab': config.get('lightnovel_use_specialized_vocab', True),
                    'eroge_mode': config.get('lightnovel_eroge_mode', False),
                    'enable_chunking': config.get('lightnovel_enable_chunking', True),
                    'chunk_size': config.get('lightnovel_chunk_size', 1500),
                    'output_format': config.get('lightnovel_output_format', 'same as input'),
                    'max_section_length': config.get('lightnovel_max_section_length', 5000)
                }
            
            # Detect eroge content
            sample_text = " ".join([item.get('original', '') for item in translatable_content[:5]])
            is_eroge = self.lightnovel_processor.detect_eroge_content(sample_text)
            eroge_mode = config.get('lightnovel_eroge_mode', False) or is_eroge
            
            # Count characters and prepare texts for translation
            total_characters = 0
            japanese_characters = 0
            texts_to_translate = []
            
            for item in translatable_content:
                text = item.get('original', '')
                total_characters += len(text)
                
                # Count Japanese characters
                import re
                japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]')
                japanese_chars = len(japanese_pattern.findall(text))
                japanese_characters += japanese_chars
                
                if japanese_chars > 0:  # Only translate texts with Japanese content
                    texts_to_translate.append(text)
            
            # Apply chunking if enabled
            enable_chunking = config.get('lightnovel_enable_chunking', True)
            chunk_size = config.get('lightnovel_chunk_size', 1500)
            overlap_tokens = config.get('lightnovel_overlap_tokens', 100)
            
            if enable_chunking:
                # Split large texts into chunks
                chunked_texts = []
                for text in texts_to_translate:
                    if len(text) > chunk_size * 4:  # Rough character to token ratio
                        chunks = self.lightnovel_processor.split_text_into_chunks(
                            text, chunk_size, overlap_tokens
                        )
                        chunked_texts.extend(chunks)
                    else:
                        chunked_texts.append(text)
                texts_to_process = chunked_texts
            else:
                texts_to_process = texts_to_translate
            
            # Get model information
            model_name = config.get('model', 'gpt-3.5-turbo')
            model_info = self.model_db.get_model(model_name)
            
            if not model_info:
                return {
                    'error': f'Unknown model: {model_name}',
                    'file_name': os.path.basename(file_path),
                    'total_cost': 0
                }
            
            # Get pricing information
            pricing = model_info.pricing
            
            # Estimate tokens using tiktoken if available, otherwise use approximation
            try:
                import tiktoken
                tokenizer = tiktoken.get_encoding("cl100k_base")
                
                def count_tokens(text):
                    return len(tokenizer.encode(text))
            except:
                # Fallback to character-based approximation
                def count_tokens(text):
                    return len(text) // 4  # Rough estimate for Japanese
            
            total_input_tokens = 0
            
            # Create specialized prompt
            prompt_text = self.lightnovel_processor.create_specialized_prompt("", eroge_mode)
            prompt_tokens = count_tokens(prompt_text)
            
            # Create specialized vocabulary 
            vocab_text = ""
            if config.get('lightnovel_use_specialized_vocab', True):
                vocab_text = self.lightnovel_processor.create_specialized_vocabulary(eroge_mode)
            vocab_tokens = count_tokens(vocab_text)
            
            # Calculate tokens for each text chunk
            for text in texts_to_process:
                text_tokens = count_tokens(text)
                request_tokens = text_tokens + prompt_tokens + vocab_tokens
                total_input_tokens += request_tokens
            
            # Estimate output tokens (assume 1.3x input for light novels, more for eroge content)
            output_multiplier = 1.4 if eroge_mode else 1.3
            total_output_tokens = int(total_input_tokens * output_multiplier)
            
            # Calculate costs
            input_cost_per_1m = pricing.input_cost
            output_cost_per_1m = pricing.output_cost
            
            input_cost = (total_input_tokens / 1_000_000) * input_cost_per_1m
            output_cost = (total_output_tokens / 1_000_000) * output_cost_per_1m
            total_cost = input_cost + output_cost
            
            # Estimate processing time and API calls
            api_calls = len(texts_to_process)
            # Add extra time for chunked texts (overlap processing)
            time_per_call = 0.7 if enable_chunking else 0.5
            estimated_minutes = api_calls * time_per_call
            
            # File information
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            metadata = extracted_data.get('metadata', {})
            
            return {
                'file_name': os.path.basename(file_path),
                'format': metadata.get('format', 'unknown'),
                'file_size_mb': file_size_mb,
                'chapters': len(extracted_data.get('chapters', [])),
                'translatable_sections': len(translatable_content),
                'sections_with_japanese': len(texts_to_translate),
                'chunks_after_processing': len(texts_to_process) if enable_chunking else len(texts_to_translate),
                'total_characters': total_characters,
                'japanese_characters': japanese_characters,
                'input_tokens': total_input_tokens,
                'output_tokens': total_output_tokens,
                'input_cost': input_cost,
                'output_cost': output_cost,
                'total_cost': total_cost,
                'estimated_minutes': estimated_minutes,
                'api_calls': api_calls,
                'model': model_name,
                'use_specialized_prompt': config.get('lightnovel_use_specialized_prompt', True),
                'use_specialized_vocab': config.get('lightnovel_use_specialized_vocab', True),
                'eroge_mode': eroge_mode,
                'eroge_detected': is_eroge,
                'enable_chunking': enable_chunking,
                'chunk_size': chunk_size,
                'overlap_tokens': overlap_tokens,
                'output_format': config.get('lightnovel_output_format', 'same as input'),
                'max_section_length': config.get('lightnovel_max_section_length', 5000),
                'content_warning': model_info.content_policy.value if model_info else "unknown"
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'file_name': os.path.basename(file_path),
                'total_cost': 0,
                'translatable_sections': 0
            }
