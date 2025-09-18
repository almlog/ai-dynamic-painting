"""
Context Optimization Service for intelligent context-based generation optimization.
Analyzes environmental, temporal, and user contexts to optimize video generation parameters.
"""

import asyncio
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ContextOptimizationService:
    """Service for context-based generation optimization"""
    
    def __init__(self):
        """Initialize context optimization service"""
        self.optimization_cache = {}  # In-memory cache
        self.performance_history = defaultdict(list)
        self.adaptation_weights = defaultdict(lambda: 1.0)
        
        # Context influence weights
        self.context_weights = {
            "environmental": {
                "temperature": 0.3,
                "humidity": 0.2,
                "lighting": 0.4,
                "season": 0.5
            },
            "temporal": {
                "time_of_day": 0.6,
                "day_of_week": 0.2,
                "season": 0.4
            },
            "user": {
                "mood": 0.7,
                "activity": 0.5,
                "preference_profile": 0.8
            }
        }
        
        # Style mappings
        self.style_mappings = {
            "morning": ["bright", "energetic", "fresh", "vibrant"],
            "afternoon": ["warm", "balanced", "natural", "clear"],
            "evening": ["soft", "cozy", "warm", "intimate"],
            "night": ["mysterious", "dramatic", "moody", "ambient"],
            "sunny": ["bright", "cheerful", "vivid", "optimistic"],
            "cloudy": ["soft", "muted", "dreamy", "contemplative"],
            "rainy": ["cozy", "melancholic", "atmospheric", "introspective"],
            "winter": ["cool", "crystalline", "serene", "minimalist"],
            "spring": ["fresh", "vibrant", "growing", "renewal"],
            "summer": ["warm", "energetic", "abundant", "lively"],
            "autumn": ["warm", "golden", "nostalgic", "harvest"]
        }
        
        # Color palettes
        self.color_palettes = {
            "warm": ["#FF6B35", "#F7931E", "#FFD23F", "#EE4B2B"],
            "cool": ["#36D8FF", "#4A90E2", "#7B68EE", "#00CED1"],
            "natural": ["#8FBC8F", "#DEB887", "#CD853F", "#D2B48C"],
            "vibrant": ["#FF1493", "#00FF7F", "#FFD700", "#FF4500"],
            "muted": ["#708090", "#A9A9A9", "#D3D3D3", "#C0C0C0"],
            "sunset": ["#FF4500", "#FF6347", "#FFD700", "#FF69B4"],
            "autumn": ["#CD853F", "#DEB887", "#D2691E", "#BC8F8F"]
        }
    
    async def analyze_context(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze context and return optimization suggestions"""
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(context_data)
            
            # Check cache first
            if cache_key in self.optimization_cache:
                result = self.optimization_cache[cache_key].copy()
                result["cache_hit"] = True
                return result
            
            # Perform context analysis
            start_time = time.time()
            
            # Extract context elements
            time_of_day = context_data.get("time_of_day", "day")
            weather = context_data.get("weather", "clear")
            temperature = context_data.get("temperature", 20)
            user_activity = context_data.get("user_activity", "general")
            
            # Generate style suggestions
            style_suggestions = self._generate_style_suggestions(context_data)
            
            # Determine mood adjustment
            mood_adjustment = self._calculate_mood_adjustment(context_data)
            
            # Select color palette
            color_palette = self._select_color_palette(context_data)
            
            # Calculate optimization score
            optimization_score = self._calculate_optimization_score(context_data)
            
            # Build result
            result = {
                "style_suggestions": style_suggestions,
                "mood_adjustment": mood_adjustment,
                "color_palette": color_palette,
                "optimization_score": optimization_score,
                "cache_hit": False,
                "processing_time_ms": int((time.time() - start_time) * 1000)
            }
            
            # Cache result
            self.optimization_cache[cache_key] = result.copy()
            
            logger.info(f"Analyzed context, optimization score: {optimization_score}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze context: {e}")
            return {
                "style_suggestions": ["balanced"],
                "mood_adjustment": "neutral",
                "color_palette": ["#808080"],
                "optimization_score": 0.5,
                "cache_hit": False,
                "processing_time_ms": 0
            }
    
    def _generate_cache_key(self, context_data: Dict[str, Any]) -> str:
        """Generate cache key from context data"""
        # Create deterministic string from context data
        context_str = json.dumps(context_data, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()
    
    def _generate_style_suggestions(self, context_data: Dict[str, Any]) -> List[str]:
        """Generate style suggestions based on context"""
        suggestions = set()
        
        # Time-based styles
        time_of_day = context_data.get("time_of_day")
        if time_of_day in self.style_mappings:
            suggestions.update(self.style_mappings[time_of_day])
        
        # Weather-based styles
        weather = context_data.get("weather")
        if weather in self.style_mappings:
            suggestions.update(self.style_mappings[weather])
        
        # Season-based styles
        season = context_data.get("season")
        if season in self.style_mappings:
            suggestions.update(self.style_mappings[season])
        
        # User activity influence
        activity = context_data.get("user_activity", "").lower()
        if "party" in activity or "energetic" in activity:
            suggestions.update(["vibrant", "dynamic", "energetic"])
        elif "relax" in activity or "peaceful" in activity:
            suggestions.update(["soft", "calming", "serene"])
        
        return list(suggestions)[:4]  # Return top 4 suggestions
    
    def _calculate_mood_adjustment(self, context_data: Dict[str, Any]) -> str:
        """Calculate mood adjustment based on context"""
        mood_score = 0.0
        
        # Time of day influence
        time_of_day = context_data.get("time_of_day", "day")
        if time_of_day in ["morning", "afternoon"]:
            mood_score += 0.3
        elif time_of_day == "evening":
            mood_score += 0.1
        elif time_of_day == "night":
            mood_score -= 0.2
        
        # Weather influence
        weather = context_data.get("weather", "clear")
        if weather == "sunny":
            mood_score += 0.4
        elif weather == "cloudy":
            mood_score += 0.1
        elif weather == "rainy":
            mood_score -= 0.3
        
        # Temperature influence
        temperature = context_data.get("temperature", 20)
        if 18 <= temperature <= 25:
            mood_score += 0.2
        elif temperature < 10 or temperature > 30:
            mood_score -= 0.2
        
        # User mood
        user_mood = context_data.get("user_mood", "").lower()
        if "happy" in user_mood or "energetic" in user_mood:
            mood_score += 0.5
        elif "sad" in user_mood or "tired" in user_mood:
            mood_score -= 0.4
        elif "peaceful" in user_mood or "calm" in user_mood:
            mood_score += 0.2
        
        # Convert score to mood
        if mood_score > 0.5:
            return "uplifting"
        elif mood_score > 0.2:
            return "positive"
        elif mood_score > -0.2:
            return "neutral"
        elif mood_score > -0.5:
            return "contemplative"
        else:
            return "introspective"
    
    def _select_color_palette(self, context_data: Dict[str, Any]) -> List[str]:
        """Select appropriate color palette based on context"""
        time_of_day = context_data.get("time_of_day", "day")
        weather = context_data.get("weather", "clear")
        season = context_data.get("season", "summer")
        
        # Priority order: time > weather > season
        if time_of_day == "sunset" or time_of_day == "evening":
            return self.color_palettes.get("sunset", self.color_palettes["warm"])
        elif weather == "sunny":
            return self.color_palettes.get("vibrant", self.color_palettes["warm"])
        elif weather == "rainy":
            return self.color_palettes.get("muted", self.color_palettes["cool"])
        elif season == "autumn":
            return self.color_palettes.get("autumn", self.color_palettes["warm"])
        elif season == "winter":
            return self.color_palettes.get("cool", self.color_palettes["muted"])
        else:
            return self.color_palettes.get("natural", self.color_palettes["balanced"])
    
    def _calculate_optimization_score(self, context_data: Dict[str, Any]) -> float:
        """Calculate overall optimization confidence score"""
        score = 0.5  # Base score
        
        # More complete context data = higher score
        context_elements = ["time_of_day", "weather", "temperature", "season", "user_activity"]
        completeness = sum(1 for elem in context_elements if elem in context_data) / len(context_elements)
        score += completeness * 0.3
        
        # Adaptation weight (learns from feedback)
        cache_key = self._generate_cache_key(context_data)
        adaptation_weight = self.adaptation_weights.get(cache_key, 1.0)
        score *= adaptation_weight
        
        return min(max(score, 0.1), 0.95)
    
    async def optimize_generation_params(self, contexts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Optimize generation parameters based on multiple context sources"""
        try:
            # Combine all contexts
            combined_context = {}
            for context_type, context_data in contexts.items():
                combined_context.update(context_data)
            
            # Analyze combined context
            analysis = await self.analyze_context(combined_context)
            
            # Generate optimization parameters
            params = {
                "style": analysis["style_suggestions"][0] if analysis["style_suggestions"] else "balanced",
                "mood": analysis["mood_adjustment"],
                "color_palette": analysis["color_palette"],
                "energy_level": self._calculate_energy_level(combined_context),
                "color_temperature": self._calculate_color_temperature(combined_context),
                "optimization_confidence": analysis["optimization_score"]
            }
            
            # Apply context-specific weights
            for context_type, context_data in contexts.items():
                if context_type in self.context_weights:
                    weight = sum(self.context_weights[context_type].values()) / len(self.context_weights[context_type])
                    params["optimization_confidence"] *= (1 + weight * 0.2)
            
            params["optimization_confidence"] = min(params["optimization_confidence"], 0.95)
            
            return params
            
        except Exception as e:
            logger.error(f"Failed to optimize generation params: {e}")
            return {
                "style": "balanced",
                "mood": "neutral", 
                "color_palette": ["#808080"],
                "energy_level": 0.5,
                "color_temperature": 5500,
                "optimization_confidence": 0.3
            }
    
    def _calculate_energy_level(self, context: Dict[str, Any]) -> float:
        """Calculate energy level based on context"""
        energy = 0.5  # Base energy
        
        # Activity influence
        activity = context.get("activity", "").lower()
        if "party" in activity or "dance" in activity:
            energy = 0.9
        elif "workout" in activity or "exercise" in activity:
            energy = 0.8
        elif "relax" in activity or "meditation" in activity:
            energy = 0.2
        elif "sleep" in activity:
            energy = 0.1
        
        # Time influence
        time_of_day = context.get("time_of_day", "day")
        if time_of_day == "morning":
            energy += 0.2
        elif time_of_day == "night":
            energy -= 0.2
        
        return min(max(energy, 0.1), 1.0)
    
    def _calculate_color_temperature(self, context: Dict[str, Any]) -> int:
        """Calculate color temperature in Kelvin"""
        # Base temperature
        temp = 5500  # Daylight
        
        time_of_day = context.get("time_of_day", "day")
        if time_of_day == "sunrise" or time_of_day == "sunset":
            temp = 3000  # Warm
        elif time_of_day == "evening":
            temp = 3500  # Warm white
        elif time_of_day == "night":
            temp = 2700  # Very warm
        elif time_of_day == "noon":
            temp = 6500  # Cool white
        
        return temp
    
    async def optimize_prompt(self, base_prompt: str, context: Dict[str, Any]) -> str:
        """Optimize prompt based on context"""
        try:
            analysis = await self.analyze_context(context)
            
            optimized_prompt = base_prompt
            
            # Add style elements
            if analysis["style_suggestions"]:
                style = analysis["style_suggestions"][0]
                optimized_prompt += f", {style} style"
            
            # Add mood elements
            mood = analysis["mood_adjustment"]
            if mood != "neutral":
                optimized_prompt += f", {mood} mood"
            
            # Add context-specific elements
            time_of_day = context.get("time_of_day")
            if time_of_day:
                if time_of_day == "sunset":
                    optimized_prompt += ", golden hour lighting"
                elif time_of_day == "night":
                    optimized_prompt += ", soft moonlight"
                elif time_of_day == "morning":
                    optimized_prompt += ", bright morning light"
            
            season = context.get("season")
            if season:
                optimized_prompt += f", {season} atmosphere"
            
            weather = context.get("weather")
            if weather and weather != "clear":
                optimized_prompt += f", {weather} weather"
            
            return optimized_prompt.strip()
            
        except Exception as e:
            logger.error(f"Failed to optimize prompt: {e}")
            return base_prompt
    
    async def track_optimization_performance(self, optimization_id: str, 
                                           context: Dict[str, Any], 
                                           result: Dict[str, Any]) -> bool:
        """Track performance of optimization"""
        try:
            cache_key = self._generate_cache_key(context)
            
            performance_data = {
                "optimization_id": optimization_id,
                "context": context,
                "result": result,
                "timestamp": datetime.now(),
                "satisfaction": result.get("user_satisfaction", 0.5),
                "quality": result.get("generation_quality", 0.5),
                "context_match": result.get("context_match", 0.5)
            }
            
            self.performance_history[cache_key].append(performance_data)
            
            # Update adaptation weights based on feedback
            overall_score = (
                performance_data["satisfaction"] + 
                performance_data["quality"] + 
                performance_data["context_match"]
            ) / 3
            
            current_weight = self.adaptation_weights[cache_key]
            self.adaptation_weights[cache_key] = current_weight * 0.9 + overall_score * 0.1
            
            logger.info(f"Tracked optimization performance: {overall_score}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track optimization performance: {e}")
            return False
    
    async def get_optimization_metrics(self) -> Dict[str, Any]:
        """Get optimization performance metrics"""
        try:
            total_optimizations = sum(len(history) for history in self.performance_history.values())
            
            if total_optimizations == 0:
                return {
                    "total_optimizations": 0,
                    "average_satisfaction": 0.5,
                    "best_performing_contexts": [],
                    "cache_hit_rate": 0.0
                }
            
            # Calculate averages
            all_scores = []
            for history in self.performance_history.values():
                for record in history:
                    all_scores.append(record["satisfaction"])
            
            average_satisfaction = sum(all_scores) / len(all_scores) if all_scores else 0.5
            
            # Find best performing contexts
            best_contexts = []
            for cache_key, history in self.performance_history.items():
                if history:
                    avg_score = sum(r["satisfaction"] for r in history) / len(history)
                    best_contexts.append({
                        "context": history[0]["context"],
                        "avg_satisfaction": avg_score,
                        "count": len(history)
                    })
            
            best_contexts.sort(key=lambda x: x["avg_satisfaction"], reverse=True)
            
            return {
                "total_optimizations": total_optimizations,
                "average_satisfaction": average_satisfaction,
                "best_performing_contexts": best_contexts[:5],
                "cache_hit_rate": len(self.optimization_cache) / max(total_optimizations, 1)
            }
            
        except Exception as e:
            logger.error(f"Failed to get optimization metrics: {e}")
            return {
                "total_optimizations": 0,
                "average_satisfaction": 0.5,
                "best_performing_contexts": [],
                "cache_hit_rate": 0.0
            }
    
    async def record_feedback(self, optimization_id: str, params: Dict[str, Any], 
                            feedback: Dict[str, Any]) -> bool:
        """Record feedback for optimization"""
        try:
            # Find the context for this optimization
            for cache_key, history in self.performance_history.items():
                for record in history:
                    if record.get("optimization_id") == optimization_id:
                        # Update the record with feedback
                        record["feedback"] = feedback
                        satisfaction = feedback.get("satisfaction", 0.5)
                        
                        # Adjust adaptation weights
                        current_weight = self.adaptation_weights[cache_key]
                        adjustment = (satisfaction - 0.5) * 0.1
                        self.adaptation_weights[cache_key] = max(0.1, min(2.0, current_weight + adjustment))
                        
                        return True
            
            logger.warning(f"Optimization {optimization_id} not found for feedback")
            return False
            
        except Exception as e:
            logger.error(f"Failed to record feedback: {e}")
            return False