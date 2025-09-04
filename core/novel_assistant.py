"""
Novel Writing AI Assistant - Specialized AI client for creative writing
"""

import logging
from typing import Dict, List, Optional, Any
from .novel_models import Character, Project, Scene, WritingSession, NovelDatabase
from .api_client import APIClient


class NovelWritingAssistant:
    """AI assistant specialized for novel writing"""
    
    def __init__(self, config_manager, novel_db: NovelDatabase):
        self.config_manager = config_manager
        self.novel_db = novel_db
        self.logger = logging.getLogger(__name__)
        
        # Base prompts for different writing tasks
        self.base_prompts = {
            "character_generation": """You are a character creation expert. Create a detailed character based on the given style and parameters.

Style: {style}
Guidelines for {style} characters:
{style_guidelines}

Requirements:
- Name should fit the {style} style
- Personality should be multi-dimensional and interesting
- Appearance should be vivid but not overly detailed
- Background should provide motivation and depth
- Speech pattern should reflect personality and culture
- Include both strengths and flaws

Generate a character with these details. Be creative but consistent with the style.""",

            "scene_writing": """You are a skilled {style} novelist. Write a scene based on the given context and requirements.

Project Context:
Title: {project_title}
Genre: {genre}
Style: {writing_style}
Current Context: {context}

Scene Requirements:
{scene_requirements}

Characters in this scene:
{character_info}

Key points to remember:
{key_points}

Write a compelling scene that:
1. Advances the plot naturally
2. Stays true to character personalities
3. Maintains the established tone and style
4. Shows character growth or reveals new information
5. Engages the reader emotionally

Scene:""",

            "dialogue_writing": """You are an expert at writing natural, engaging dialogue in the {style} style.

Characters in this conversation:
{character_info}

Context: {context}
Situation: {situation}
Goal: {dialogue_goal}

Guidelines:
- Each character should have a distinct voice
- Dialogue should sound natural for the {style} style
- Include appropriate body language and actions
- Advance the plot or develop relationships
- Show personality through word choice and speech patterns

Write the dialogue:""",

            "story_continuation": """You are continuing a {style} story. Maintain consistency with the established world and characters.

Story Context:
{context}

Recent events:
{recent_events}

Characters currently active:
{active_characters}

Key plot points to remember:
{key_points}

Current goal: {current_goal}

Continue the story in a way that:
1. Flows naturally from the previous content
2. Maintains character consistency
3. Advances toward the current goal
4. Stays true to the established tone and style
5. Keeps the reader engaged

Continuation:""",

            "world_building": """You are a world-building expert for {style} stories. Develop the requested world element.

World Type: {style}
Project: {project_title}
Existing World Info: {world_info}

Request: {world_request}

Create detailed, immersive world-building that:
1. Fits the {style} aesthetic and cultural context
2. Supports the story themes and plot
3. Feels authentic and lived-in
4. Provides opportunities for character interaction
5. Enhances the reader's experience

World Element:""",

            "character_dialogue": """Write dialogue for {character_name} in this situation.

Character Profile:
Name: {character_name}
Personality: {personality}
Speech Pattern: {speech_pattern}
Current Mood: {mood}

Situation: {situation}
Other Characters Present: {other_characters}

The dialogue should:
1. Sound authentic to this character
2. Reflect their current emotional state
3. Fit the situation appropriately
4. Show their personality clearly
5. Advance the scene naturally

{character_name}'s dialogue:"""
        }

    def generate_character(self, style: str, requirements: Dict[str, Any]) -> Dict[str, str]:
        """Generate a character using AI based on style and requirements"""
        try:
            # Get style guidelines
            style_info = self.novel_db.character_styles.get(style, {})
            style_guidelines = self._format_style_guidelines(style_info)
            
            # Prepare prompt
            prompt = self.base_prompts["character_generation"].format(
                style=style,
                style_guidelines=style_guidelines
            )
            
            # Add specific requirements
            if requirements:
                prompt += f"\n\nSpecific requirements:\n"
                for key, value in requirements.items():
                    if value:
                        prompt += f"- {key}: {value}\n"
            
            # Get AI response
            api_client = APIClient(self.config_manager.get_config())
            response = api_client.get_completion(prompt, max_tokens=800)
            
            # Parse response into character fields
            return self._parse_character_response(response)
            
        except Exception as e:
            self.logger.error(f"Error generating character: {e}")
            return {}

    def write_scene(self, project: Project, session: WritingSession, 
                   scene_requirements: str, characters: List[Character]) -> str:
        """Write a scene using AI based on project context"""
        try:
            # Prepare character information
            character_info = self._format_character_info(characters)
            
            # Prepare prompt
            prompt = self.base_prompts["scene_writing"].format(
                style=project.style,
                project_title=project.title,
                genre=project.genre,
                writing_style=project.writing_style,
                context=session.context,
                scene_requirements=scene_requirements,
                character_info=character_info,
                key_points="\n".join(session.key_points)
            )
            
            # Get AI response
            api_client = APIClient(self.config_manager.get_config())
            response = api_client.get_completion(prompt, max_tokens=1200)
            
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Error writing scene: {e}")
            return ""

    def write_dialogue(self, characters: List[Character], context: str, 
                      situation: str, goal: str, style: str) -> str:
        """Write dialogue between characters"""
        try:
            character_info = self._format_character_info(characters)
            
            prompt = self.base_prompts["dialogue_writing"].format(
                style=style,
                character_info=character_info,
                context=context,
                situation=situation,
                dialogue_goal=goal
            )
            
            api_client = APIClient(self.config_manager.get_config())
            response = api_client.get_completion(prompt, max_tokens=800)
            
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Error writing dialogue: {e}")
            return ""

    def continue_story(self, project: Project, session: WritingSession,
                      recent_events: str, current_goal: str) -> str:
        """Continue the story based on current context"""
        try:
            # Get active characters
            active_chars = []
            for char_id in session.active_characters:
                char = self.novel_db.load_character(char_id)
                if char:
                    active_chars.append(char)
            
            active_character_info = self._format_character_info(active_chars)
            
            prompt = self.base_prompts["story_continuation"].format(
                style=project.style,
                context=session.context,
                recent_events=recent_events,
                active_characters=active_character_info,
                key_points="\n".join(session.key_points),
                current_goal=current_goal
            )
            
            api_client = APIClient(self.config_manager.get_config())
            response = api_client.get_completion(prompt, max_tokens=1000)
            
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Error continuing story: {e}")
            return ""

    def expand_world_building(self, project: Project, world_request: str) -> str:
        """Generate world-building content"""
        try:
            prompt = self.base_prompts["world_building"].format(
                style=project.style,
                project_title=project.title,
                world_info=project.world_building,
                world_request=world_request
            )
            
            api_client = APIClient(self.config_manager.get_config())
            response = api_client.get_completion(prompt, max_tokens=800)
            
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Error expanding world building: {e}")
            return ""

    def generate_character_dialogue(self, character: Character, situation: str,
                                   other_characters: List[str], mood: str = "") -> str:
        """Generate dialogue for a specific character"""
        try:
            prompt = self.base_prompts["character_dialogue"].format(
                character_name=character.name,
                personality=character.personality,
                speech_pattern=character.speech_pattern,
                mood=mood or "neutral",
                situation=situation,
                other_characters=", ".join(other_characters) if other_characters else "none"
            )
            
            api_client = APIClient(self.config_manager.get_config())
            response = api_client.get_completion(prompt, max_tokens=400)
            
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Error generating character dialogue: {e}")
            return ""

    def _format_style_guidelines(self, style_info: Dict[str, List[str]]) -> str:
        """Format style guidelines for prompts"""
        if not style_info:
            return "General guidelines: Create a well-rounded, interesting character."
        
        guidelines = []
        for category, items in style_info.items():
            guidelines.append(f"{category.replace('_', ' ').title()}: {', '.join(items)}")
        
        return "\n".join(guidelines)

    def _format_character_info(self, characters: List[Character]) -> str:
        """Format character information for prompts"""
        if not characters:
            return "No characters specified."
        
        char_info = []
        for char in characters:
            info = f"**{char.name}**: {char.personality}"
            if char.speech_pattern:
                info += f" (Speech: {char.speech_pattern})"
            if char.background:
                info += f" (Background: {char.background[:100]}...)"
            char_info.append(info)
        
        return "\n".join(char_info)

    def _parse_character_response(self, response: str) -> Dict[str, str]:
        """Parse AI response into character fields"""
        # This is a simple parser - could be made more sophisticated
        fields = {
            "name": "",
            "personality": "",
            "appearance": "",
            "background": "",
            "speech_pattern": "",
            "occupation": "",
            "goals": "",
            "fears": ""
        }
        
        lines = response.split('\n')
        current_field = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line starts a new field
            field_found = False
            for field in fields.keys():
                if line.lower().startswith(field.replace('_', ' ')) or line.lower().startswith(field):
                    if current_field and current_content:
                        fields[current_field] = ' '.join(current_content).strip()
                    current_field = field
                    current_content = [line.split(':', 1)[-1].strip()]
                    field_found = True
                    break
            
            if not field_found and current_field:
                current_content.append(line)
        
        # Save the last field
        if current_field and current_content:
            fields[current_field] = ' '.join(current_content).strip()
        
        # If parsing failed, put everything in personality
        if not any(fields.values()):
            fields["personality"] = response.strip()
        
        return fields
