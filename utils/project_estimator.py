"""
Project Estimator for translation cost and time estimation
Supports RPG Maker, Ren'Py, Unity, Wolf RPG Editor, KiriKiri, and NScripter projects
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
        
        if is_renpy:
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
        if is_renpy:
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
                if is_renpy:
                    file_stats = self.renpy_processor.get_file_stats(file_path)
                elif is_unity:
                    file_stats = self.unity_processor.get_file_stats(file_path)
                else:
                    file_stats = self.file_processor.get_file_stats(file_path)
                
                if file_stats.get('needs_translation', False):
                    translatable_files += 1
                    japanese_strings = file_stats.get('japanese_text_entries', 0)
                    estimated_tokens = file_stats.get('estimated_tokens', 0)
                    
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
