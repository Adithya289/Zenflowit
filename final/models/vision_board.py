from utils.db import (
    get_vision_board_categories,
    get_user_vision_board_theme,
    update_vision_board_theme,
    get_vision_board_tiles,
    add_vision_board_tile,
    update_vision_board_tile,
    delete_vision_board_tile,
    update_tile_positions
)
from models.rewards import Reward

class VisionBoard:
    """Vision Board model for handling vision board operations"""
    
    @staticmethod
    def get_all_categories():
        """Get all available vision board categories"""
        return get_vision_board_categories()
    
    @staticmethod
    def get_user_theme(user_id):
        """Get a user's vision board theme"""
        return get_user_vision_board_theme(user_id)
    
    @staticmethod
    def update_theme(user_id, theme):
        """Update a user's vision board theme"""
        return update_vision_board_theme(user_id, theme)
    
    @staticmethod
    def get_tiles(user_id, category_id=None):
        """Get all vision board tiles for a user, optionally filtered by category"""
        return get_vision_board_tiles(user_id, category_id)
    
    @staticmethod
    def add_tile(user_id, title, description=None, image_path=None, 
                 image_url=None, is_affirmation=False, category_id=None):
        """Add a new vision board tile"""
        tile_id = add_vision_board_tile(
            user_id, title, description, image_path, 
            image_url, is_affirmation, category_id
        )
        
        # Check if this is the user's first vision board tile and award the badge
        if tile_id:
            existing_tiles = get_vision_board_tiles(user_id)
            if existing_tiles and len(existing_tiles) == 1:  # Only one tile means this is the first one
                # Award the Vision Creator badge
                success, newly_earned = Reward.check_and_award_reward(user_id, 'vision_board_created', 1)
                return tile_id, newly_earned
        
        return tile_id, []
    
    @staticmethod
    def update_tile(tile_id, user_id, title=None, description=None, 
                    image_path=None, image_url=None, is_affirmation=None, category_id=None):
        """Update an existing vision board tile"""
        return update_vision_board_tile(
            tile_id, user_id, title, description, 
            image_path, image_url, is_affirmation, category_id
        )
    
    @staticmethod
    def delete_tile(tile_id, user_id):
        """Delete a vision board tile"""
        return delete_vision_board_tile(tile_id, user_id)
    
    @staticmethod
    def reorder_tiles(positions_dict, user_id):
        """Update positions of multiple tiles at once"""
        return update_tile_positions(positions_dict, user_id)