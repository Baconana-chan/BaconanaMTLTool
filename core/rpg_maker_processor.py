"""
Enhanced RPG Maker MV/MZ Processor
Provides selective event code processing for optimized AI translation
"""

import json
import os
import re
from typing import Dict, List, Any, Set, Optional
from dataclasses import dataclass


@dataclass
class RPGMakerEventCode:
    """Represents an RPG Maker event code with metadata"""
    code: int
    name: str
    description: str
    category: str
    cost_level: str  # "low", "medium", "high"
    recommended: bool = False


class RPGMakerProcessor:
    """Enhanced processor for RPG Maker MV/MZ with selective event code processing"""
    
    def __init__(self):
        # Japanese text detection pattern
        self.japanese_pattern = re.compile(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]')
        
        # Define available event codes with metadata
        self.available_codes = {
            # Main Dialogue Codes (Recommended)
            401: RPGMakerEventCode(
                code=401, name="Show Text", description="Main dialogue text display",
                category="main_dialogue", cost_level="low", recommended=True
            ),
            405: RPGMakerEventCode(
                code=405, name="Show Text (Scrolling)", description="Scrolling text display",
                category="main_dialogue", cost_level="low", recommended=True
            ),
            102: RPGMakerEventCode(
                code=102, name="Show Choices", description="Player choice options",
                category="main_dialogue", cost_level="low", recommended=True
            ),
            
            # Optional Codes
            101: RPGMakerEventCode(
                code=101, name="Character Names", description="Character name display",
                category="optional", cost_level="low"
            ),
            408: RPGMakerEventCode(
                code=408, name="Comments", description="Developer comments (High translation cost!)",
                category="optional", cost_level="high"
            ),
            
            # Variable Codes
            122: RPGMakerEventCode(
                code=122, name="Control Variables", description="Variable control with text",
                category="variables", cost_level="medium"
            ),
            
            # Other Event Codes
            355: RPGMakerEventCode(
                code=355, name="Scripts", description="Script commands",
                category="other", cost_level="medium"
            ),
            357: RPGMakerEventCode(
                code=357, name="Picture Text", description="Text displayed on pictures",
                category="other", cost_level="medium"
            ),
            657: RPGMakerEventCode(
                code=657, name="Picture Text Extended", description="Extended picture text",
                category="other", cost_level="medium"
            ),
            356: RPGMakerEventCode(
                code=356, name="Plugin Commands", description="Plugin command text",
                category="other", cost_level="medium"
            ),
            320: RPGMakerEventCode(
                code=320, name="Change Name Input", description="Name input prompts",
                category="other", cost_level="low"
            ),
            324: RPGMakerEventCode(
                code=324, name="Change Nickname", description="Character nickname changes",
                category="other", cost_level="low"
            ),
            111: RPGMakerEventCode(
                code=111, name="Conditional Branch", description="Conditional branch text",
                category="other", cost_level="medium"
            ),
            108: RPGMakerEventCode(
                code=108, name="Comments", description="Comment text",
                category="other", cost_level="high"
            )
        }
        
        # Default enabled codes (recommended ones)
        self.enabled_codes = {401, 405, 102}  # Main dialogue codes only
        
        # Standard translatable fields for non-event data
        self.translatable_fields = {
            'name', 'nickname', 'description', 'message', 'note', 'text',
            'title', 'displayName', 'content', 'label', 'tooltip'
        }
    
    def get_code_categories(self) -> Dict[str, List[RPGMakerEventCode]]:
        """Get event codes grouped by category"""
        categories = {}
        for code_info in self.available_codes.values():
            if code_info.category not in categories:
                categories[code_info.category] = []
            categories[code_info.category].append(code_info)
        
        # Sort by code number within each category
        for category in categories:
            categories[category].sort(key=lambda x: x.code)
        
        return categories
    
    def get_recommended_codes(self) -> Set[int]:
        """Get list of recommended event codes"""
        return {code for code, info in self.available_codes.items() if info.recommended}
    
    def set_enabled_codes(self, codes: Set[int]):
        """Set which event codes should be processed"""
        # Validate that all codes are available
        invalid_codes = codes - set(self.available_codes.keys())
        if invalid_codes:
            raise ValueError(f"Invalid event codes: {invalid_codes}")
        
        self.enabled_codes = codes.copy()
    
    def get_enabled_codes(self) -> Set[int]:
        """Get currently enabled event codes"""
        return self.enabled_codes.copy()
    
    def get_code_info(self, code: int) -> Optional[RPGMakerEventCode]:
        """Get information about a specific event code"""
        return self.available_codes.get(code)
    
    def extract_text_from_file(self, file_path: str) -> List[str]:
        """Extract Japanese text from a single RPG Maker file"""
        texts = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._extract_text_recursive(data, texts)
            return texts
            
        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")
            return []

    def get_cost_estimation(self) -> Dict[str, Any]:
        """Get cost estimation for current enabled codes"""
        if not self.enabled_codes:
            return {
                'category': 'none',
                'description': 'No codes selected',
                'estimated_texts': 0,
                'cost_multiplier': 0.0
            }
        
        # Categorize codes by cost impact
        high_cost_codes = {320, 355, 117, 118, 108}  # Script, System, Transfer, Comments
        medium_cost_codes = {103, 104, 111, 122, 356}  # Advanced Conditional, System Settings
        low_cost_codes = {401, 405, 102, 324}  # Main dialogue, choices, nicknames
        
        enabled_high = self.enabled_codes & high_cost_codes
        enabled_medium = self.enabled_codes & medium_cost_codes
        enabled_low = self.enabled_codes & low_cost_codes
        
        # Determine cost category
        if enabled_high:
            category = 'high'
            multiplier = 1.0
            description = 'High cost: includes script/system codes'
        elif enabled_medium:
            category = 'medium'
            multiplier = 0.6
            description = 'Medium cost: includes choices/conditions'
        else:
            category = 'low'
            multiplier = 0.3
            description = 'Low cost: dialogue only'
        
        # Estimate text count
        base_estimate = len(self.enabled_codes) * 50  # Rough estimate
        
        return {
            'category': category,
            'description': description,
            'estimated_texts': base_estimate,
            'cost_multiplier': multiplier,
            'enabled_codes': list(self.enabled_codes),
            'high_cost_codes': list(enabled_high),
            'medium_cost_codes': list(enabled_medium),
            'low_cost_codes': list(enabled_low)
        }
    
    def is_rpg_maker_project(self, project_path: str) -> bool:
        """Check if the given path contains RPG Maker project files"""
        data_dir = os.path.join(project_path, "data")
        if not os.path.exists(data_dir):
            return False
        
        # Check for common RPG Maker files
        required_files = ["System.json"]
        rpg_maker_files = ["Map001.json", "CommonEvents.json", "Actors.json", "Classes.json"]
        
        # At least one required file must exist
        for req_file in required_files:
            if os.path.exists(os.path.join(data_dir, req_file)):
                return True
        
        # Or at least two RPG Maker files must exist
        found_files = 0
        for rpg_file in rpg_maker_files:
            if os.path.exists(os.path.join(data_dir, rpg_file)):
                found_files += 1
                if found_files >= 2:
                    return True
        
        return False

    def estimate_translation_cost(self, data: Any) -> Dict[str, Any]:
        """Estimate translation cost based on enabled codes"""
        costs = {"low": 0, "medium": 0, "high": 0}
        code_usage = {}
        
        def count_codes_recursive(obj):
            if isinstance(obj, dict):
                # Check for event lists
                if 'list' in obj and isinstance(obj['list'], list):
                    for event in obj['list']:
                        if isinstance(event, dict) and 'code' in event:
                            code = event.get('code', 0)
                            if code in self.enabled_codes and code in self.available_codes:
                                code_info = self.available_codes[code]
                                costs[code_info.cost_level] += 1
                                code_usage[code] = code_usage.get(code, 0) + 1
                
                # Recurse into nested objects
                for value in obj.values():
                    count_codes_recursive(value)
            
            elif isinstance(obj, list):
                for item in obj:
                    count_codes_recursive(item)
        
        count_codes_recursive(data)
        
        # Calculate estimated cost multipliers
        total_items = sum(costs.values())
        estimated_cost = costs["low"] * 1 + costs["medium"] * 2 + costs["high"] * 5
        
        return {
            "total_items": total_items,
            "cost_breakdown": costs,
            "estimated_cost_units": estimated_cost,
            "code_usage": code_usage,
            "enabled_codes": len(self.enabled_codes),
            "warning_high_cost": costs["high"] > 0
        }
    
    def extract_translatable_text(self, data: Any) -> List[str]:
        """Extract translatable text based on enabled event codes"""
        texts = []
        self._extract_text_recursive(data, texts)
        return texts
    
    def _extract_text_recursive(self, obj: Any, texts: List[str], path: str = "", seen_texts: Optional[Set[str]] = None):
        """Recursively extract translatable text without duplicates"""
        if seen_texts is None:
            seen_texts = set()
            
        if isinstance(obj, str):
            if self.japanese_pattern.search(obj) and obj not in seen_texts:
                texts.append(obj)
                seen_texts.add(obj)
        
        elif isinstance(obj, dict):
            # Handle event lists with selective code processing
            if 'list' in obj and isinstance(obj['list'], list):
                self._extract_from_event_list(obj['list'], texts, seen_texts)
            
            # Handle regular translatable fields
            for key, value in obj.items():
                if key.lower() in self.translatable_fields:
                    if isinstance(value, str) and self.japanese_pattern.search(value) and value not in seen_texts:
                        texts.append(value)
                        seen_texts.add(value)
                else:
                    current_path = f"{path}.{key}" if path else key
                    self._extract_text_recursive(value, texts, current_path, seen_texts)
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                current_path = f"{path}[{i}]" if path else f"[{i}]"
                self._extract_text_recursive(item, texts, current_path, seen_texts)
    
    def _extract_from_event_list(self, event_list: List[Dict[str, Any]], texts: List[str], seen_texts: Optional[Set[str]] = None):
        """Extract text from RPG Maker event command list using enabled codes only"""
        if seen_texts is None:
            seen_texts = set()
            
        for event in event_list:
            if not isinstance(event, dict):
                continue
            
            code = event.get('code', 0)
            parameters = event.get('parameters', [])
            
            # Only process enabled codes
            if code not in self.enabled_codes:
                continue
            
            # Handle different event command types
            if code in self.available_codes:
                for param in parameters:
                    if isinstance(param, str) and self.japanese_pattern.search(param):
                        # Avoid duplicates
                        if param not in seen_texts:
                            texts.append(param)
                            seen_texts.add(param)
                    elif isinstance(param, list):
                        # Handle nested parameter lists
                        for sub_param in param:
                            if isinstance(sub_param, str) and self.japanese_pattern.search(sub_param):
                                # Avoid duplicates
                                if sub_param not in seen_texts:
                                    texts.append(sub_param)
                                    seen_texts.add(sub_param)
    
    def apply_translations(self, data: Any, translations: Dict[str, str]) -> Any:
        """Apply translations back to the data structure"""
        return self._apply_translations_recursive(data, translations)
    
    def _apply_translations_recursive(self, obj: Any, translation_map: Dict[str, str]) -> Any:
        """Recursively apply translations to data structure"""
        if isinstance(obj, str):
            return translation_map.get(obj, obj)
        
        elif isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                if key == 'list' and isinstance(value, list):
                    # Handle event lists specially
                    result[key] = self._apply_translations_to_event_list(value, translation_map)
                elif key.lower() in self.translatable_fields and isinstance(value, str):
                    result[key] = translation_map.get(value, value)
                else:
                    result[key] = self._apply_translations_recursive(value, translation_map)
            return result
        
        elif isinstance(obj, list):
            return [self._apply_translations_recursive(item, translation_map) for item in obj]
        
        else:
            return obj
    
    def _apply_translations_to_event_list(self, event_list: List[Dict[str, Any]], 
                                         translation_map: Dict[str, str]) -> List[Dict[str, Any]]:
        """Apply translations to event list based on enabled codes"""
        result = []
        for event in event_list:
            if not isinstance(event, dict):
                result.append(event)
                continue
            
            code = event.get('code', 0)
            
            # Only translate enabled codes
            if code not in self.enabled_codes:
                result.append(event)
                continue
            
            # Apply translations to parameters
            new_event = event.copy()
            if 'parameters' in new_event:
                new_parameters = []
                for param in new_event['parameters']:
                    if isinstance(param, str):
                        new_parameters.append(translation_map.get(param, param))
                    elif isinstance(param, list):
                        new_param_list = []
                        for sub_param in param:
                            if isinstance(sub_param, str):
                                new_param_list.append(translation_map.get(sub_param, sub_param))
                            else:
                                new_param_list.append(sub_param)
                        new_parameters.append(new_param_list)
                    else:
                        new_parameters.append(param)
                new_event['parameters'] = new_parameters
            
            result.append(new_event)
        
        return result
    
    def get_code_info(self, code: int) -> Optional[RPGMakerEventCode]:
        """Get information about a specific event code"""
        return self.available_codes.get(code)
    
    def export_settings(self) -> Dict[str, Any]:
        """Export current processor settings"""
        return {
            "enabled_codes": list(self.enabled_codes),
            "version": "1.0"
        }
    
    def import_settings(self, settings: Dict[str, Any]):
        """Import processor settings"""
        if "enabled_codes" in settings:
            self.set_enabled_codes(set(settings["enabled_codes"]))
