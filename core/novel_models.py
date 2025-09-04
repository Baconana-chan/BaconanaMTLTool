"""
Novel Writing System - Models for characters, stories, and writing sessions
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


@dataclass
class Character:
    """Character data model"""
    id: str
    name: str
    style: str  # japanese, korean, chinese, fantasy, western, etc.
    age: Optional[str] = None
    gender: str = "unknown"
    personality: str = ""
    appearance: str = ""
    background: str = ""
    occupation: str = ""
    relationships: Dict[str, str] = None  # character_id -> relationship type
    speech_pattern: str = ""
    goals: str = ""
    fears: str = ""
    custom_fields: Dict[str, str] = None  # user-defined fields
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if self.relationships is None:
            self.relationships = {}
        if self.custom_fields is None:
            self.custom_fields = {}
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()


@dataclass
class Scene:
    """Scene data model"""
    id: str
    title: str
    content: str
    characters: List[str]  # character IDs involved in this scene
    location: str = ""
    mood: str = ""
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()


@dataclass
class Project:
    """Novel project data model"""
    id: str
    title: str
    description: str
    genre: str = ""
    style: str = "japanese"  # overall style preference
    target_length: str = "short"  # short, medium, long
    characters: List[str] = None  # character IDs
    scenes: List[str] = None  # scene IDs
    outline: str = ""
    themes: List[str] = None
    world_building: str = ""
    writing_style: str = ""  # formal, casual, poetic, etc.
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if self.characters is None:
            self.characters = []
        if self.scenes is None:
            self.scenes = []
        if self.themes is None:
            self.themes = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()


@dataclass
class WritingSession:
    """Writing session for context and continuity"""
    id: str
    project_id: str
    context: str  # current story context
    key_points: List[str]  # important plot points to remember
    active_characters: List[str]  # characters currently active in the scene
    current_location: str = ""
    current_mood: str = ""
    word_count: int = 0
    goals: str = ""  # what to accomplish in this session
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class NovelDatabase:
    """Database for managing novel writing data"""
    
    def __init__(self, data_dir: str = "novel_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize subdirectories
        (self.data_dir / "characters").mkdir(exist_ok=True)
        (self.data_dir / "projects").mkdir(exist_ok=True)
        (self.data_dir / "scenes").mkdir(exist_ok=True)
        (self.data_dir / "sessions").mkdir(exist_ok=True)
        
        # Character style templates
        self.character_styles = {
            "japanese": {
                "name_patterns": ["Japanese names", "honorifics (san, chan, kun)"],
                "personality_traits": ["polite", "reserved", "group-oriented", "respectful"],
                "appearance_features": ["anime/manga style", "school uniforms", "traditional clothing"],
                "speech_patterns": ["formal/informal levels", "honorifics", "indirect communication"]
            },
            "korean": {
                "name_patterns": ["Korean names", "honorifics (oppa, unnie, hyung, noona)"],
                "personality_traits": ["family-oriented", "hardworking", "respectful to elders"],
                "appearance_features": ["K-drama style", "modern fashion", "neat appearance"],
                "speech_patterns": ["age-based honorifics", "formal speech levels"]
            },
            "chinese": {
                "name_patterns": ["Chinese names", "titles and ranks"],
                "personality_traits": ["traditional values", "filial piety", "wisdom-seeking"],
                "appearance_features": ["traditional robes", "martial arts attire", "elegant styling"],
                "speech_patterns": ["poetic language", "proverbs", "formal address"]
            },
            "fantasy": {
                "name_patterns": ["fantasy names", "titles (Lord, Lady, Sir)"],
                "personality_traits": ["brave", "magical", "adventurous", "noble"],
                "appearance_features": ["magical elements", "medieval clothing", "unique features"],
                "speech_patterns": ["archaic language", "formal speech", "magical terminology"]
            },
            "western": {
                "name_patterns": ["Western names", "casual address"],
                "personality_traits": ["independent", "direct", "individualistic"],
                "appearance_features": ["modern clothing", "realistic proportions"],
                "speech_patterns": ["casual conversation", "slang", "direct communication"]
            }
        }
        
        # Writing prompts for different scenarios
        self.writing_prompts = {
            "character_introduction": "Introduce this character in a compelling way that shows their personality through actions and dialogue.",
            "dialogue_scene": "Write a dialogue scene between these characters that advances the plot and reveals character dynamics.",
            "action_sequence": "Write an action sequence that maintains tension while showing character reactions and growth.",
            "emotional_moment": "Write an emotional scene that explores the characters' inner feelings and motivations.",
            "world_building": "Describe this location or world element in a way that immerse the reader and supports the story.",
            "plot_advancement": "Continue the story in a way that moves the plot forward while maintaining character consistency."
        }

    def save_character(self, character: Character) -> bool:
        """Save character to database"""
        try:
            file_path = self.data_dir / "characters" / f"{character.id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(character), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving character: {e}")
            return False

    def load_character(self, character_id: str) -> Optional[Character]:
        """Load character from database"""
        try:
            file_path = self.data_dir / "characters" / f"{character_id}.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return Character(**data)
        except Exception as e:
            print(f"Error loading character: {e}")
        return None

    def get_all_characters(self) -> List[Character]:
        """Get all characters from database"""
        characters = []
        characters_dir = self.data_dir / "characters"
        for file_path in characters_dir.glob("*.json"):
            character = self.load_character(file_path.stem)
            if character:
                characters.append(character)
        return characters

    def save_project(self, project: Project) -> bool:
        """Save project to database"""
        try:
            file_path = self.data_dir / "projects" / f"{project.id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(project), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving project: {e}")
            return False

    def load_project(self, project_id: str) -> Optional[Project]:
        """Load project from database"""
        try:
            file_path = self.data_dir / "projects" / f"{project_id}.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return Project(**data)
        except Exception as e:
            print(f"Error loading project: {e}")
        return None

    def get_all_projects(self) -> List[Project]:
        """Get all projects from database"""
        projects = []
        projects_dir = self.data_dir / "projects"
        for file_path in projects_dir.glob("*.json"):
            project = self.load_project(file_path.stem)
            if project:
                projects.append(project)
        return projects

    def save_scene(self, scene: Scene) -> bool:
        """Save scene to database"""
        try:
            file_path = self.data_dir / "scenes" / f"{scene.id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(scene), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving scene: {e}")
            return False

    def load_scene(self, scene_id: str) -> Optional[Scene]:
        """Load scene from database"""
        try:
            file_path = self.data_dir / "scenes" / f"{scene_id}.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return Scene(**data)
        except Exception as e:
            print(f"Error loading scene: {e}")
        return None

    def save_writing_session(self, session: WritingSession) -> bool:
        """Save writing session to database"""
        try:
            file_path = self.data_dir / "sessions" / f"{session.id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(session), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving writing session: {e}")
            return False

    def load_writing_session(self, session_id: str) -> Optional[WritingSession]:
        """Load writing session from database"""
        try:
            file_path = self.data_dir / "sessions" / f"{session_id}.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return WritingSession(**data)
        except Exception as e:
            print(f"Error loading writing session: {e}")
        return None

    def delete_character(self, character_id: str) -> bool:
        """Delete character from database"""
        try:
            file_path = self.data_dir / "characters" / f"{character_id}.json"
            if file_path.exists():
                file_path.unlink()
                return True
        except Exception as e:
            print(f"Error deleting character: {e}")
        return False

    def delete_project(self, project_id: str) -> bool:
        """Delete project from database"""
        try:
            file_path = self.data_dir / "projects" / f"{project_id}.json"
            if file_path.exists():
                file_path.unlink()
                return True
        except Exception as e:
            print(f"Error deleting project: {e}")
        return False
