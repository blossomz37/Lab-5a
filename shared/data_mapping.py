"""
Data mapping utilities based on data_map.yaml
Provides field specifications, display rules, and data transformations
"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class FieldType(Enum):
    """Field display types"""
    DISPLAY = "Display"
    HYPERLINK = "Hyperlink" 
    DISPLAY_IMAGE = "Display Image"
    SEARCHABLE = "Searchable"
    IGNORE = "Ignore"

@dataclass
class FieldSpec:
    """Field specification from data mapping"""
    field_name: str
    display_name: str
    field_type: FieldType
    description: Optional[str] = None
    format_rule: Optional[str] = None

class DataMapper:
    """Data mapping utility class"""
    
    def __init__(self, yaml_path: Optional[str] = None):
        """Initialize with data mapping YAML file"""
        if yaml_path is None:
            # Default to data_map.yaml in project root
            project_root = Path(__file__).parent.parent
            yaml_path = project_root / "data_map.yaml"
        
        self.yaml_path = Path(yaml_path)
        self.mapping = self._load_mapping()
        self.genre_mapping = self._extract_genre_mapping()
        self.field_specs = self._extract_field_specs()
    
    def _load_mapping(self) -> Dict[str, Any]:
        """Load YAML mapping file"""
        try:
            with open(self.yaml_path, 'r') as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            print(f"Warning: Data mapping file not found: {self.yaml_path}")
            return {}
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
            return {}
    
    def _extract_genre_mapping(self) -> Dict[str, str]:
        """Extract genre code to display name mapping"""
        return self.mapping.get('genres', {})
    
    def _extract_field_specs(self) -> Dict[str, FieldSpec]:
        """Extract field specifications from YAML"""
        field_specs = {}
        fields_config = self.mapping.get('fields', {})
        
        # Map display_type strings to FieldType enums
        type_mapping = {
            'display': FieldType.DISPLAY,
            'hyperlink': FieldType.HYPERLINK,
            'image': FieldType.DISPLAY_IMAGE,
            'ignore': FieldType.IGNORE,
            'hyperlink_source': FieldType.IGNORE  # Used by other fields
        }
        
        for field_name, config in fields_config.items():
            if isinstance(config, dict):
                display_type = config.get('display_type', 'display')
                field_type = type_mapping.get(display_type, FieldType.DISPLAY)
                
                field_specs[field_name] = FieldSpec(
                    field_name=field_name,
                    display_name=config.get('display_name', field_name),
                    field_type=field_type,
                    description=config.get('format', None)
                )
        
        return field_specs
    
    def get_genre_display_name(self, genre_code: str) -> str:
        """Get display name for genre code"""
        return self.genre_mapping.get(genre_code, genre_code.replace('_', ' ').title())
    
    def get_field_spec(self, field_name: str) -> Optional[FieldSpec]:
        """Get field specification for given field"""
        return self.field_specs.get(field_name)
    
    def get_display_fields(self) -> List[FieldSpec]:
        """Get all fields that should be displayed"""
        return [spec for spec in self.field_specs.values() 
                if spec.field_type in [FieldType.DISPLAY, FieldType.HYPERLINK, FieldType.DISPLAY_IMAGE]]
    
    def get_searchable_fields(self) -> List[str]:
        """Get fields that should be searchable"""
        # Based on data_map.yaml, these are the key searchable fields
        return ['Title', 'Author', 'Series', 'blurbText', 'topicTags', 'subcatsList']
    
    def format_field_value(self, field_name: str, value: Any) -> str:
        """Format field value according to mapping rules"""
        if value is None or value == '':
            return 'N/A'
        
        spec = self.get_field_spec(field_name)
        if not spec:
            return str(value)
        
        # Apply specific formatting rules
        if field_name == 'price':
            try:
                return f"${float(value):.2f}"
            except (ValueError, TypeError):
                return str(value)
        
        elif field_name == 'reviewAverage':
            try:
                rating = float(value)
                stars = "⭐" * int(rating)
                return f"{stars} {rating:.1f}"
            except (ValueError, TypeError):
                return str(value)
        
        elif field_name == 'nReviews':
            try:
                return f"{int(value):,}"
            except (ValueError, TypeError):
                return str(value)
        
        elif field_name == 'releaseDate':
            # Keep as-is for now, could add date parsing later
            return str(value)
        
        elif field_name == 'isTrad':
            if isinstance(value, bool):
                return "Yes" if value else "No"
            return str(value)
        
        elif field_name == 'isFree':
            if isinstance(value, bool):
                return "Free" if value else "Paid"
            return str(value)
        
        elif field_name in ['topicTags', 'subcatsList']:
            # Handle pipe and hash separated lists
            if isinstance(value, str):
                if '|' in value:
                    items = [item.strip() for item in value.split('|') if item.strip()]
                    return ', '.join(items)
                elif '#' in value:
                    items = [item.strip() for item in value.split('#') if item.strip()]
                    return ', '.join(items)
            return str(value)
        
        return str(value)
    
    def extract_author_info(self, author_text: str) -> Tuple[str, Optional[str], Optional[str]]:
        """Extract author name, URL, and ISBN from markdown format"""
        if not author_text:
            return "Unknown Author", None, None
        
        # Pattern for [Name](URL)
        markdown_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        match = re.search(markdown_pattern, author_text)
        
        if match:
            author_name = match.group(1)
            author_url = match.group(2)
            
            # Extract ISBN from URL if present
            isbn_match = re.search(r'/([A-Z0-9]{10,})/?$', author_url)
            isbn = isbn_match.group(1) if isbn_match else None
            
            return author_name, author_url, isbn
        else:
            return author_text, None, None
    
    def get_enhanced_book_data(self, book_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance book data with mapping transformations"""
        enhanced = book_data.copy()
        
        # Apply genre mapping
        if 'genre' in enhanced:
            enhanced['genre_display'] = self.get_genre_display_name(enhanced['genre'])
        
        # Extract author information
        if 'Author' in enhanced:
            name, url, isbn = self.extract_author_info(enhanced['Author'])
            enhanced['author_name'] = name
            enhanced['author_url'] = url
            enhanced['author_isbn'] = isbn
        
        # Format specific fields (create list first to avoid iteration error)
        items_to_format = list(enhanced.items())
        for field_name, value in items_to_format:
            if field_name in self.field_specs:
                enhanced[f'{field_name}_formatted'] = self.format_field_value(field_name, value)
        
        return enhanced
    
    def get_card_display_config(self) -> Dict[str, Any]:
        """Get configuration for book card display"""
        card_config = self.mapping.get('card_display', {})
        
        # Return configured display or defaults
        return {
            'primary_fields': card_config.get('primary_fields', ['Title', 'Author', 'reviewAverage', 'nReviews', 'price']),
            'secondary_fields': card_config.get('secondary_fields', ['Series', 'nPages', 'releaseDate', 'publisher']),
            'expandable_fields': card_config.get('expandable_fields', ['blurbText', 'topicTags', 'subcatsList'])
        }

# Global instance
_data_mapper: Optional[DataMapper] = None

def get_data_mapper() -> DataMapper:
    """Get global data mapper instance"""
    global _data_mapper
    if _data_mapper is None:
        _data_mapper = DataMapper()
    return _data_mapper