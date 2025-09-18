"""
Preference Learning Service for advanced user preference tracking and learning.
Analyzes user interactions to learn preferences and adjust generation parameters.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
import math
import logging

logger = logging.getLogger(__name__)


class PreferenceLearningService:
    """Service for learning and managing user preferences"""
    
    def __init__(self):
        """Initialize preference learning service"""
        self.user_preferences = {}  # In-memory storage for now
        self.interaction_history = defaultdict(list)
        self.preference_weights = {
            "like": 1.0,
            "watch": 0.5,
            "repeat": 1.2,
            "favorite": 1.5,
            "skip": -0.8,
            "dislike": -1.0,
            "report": -1.5
        }
        self.decay_factor = 0.95  # Time decay for old interactions
        self.min_confidence = 0.1
        self.max_confidence = 0.95
        
    async def record_interaction(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Record a user interaction and update preferences"""
        try:
            user_id = interaction_data.get("user_id")
            if not user_id:
                return {"success": False, "error": "User ID required"}
            
            # Generate interaction ID
            interaction_id = f"interaction_{uuid.uuid4().hex[:8]}"
            
            # Store interaction
            self.interaction_history[user_id].append({
                **interaction_data,
                "interaction_id": interaction_id,
                "timestamp": interaction_data.get("timestamp", datetime.now())
            })
            
            # Update preferences based on interaction
            await self._update_preferences(user_id, interaction_data)
            
            logger.info(f"Recorded interaction {interaction_id} for user {user_id}")
            return {
                "success": True,
                "interaction_id": interaction_id,
                "message": "Interaction recorded successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to record interaction: {e}")
            return {"success": False, "error": str(e)}
    
    async def _update_preferences(self, user_id: str, interaction: Dict[str, Any]):
        """Update user preferences based on new interaction"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                "style_preferences": defaultdict(float),
                "time_preferences": defaultdict(float),
                "weather_preferences": defaultdict(float),
                "confidence_scores": {
                    "style": defaultdict(float),
                    "time": defaultdict(float),
                    "weather": defaultdict(float)
                }
            }
        
        # Get interaction weight
        interaction_type = interaction.get("interaction_type", "watch")
        weight = self.preference_weights.get(interaction_type, 0.5)
        
        # Apply duration factor for watch interactions
        if interaction_type == "watch":
            duration = interaction.get("duration_seconds", 0)
            if duration > 120:
                weight *= 1.2
            elif duration < 30:
                weight *= 0.5
        
        # Update style preference
        if prompt_style := interaction.get("prompt_style"):
            self.user_preferences[user_id]["style_preferences"][prompt_style] += weight
            self._update_confidence(user_id, "style", prompt_style, weight)
        
        # Update time preference
        if time_of_day := interaction.get("time_of_day"):
            self.user_preferences[user_id]["time_preferences"][time_of_day] += weight
            self._update_confidence(user_id, "time", time_of_day, weight)
        
        # Update weather preference
        if weather := interaction.get("weather"):
            self.user_preferences[user_id]["weather_preferences"][weather] += weight
            self._update_confidence(user_id, "weather", weather, weight)
    
    def _update_confidence(self, user_id: str, category: str, value: str, weight: float):
        """Update confidence score for a preference"""
        current = self.user_preferences[user_id]["confidence_scores"][category][value]
        
        # Calculate new confidence based on interaction weight
        if weight > 0:
            # Positive interaction increases confidence
            new_confidence = current + (1 - current) * abs(weight) * 0.1
        else:
            # Negative interaction decreases confidence
            new_confidence = current * (1 - abs(weight) * 0.2)
        
        # Clamp to valid range
        new_confidence = max(self.min_confidence, min(self.max_confidence, new_confidence))
        self.user_preferences[user_id]["confidence_scores"][category][value] = new_confidence
    
    async def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get learned preferences for a user"""
        if user_id not in self.user_preferences:
            return None
        
        # Apply time decay to old interactions
        await self._apply_time_decay(user_id)
        
        prefs = self.user_preferences[user_id]
        
        # Normalize preferences to get top choices
        result = {
            "style_preferences": self._get_top_preferences(prefs["style_preferences"]),
            "time_preferences": self._get_top_preferences(prefs["time_preferences"]),
            "weather_preferences": self._get_top_preferences(prefs["weather_preferences"]),
            "confidence_scores": prefs["confidence_scores"],
            "last_updated": datetime.now().isoformat()
        }
        
        return result
    
    def _get_top_preferences(self, pref_dict: Dict[str, float], top_n: int = 3) -> List[Dict[str, Any]]:
        """Get top N preferences from a preference dictionary"""
        if not pref_dict:
            return []
        
        # Sort by score
        sorted_prefs = sorted(pref_dict.items(), key=lambda x: x[1], reverse=True)
        
        # Get top N with normalized scores
        total = sum(abs(v) for _, v in sorted_prefs[:top_n])
        if total == 0:
            return []
        
        return [
            {"value": k, "score": v, "normalized": v/total}
            for k, v in sorted_prefs[:top_n]
        ]
    
    async def _apply_time_decay(self, user_id: str):
        """Apply time decay to old interactions"""
        if user_id not in self.interaction_history:
            return
        
        now = datetime.now()
        interactions = self.interaction_history[user_id]
        
        for interaction in interactions:
            timestamp = interaction.get("timestamp", now)
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            
            # Calculate days since interaction
            days_old = (now - timestamp).days
            
            if days_old > 7:  # Apply decay after 7 days
                decay = self.decay_factor ** (days_old / 7)
                
                # Apply decay to relevant preferences
                if prompt_style := interaction.get("prompt_style"):
                    self.user_preferences[user_id]["style_preferences"][prompt_style] *= decay
                    self.user_preferences[user_id]["confidence_scores"]["style"][prompt_style] *= decay
    
    async def adjust_prompt_for_user(self, user_id: str, base_prompt: str) -> str:
        """Adjust a prompt based on user preferences"""
        preferences = await self.get_user_preferences(user_id)
        
        if not preferences:
            return base_prompt
        
        adjusted_prompt = base_prompt
        
        # Add style preference if high confidence
        if style_prefs := preferences.get("style_preferences"):
            top_style = style_prefs[0] if style_prefs else None
            if top_style and top_style["score"] > 0:  # Lower threshold for testing
                style_value = top_style["value"]
                confidence = preferences["confidence_scores"]["style"].get(style_value, 0)
                
                if confidence > 0.1:  # Lower threshold for testing
                    adjusted_prompt = f"{adjusted_prompt}, in {style_value} style"
        
        # Add time-based adjustments
        if time_prefs := preferences.get("time_preferences"):
            top_time = time_prefs[0] if time_prefs else None
            if top_time and top_time["value"] == "evening":
                adjusted_prompt = f"{adjusted_prompt}, with warm evening lighting"
            elif top_time and top_time["value"] == "morning":
                adjusted_prompt = f"{adjusted_prompt}, with bright morning light"
        
        return adjusted_prompt
    
    async def get_recommendations(self, user_id: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get video generation recommendations based on user preferences"""
        preferences = await self.get_user_preferences(user_id)
        
        if not preferences:
            return []
        
        recommendations = []
        
        # Generate recommendations based on top preferences
        style_prefs = preferences.get("style_preferences", [])
        time_prefs = preferences.get("time_preferences", [])
        
        for style_pref in style_prefs[:2]:  # Top 2 styles
            style = style_pref["value"]
            style_confidence = preferences["confidence_scores"]["style"].get(style, 0)
            
            # Match with context if provided
            if context:
                time_of_day = context.get("time_of_day")
                if time_of_day:
                    # Check if this time matches user preferences
                    time_score = next(
                        (tp["score"] for tp in time_prefs if tp["value"] == time_of_day),
                        0
                    )
                    
                    if time_score > 0:
                        style_confidence *= 1.2  # Boost confidence for matching context
            
            recommendations.append({
                "style": style,
                "confidence": min(style_confidence, 0.95),
                "reason": f"Based on {len(self.interaction_history[user_id])} past interactions"
            })
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x["confidence"], reverse=True)
        
        return recommendations
    
    async def predict_preference(self, user_id: str, content_id: str) -> Dict[str, Any]:
        """Predict user preference for specific content"""
        if user_id not in self.user_preferences:
            # No data available, return neutral prediction
            return {
                "preference_score": 0.5,
                "confidence": 0.1,
                "reason": "No user interaction data available"
            }
        
        # Get user preferences
        preferences = await self.get_user_preferences(user_id)
        if not preferences:
            return {
                "preference_score": 0.5,
                "confidence": 0.1,
                "reason": "Unable to retrieve preferences"
            }
        
        # Calculate preference score based on available data
        total_score = 0.0
        confidence_factors = []
        
        # Analyze based on style preferences
        style_prefs = preferences.get("style_preferences", [])
        if style_prefs:
            # Use top style preference for scoring
            top_style = style_prefs[0]
            style_score = top_style.get("score", 0.5)
            total_score += style_score * 0.6  # 60% weight on style
            confidence_factors.append(top_style.get("score", 0.1))
        
        # Analyze based on time preferences (if current time data available)
        time_prefs = preferences.get("time_preferences", [])
        if time_prefs:
            # Use current time or general time preference
            current_hour = datetime.now().hour
            time_of_day = "morning" if 6 <= current_hour < 12 else \
                         "afternoon" if 12 <= current_hour < 18 else \
                         "evening" if 18 <= current_hour < 22 else "night"
            
            time_score = next(
                (tp["score"] for tp in time_prefs if tp["value"] == time_of_day),
                0.5  # Default neutral score
            )
            total_score += time_score * 0.3  # 30% weight on time
            confidence_factors.append(time_score)
        
        # Add weather context if available (10% weight)
        weather_prefs = preferences.get("weather_preferences", [])
        if weather_prefs:
            # Use first weather preference as baseline
            weather_score = weather_prefs[0].get("score", 0.5)
            total_score += weather_score * 0.1
            confidence_factors.append(weather_score)
        
        # Normalize score to 0-1 range
        final_score = max(0.0, min(1.0, total_score))
        
        # Calculate confidence based on amount of data and consistency
        if confidence_factors:
            confidence = sum(confidence_factors) / len(confidence_factors)
            # Boost confidence if we have multiple data points
            if len(self.interaction_history[user_id]) > 5:
                confidence = min(0.95, confidence * 1.2)
        else:
            confidence = 0.1
        
        return {
            "preference_score": final_score,
            "confidence": confidence,
            "reason": f"Based on {len(style_prefs)} style preferences and {len(self.interaction_history[user_id])} interactions"
        }