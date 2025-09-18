"""
Dynamic prompt enhancement service for AI-powered prompt optimization.
Implements multi-layer enhancement, style transfer, and adaptive learning.
"""

import uuid
import time
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from src.models.prompt_enhancement import (
    PromptEnhancement, 
    EnhancementRequest, 
    EnhancementResponse,
    EnhancementLayer,
    EnhancementHistory,
    AdaptationMetrics
)


class DynamicPromptService:
    """Service for dynamic prompt enhancement with multi-layer optimization"""
    
    def __init__(self, db_url: str = "sqlite:///ai_dynamic_painting.db"):
        self.engine = create_engine(db_url)
        self.session_factory = sessionmaker(bind=self.engine)
        self.enhancement_cache = {}
        self.style_patterns = {
            "van_gogh": ["swirling brushstrokes", "vibrant yellows and blues", "expressive texture"],
            "picasso": ["cubist perspective", "geometric forms", "bold angular shapes"],
            "monet": ["impressionist style", "soft light", "water lilies", "atmospheric"],
            "dali": ["surrealist", "melting forms", "dreamlike", "impossible perspectives"]
        }
        self.quality_weights = {
            "length_bonus": 0.1,
            "style_clarity": 0.3,
            "technical_terms": 0.2,
            "artistic_elements": 0.4
        }
        
    async def enhance_prompt(self, base_prompt: str, enhancement_config: Dict[str, Any], 
                           user_id: Optional[str] = None) -> str:
        """Enhance a prompt based on configuration parameters"""
        enhancement_id = f"enh_{uuid.uuid4().hex[:8]}"
        
        enhanced_prompt = base_prompt
        
        # Apply target style
        if target_style := enhancement_config.get("target_style"):
            enhanced_prompt = f"{enhanced_prompt}, in {target_style} style"
            
        # Apply mood
        if mood := enhancement_config.get("mood"):
            enhanced_prompt = f"{enhanced_prompt}, {mood} atmosphere"
            
        # Apply technical quality
        if tech_quality := enhancement_config.get("technical_quality"):
            enhanced_prompt = f"{enhanced_prompt}, {tech_quality}"
            
        # Apply artistic elements
        if artistic_elements := enhancement_config.get("artistic_elements"):
            elements_str = ", ".join(artistic_elements)
            enhanced_prompt = f"{enhanced_prompt}, with {elements_str}"
            
        # Store enhancement
        session = self.session_factory()
        try:
            enhancement = PromptEnhancement(
                enhancement_id=enhancement_id,
                base_prompt=base_prompt,
                enhanced_prompt=enhanced_prompt,
                enhancement_type="multi_config",
                enhancement_params=enhancement_config,
                user_id=user_id
            )
            session.add(enhancement)
            session.commit()
        finally:
            session.close()
            
        return enhanced_prompt
    
    async def enhance_with_context(self, base_prompt: str, context: Dict[str, Any]) -> str:
        """Enhance prompt based on contextual information"""
        enhanced_prompt = base_prompt
        
        # Time of day context
        if time_of_day := context.get("time_of_day"):
            if time_of_day == "night":
                enhanced_prompt = f"{enhanced_prompt}, nighttime scene, dark atmosphere"
            elif time_of_day == "dawn":
                enhanced_prompt = f"{enhanced_prompt}, dawn lighting, soft morning glow"
                
        # Weather context
        if weather := context.get("weather"):
            if weather == "rainy":
                enhanced_prompt = f"{enhanced_prompt}, rain, wet surfaces, moody lighting"
            elif weather == "sunny":
                enhanced_prompt = f"{enhanced_prompt}, bright sunlight, clear skies"
                
        # Season context
        if season := context.get("season"):
            if season == "winter":
                enhanced_prompt = f"{enhanced_prompt}, winter scene, cold atmosphere"
            elif season == "autumn":
                enhanced_prompt = f"{enhanced_prompt}, autumn colors, golden leaves"
                
        # Mood context
        if mood := context.get("mood"):
            enhanced_prompt = f"{enhanced_prompt}, {mood} mood"
            
        return enhanced_prompt
    
    async def apply_enhancement_layers(self, base_prompt: str, enhancement_layers: List[Dict[str, Any]]) -> str:
        """Apply multiple enhancement layers to a prompt"""
        enhanced_prompt = base_prompt
        
        for layer in enhancement_layers:
            layer_type = layer.get("layer")
            params = layer.get("params", {})
            
            if layer_type == "style":
                style = params.get("style", "balanced")
                intensity = params.get("intensity", 0.5)
                if intensity > 0.7:
                    enhanced_prompt = f"{enhanced_prompt}, strong {style} style"
                else:
                    enhanced_prompt = f"{enhanced_prompt}, subtle {style} influence"
                    
            elif layer_type == "lighting":
                lighting = params.get("lighting", "natural")
                time = params.get("time", "day")
                enhanced_prompt = f"{enhanced_prompt}, {lighting} lighting at {time}"
                
            elif layer_type == "details":
                details = params.get("details", [])
                if details:
                    detail_str = ", ".join(details)
                    enhanced_prompt = f"{enhanced_prompt}, featuring {detail_str}"
                    
            elif layer_type == "technical":
                quality = params.get("quality", "standard")
                render = params.get("render", "realistic")
                enhanced_prompt = f"{enhanced_prompt}, {quality} quality, {render} rendering"
                
        return enhanced_prompt
    
    async def score_enhancement_quality(self, base_prompt: str, enhanced_prompt: str) -> float:
        """Score the quality of prompt enhancement"""
        base_len = len(base_prompt.split())
        enhanced_len = len(enhanced_prompt.split())
        
        # Length improvement score
        length_score = min((enhanced_len - base_len) / base_len, 1.0) if base_len > 0 else 0
        
        # Style clarity score (check for style-related terms)
        style_terms = ["style", "artistic", "painting", "rendering", "technique"]
        style_score = sum(1 for term in style_terms if term in enhanced_prompt.lower()) / len(style_terms)
        
        # Technical terms score
        tech_terms = ["quality", "resolution", "lighting", "composition", "detailed"]
        tech_score = sum(1 for term in tech_terms if term in enhanced_prompt.lower()) / len(tech_terms)
        
        # Artistic elements score
        art_terms = ["beautiful", "atmospheric", "cinematic", "dramatic", "vibrant"]
        art_score = sum(1 for term in art_terms if term in enhanced_prompt.lower()) / len(art_terms)
        
        # Weighted final score
        final_score = (
            length_score * self.quality_weights["length_bonus"] +
            style_score * self.quality_weights["style_clarity"] +
            tech_score * self.quality_weights["technical_terms"] +
            art_score * self.quality_weights["artistic_elements"]
        )
        
        return min(final_score, 1.0)
    
    async def apply_style_transfer(self, base_prompt: str, target_style: str) -> str:
        """Apply specific artistic style to prompt"""
        style_key = target_style.lower().replace(" ", "_")
        
        if style_patterns := self.style_patterns.get(style_key):
            style_elements = ", ".join(style_patterns[:2])  # Use first 2 elements
            enhanced_prompt = f"{base_prompt}, in the style of {target_style}, {style_elements}"
        else:
            enhanced_prompt = f"{base_prompt}, in {target_style} style"
            
        return enhanced_prompt
    
    async def optimize_technical_aspects(self, base_prompt: str, technical_params: Dict[str, Any]) -> str:
        """Optimize prompt with technical parameters"""
        enhanced_prompt = base_prompt
        
        # Add resolution
        if resolution := technical_params.get("resolution"):
            enhanced_prompt = f"{enhanced_prompt}, {resolution} resolution"
            
        # Add camera specs
        if camera := technical_params.get("camera"):
            enhanced_prompt = f"{enhanced_prompt}, shot with {camera}"
            
        # Add lens info
        if lens := technical_params.get("lens"):
            enhanced_prompt = f"{enhanced_prompt}, {lens} lens"
            
        # Add lighting setup
        if lighting := technical_params.get("lighting"):
            enhanced_prompt = f"{enhanced_prompt}, {lighting}"
            
        # Add composition rules
        if composition := technical_params.get("composition"):
            enhanced_prompt = f"{enhanced_prompt}, {composition} composition"
            
        return enhanced_prompt
    
    async def get_enhancement_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get enhancement history for a user"""
        session = self.session_factory()
        try:
            enhancements = session.query(PromptEnhancement).filter(
                PromptEnhancement.user_id == user_id
            ).order_by(PromptEnhancement.created_at.desc()).limit(10).all()
            
            history = []
            for enhancement in enhancements:
                history.append({
                    "enhancement_id": enhancement.enhancement_id,
                    "base_prompt": enhancement.base_prompt,
                    "enhanced_prompt": enhancement.enhanced_prompt,
                    "enhancement_type": enhancement.enhancement_type,
                    "quality_score": enhancement.quality_score,
                    "user_satisfaction": enhancement.user_satisfaction,
                    "timestamp": enhancement.created_at.isoformat()
                })
                
            return history
        finally:
            session.close()
    
    async def record_enhancement_feedback(self, enhancement_id: str, feedback: Dict[str, float]):
        """Record user feedback for enhancement"""
        session = self.session_factory()
        try:
            enhancement = session.query(PromptEnhancement).filter(
                PromptEnhancement.enhancement_id == enhancement_id
            ).first()
            
            if enhancement:
                enhancement.update_feedback(
                    satisfaction=feedback.get("user_satisfaction"),
                    technical=feedback.get("technical_quality"),
                    style=feedback.get("style_accuracy")
                )
                session.commit()
                
        finally:
            session.close()
    
    async def get_adaptation_metrics(self) -> Dict[str, Any]:
        """Get system adaptation and learning metrics"""
        session = self.session_factory()
        try:
            total_enhancements = session.query(PromptEnhancement).count()
            
            if total_enhancements == 0:
                return {
                    "learning_rate": 0.0,
                    "improvement_trend": 0.0,
                    "total_enhancements": 0,
                    "average_quality": 0.0
                }
            
            # Calculate average quality
            enhancements = session.query(PromptEnhancement).all()
            avg_quality = sum(e.quality_score for e in enhancements) / len(enhancements)
            
            # Calculate improvement trend (last 10 vs previous 10)
            recent = session.query(PromptEnhancement).order_by(
                PromptEnhancement.created_at.desc()
            ).limit(10).all()
            
            older = session.query(PromptEnhancement).order_by(
                PromptEnhancement.created_at.desc()
            ).offset(10).limit(10).all()
            
            recent_avg = sum(e.quality_score for e in recent) / len(recent) if recent else 0
            older_avg = sum(e.quality_score for e in older) / len(older) if older else 0
            improvement_trend = recent_avg - older_avg if older_avg > 0 else 0
            
            return {
                "learning_rate": 0.1,  # Fixed learning rate
                "improvement_trend": improvement_trend,
                "total_enhancements": total_enhancements,
                "average_quality": avg_quality
            }
            
        finally:
            session.close()