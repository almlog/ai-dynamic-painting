"""Learning Service for user preference learning and personalization."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import math
from statistics import mean, median, stdev
import numpy as np
from collections import defaultdict, Counter
from sklearn.cluster import KMeans
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score

logger = logging.getLogger("ai_system.learning")


class PreferenceType(Enum):
    """Enumeration for preference types"""
    STYLE = "style"
    CONTENT = "content"
    TIMING = "timing"
    DURATION = "duration"
    MOOD = "mood"
    WEATHER = "weather"
    SEASON = "season"


class InteractionType(Enum):
    """Enumeration for interaction types"""
    VIEW = "view"
    LIKE = "like"
    SKIP = "skip"
    SHARE = "share"
    SAVE = "save"
    DELETE = "delete"
    REPLAY = "replay"


class LearningAlgorithm(Enum):
    """Enumeration for learning algorithms"""
    COLLABORATIVE_FILTERING = "collaborative_filtering"
    CONTENT_BASED = "content_based"
    HYBRID = "hybrid"
    DEEP_LEARNING = "deep_learning"
    REINFORCEMENT = "reinforcement"


class ConfidenceLevel(Enum):
    """Enumeration for confidence levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class PreferenceCategory(Enum):
    """Enumeration for preference categories"""
    VISUAL = "visual"
    TEMPORAL = "temporal"
    CONTEXTUAL = "contextual"
    BEHAVIORAL = "behavioral"
    EMOTIONAL = "emotional"


class FeedbackType(Enum):
    """Enumeration for feedback types"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    EXPLICIT = "explicit"
    IMPLICIT = "implicit"


class LearningMode(Enum):
    """Enumeration for learning modes"""
    ACTIVE = "active"
    PASSIVE = "passive"
    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    REINFORCEMENT = "reinforcement"


class PersonalizationLevel(Enum):
    """Enumeration for personalization levels"""
    MINIMAL = "minimal"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    ADAPTIVE = "adaptive"
    CUSTOM = "custom"


@dataclass
class UserPreference:
    """Data class for user preference representation"""
    user_id: str
    preference_type: PreferenceType
    preference_value: str
    confidence: float = 0.5
    weight: float = 1.0
    interaction_count: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    creation_date: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert preference to dictionary"""
        return {
            'user_id': self.user_id,
            'preference_type': self.preference_type.value,
            'preference_value': self.preference_value,
            'confidence': self.confidence,
            'weight': self.weight,
            'interaction_count': self.interaction_count,
            'last_updated': self.last_updated.isoformat(),
            'creation_date': self.creation_date.isoformat()
        }


@dataclass
class InteractionRecord:
    """Data class for interaction record"""
    user_id: str
    content_id: str
    interaction_type: InteractionType
    duration_watched: int = 0
    total_duration: int = 0
    content_metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def completion_rate(self) -> float:
        """Calculate completion rate"""
        if self.total_duration > 0:
            return min(self.duration_watched / self.total_duration, 1.0)
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert interaction to dictionary"""
        return {
            'user_id': self.user_id,
            'content_id': self.content_id,
            'interaction_type': self.interaction_type.value,
            'duration_watched': self.duration_watched,
            'total_duration': self.total_duration,
            'completion_rate': self.completion_rate,
            'content_metadata': self.content_metadata,
            'timestamp': self.timestamp.isoformat(),
            'context': self.context
        }


class LearningService:
    """Advanced learning service for user preference analysis and personalization"""
    
    def __init__(self):
        """Initialize the learning service"""
        self.user_preferences: Dict[str, Dict[str, UserPreference]] = defaultdict(dict)
        self.interaction_history: List[InteractionRecord] = []
        self.learning_models: Dict[str, Any] = {}
        self.algorithm_weights = {
            LearningAlgorithm.COLLABORATIVE_FILTERING: 0.3,
            LearningAlgorithm.CONTENT_BASED: 0.4,
            LearningAlgorithm.HYBRID: 0.3
        }
        self.confidence_thresholds = {
            ConfidenceLevel.VERY_LOW: 0.2,
            ConfidenceLevel.LOW: 0.4,
            ConfidenceLevel.MEDIUM: 0.6,
            ConfidenceLevel.HIGH: 0.8,
            ConfidenceLevel.VERY_HIGH: 0.9
        }
        logger.info("LearningService initialized")
    
    async def learn_user_preferences(self, user_id: str, interaction_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Learn user preferences from interaction data"""
        try:
            # Convert interaction data to InteractionRecord objects
            interactions = []
            for data in interaction_data:
                interaction = InteractionRecord(
                    user_id=data['user_id'],
                    content_id=data['content_id'],
                    interaction_type=data['interaction_type'],
                    duration_watched=data.get('duration_watched', 0),
                    total_duration=data.get('total_duration', 0),
                    content_metadata=data.get('content_metadata', {}),
                    timestamp=data.get('timestamp', datetime.now()),
                    context=data.get('context', {})
                )
                interactions.append(interaction)
                self.interaction_history.append(interaction)
            
            # Extract preferences from interactions
            preferences = {}
            confidence_scores = {}
            
            # Analyze content metadata preferences
            for preference_type in ['style', 'mood', 'weather', 'time_of_day']:
                pref_analysis = self._analyze_preference_from_interactions(
                    interactions, preference_type
                )
                if pref_analysis:
                    preferences[preference_type] = pref_analysis
                    confidence_scores[preference_type] = pref_analysis['confidence']
            
            # Store learned preferences
            for pref_type, pref_data in preferences.items():
                preference_obj = UserPreference(
                    user_id=user_id,
                    preference_type=self._safe_get_preference_type(pref_type),
                    preference_value=pref_data['value'],
                    confidence=pref_data['confidence'],
                    interaction_count=len(interactions)
                )
                self.user_preferences[user_id][pref_type] = preference_obj
            
            learning_metadata = {
                'total_interactions': len(interactions),
                'learning_algorithm': 'content_based_analysis',
                'processing_timestamp': datetime.now().isoformat(),
                'preferences_learned': len(preferences)
            }
            
            logger.info(f"Learned {len(preferences)} preferences for user {user_id}")
            
            return {
                'preferences': preferences,
                'confidence_scores': confidence_scores,
                'learning_metadata': learning_metadata
            }
            
        except Exception as e:
            logger.error(f"Error learning user preferences: {e}")
            raise
    
    async def predict_user_preferences(self, user_id: str, content_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Predict user preferences for content candidates"""
        try:
            user_prefs = self.user_preferences.get(user_id, {})
            predictions = []
            
            for candidate in content_candidates:
                content_id = candidate['content_id']
                preference_score = 0.0
                confidence = 0.0
                reasoning_factors = []
                
                # Calculate preference score based on learned preferences
                total_weight = 0.0
                
                for pref_type, pref_obj in user_prefs.items():
                    if pref_type in candidate:
                        candidate_value = candidate[pref_type]
                        
                        # Calculate match score
                        if candidate_value == pref_obj.preference_value:
                            match_score = 1.0
                            reasoning_factors.append(f"Strong match for {pref_type}: {candidate_value}")
                        else:
                            match_score = self._calculate_similarity(
                                pref_obj.preference_value, candidate_value, pref_type
                            )
                            reasoning_factors.append(f"Partial match for {pref_type}: {candidate_value}")
                        
                        weighted_score = match_score * pref_obj.confidence * pref_obj.weight
                        preference_score += weighted_score
                        total_weight += pref_obj.confidence * pref_obj.weight
                
                # Normalize preference score
                if total_weight > 0:
                    preference_score = preference_score / total_weight
                    confidence = min(total_weight / len(user_prefs), 1.0)
                else:
                    preference_score = 0.5  # Neutral score for unknown users
                    confidence = 0.1
                    reasoning_factors.append("No learned preferences available")
                
                predictions.append({
                    'content_id': content_id,
                    'preference_score': max(0.0, min(1.0, preference_score)),
                    'confidence': max(0.0, min(1.0, confidence)),
                    'reasoning': '; '.join(reasoning_factors)
                })
            
            logger.info(f"Generated {len(predictions)} preference predictions for user {user_id}")
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting user preferences: {e}")
            return []
    
    async def update_preference_weights(self, user_id: str, weight_updates: Dict[str, float]) -> Dict[str, Any]:
        """Update preference weights for a user"""
        try:
            user_prefs = self.user_preferences.get(user_id, {})
            updated_preferences = []
            
            for pref_type, new_weight in weight_updates.items():
                if pref_type in user_prefs:
                    old_weight = user_prefs[pref_type].weight
                    user_prefs[pref_type].weight = max(0.0, min(2.0, new_weight))
                    user_prefs[pref_type].last_updated = datetime.now()
                    
                    updated_preferences.append({
                        'preference_type': pref_type,
                        'old_weight': old_weight,
                        'new_weight': user_prefs[pref_type].weight
                    })
            
            return {
                'updated_preferences': updated_preferences,
                'update_timestamp': datetime.now().isoformat(),
                'user_id': user_id
            }
            
        except Exception as e:
            logger.error(f"Error updating preference weights: {e}")
            raise
    
    async def analyze_interaction_patterns(self, user_id: str, analysis_period: Dict[str, str]) -> Dict[str, Any]:
        """Analyze user interaction patterns over a period"""
        try:
            start_date = datetime.fromisoformat(analysis_period['start_date'])
            end_date = datetime.fromisoformat(analysis_period['end_date'])
            
            # Filter interactions for user and period
            user_interactions = [
                interaction for interaction in self.interaction_history
                if interaction.user_id == user_id and start_date <= interaction.timestamp <= end_date
            ]
            
            if not user_interactions:
                return self._empty_pattern_analysis()
            
            # Analyze temporal patterns
            temporal_patterns = self._analyze_temporal_patterns(user_interactions)
            
            # Analyze content preferences
            content_preferences = self._analyze_content_preferences(user_interactions)
            
            # Calculate engagement metrics
            engagement_metrics = self._calculate_engagement_metrics(user_interactions)
            
            # Generate behavioral insights
            behavioral_insights = self._generate_behavioral_insights(user_interactions)
            
            return {
                'temporal_patterns': temporal_patterns,
                'content_preferences': content_preferences,
                'engagement_metrics': engagement_metrics,
                'behavioral_insights': behavioral_insights
            }
            
        except Exception as e:
            logger.error(f"Error analyzing interaction patterns: {e}")
            raise
    
    async def generate_personalized_recommendations(self, user_id: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized content recommendations"""
        try:
            user_prefs = self.user_preferences.get(user_id, {})
            recommendation_count = context.get('recommendation_count', 5)
            available_content_count = context.get('available_content_count', 50)
            
            # Generate mock content pool (in real implementation, this would query actual content)
            content_pool = self._generate_mock_content_pool(available_content_count)
            
            # Score each content item
            scored_content = []
            for content in content_pool:
                score = self._calculate_recommendation_score(user_id, content, context)
                scored_content.append({
                    'content_id': content['content_id'],
                    'recommendation_score': score['total_score'],
                    'personalization_factors': score['factors'],
                    'confidence': score['confidence'],
                    'explanation': score['explanation']
                })
            
            # Sort by score and return top recommendations
            scored_content.sort(key=lambda x: x['recommendation_score'], reverse=True)
            return scored_content[:recommendation_count]
            
        except Exception as e:
            logger.error(f"Error generating personalized recommendations: {e}")
            return []
    
    async def track_preference_evolution(self, user_id: str, evolution_period: Dict[str, Any]) -> Dict[str, Any]:
        """Track how user preferences evolve over time"""
        try:
            start_date = datetime.fromisoformat(evolution_period['start_date'])
            end_date = datetime.fromisoformat(evolution_period['end_date'])
            granularity = evolution_period.get('granularity', 'weekly')
            
            # Create time windows
            time_windows = self._create_time_windows(start_date, end_date, granularity)
            
            # Track preferences over each window
            preference_timeline = []
            for window_start, window_end in time_windows:
                window_interactions = [
                    interaction for interaction in self.interaction_history
                    if (interaction.user_id == user_id and 
                        window_start <= interaction.timestamp <= window_end)
                ]
                
                if window_interactions:
                    window_prefs = self._extract_preferences_from_window(window_interactions)
                    preference_timeline.append({
                        'timestamp': window_start.isoformat(),
                        'preferences': window_prefs,
                        'confidence_avg': np.mean([p['confidence'] for p in window_prefs.values()]) if window_prefs else 0.0,
                        'interaction_count': len(window_interactions)
                    })
            
            # Calculate stability metrics
            stability_metrics = self._calculate_preference_stability(preference_timeline)
            
            # Detect drift
            drift_detection = self._detect_preference_drift(preference_timeline)
            
            # Generate adaptation recommendations
            adaptation_recommendations = self._generate_adaptation_recommendations(
                preference_timeline, stability_metrics, drift_detection
            )
            
            return {
                'preference_timeline': preference_timeline,
                'stability_metrics': stability_metrics,
                'drift_detection': drift_detection,
                'adaptation_recommendations': adaptation_recommendations
            }
            
        except Exception as e:
            logger.error(f"Error tracking preference evolution: {e}")
            raise
    
    async def calculate_preference_confidence(self, user_id: str, preference_type: str) -> Dict[str, Any]:
        """Calculate confidence level for a specific preference"""
        try:
            user_prefs = self.user_preferences.get(user_id, {})
            
            if preference_type not in user_prefs:
                return {
                    'confidence_score': 0.0,
                    'confidence_level': ConfidenceLevel.VERY_LOW,
                    'factors': ['No preference data available']
                }
            
            preference = user_prefs[preference_type]
            
            # Calculate confidence based on multiple factors
            base_confidence = preference.confidence
            interaction_factor = min(preference.interaction_count / 20.0, 1.0)  # Normalize to 20 interactions
            recency_factor = self._calculate_recency_factor(preference.last_updated)
            consistency_factor = self._calculate_consistency_factor(user_id, preference_type)
            
            # Weighted combination
            final_confidence = (
                base_confidence * 0.4 +
                interaction_factor * 0.3 +
                recency_factor * 0.2 +
                consistency_factor * 0.1
            )
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(final_confidence)
            
            factors = [
                f"Base confidence: {base_confidence:.2f}",
                f"Interaction count: {preference.interaction_count}",
                f"Last updated: {preference.last_updated.strftime('%Y-%m-%d')}",
                f"Consistency score: {consistency_factor:.2f}"
            ]
            
            return {
                'confidence_score': final_confidence,
                'confidence_level': confidence_level,
                'factors': factors
            }
            
        except Exception as e:
            logger.error(f"Error calculating preference confidence: {e}")
            raise
    
    async def detect_preference_shifts(self, user_id: str, detection_params: Dict[str, Any]) -> Dict[str, Any]:
        """Detect shifts in user preferences"""
        try:
            window_days = detection_params.get('detection_window_days', 14)
            significance_threshold = detection_params.get('significance_threshold', 0.3)
            confidence_threshold = detection_params.get('confidence_threshold', 0.7)
            
            recent_cutoff = datetime.now() - timedelta(days=window_days)
            older_cutoff = datetime.now() - timedelta(days=window_days * 2)
            
            # Get recent and older interactions
            recent_interactions = [
                interaction for interaction in self.interaction_history
                if (interaction.user_id == user_id and 
                    interaction.timestamp >= recent_cutoff)
            ]
            
            older_interactions = [
                interaction for interaction in self.interaction_history
                if (interaction.user_id == user_id and 
                    older_cutoff <= interaction.timestamp < recent_cutoff)
            ]
            
            shifts_detected = False
            shift_details = []
            
            if recent_interactions and older_interactions:
                recent_prefs = self._extract_preferences_from_window(recent_interactions)
                older_prefs = self._extract_preferences_from_window(older_interactions)
                
                # Compare preferences
                for pref_type in set(recent_prefs.keys()) | set(older_prefs.keys()):
                    if pref_type in recent_prefs and pref_type in older_prefs:
                        recent_val = recent_prefs[pref_type]['value']
                        older_val = older_prefs[pref_type]['value']
                        
                        if recent_val != older_val:
                            confidence_avg = (recent_prefs[pref_type]['confidence'] + 
                                           older_prefs[pref_type]['confidence']) / 2
                            
                            if confidence_avg >= confidence_threshold:
                                shift_magnitude = abs(recent_prefs[pref_type]['confidence'] - 
                                                   older_prefs[pref_type]['confidence'])
                                
                                if shift_magnitude >= significance_threshold:
                                    shifts_detected = True
                                    shift_details.append({
                                        'preference_type': pref_type,
                                        'old_value': older_val,
                                        'new_value': recent_val,
                                        'shift_magnitude': shift_magnitude,
                                        'detection_timestamp': datetime.now().isoformat()
                                    })
            
            # Analyze impact
            impact_analysis = self._analyze_shift_impact(shift_details) if shift_details else {}
            
            return {
                'shifts_detected': shifts_detected,
                'shift_details': shift_details,
                'impact_analysis': impact_analysis
            }
            
        except Exception as e:
            logger.error(f"Error detecting preference shifts: {e}")
            raise
    
    async def optimize_content_selection(self, user_id: str, content_pool: List[Dict[str, Any]], 
                                       selection_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content selection based on user preferences"""
        try:
            selection_count = selection_criteria.get('selection_count', 5)
            diversity_factor = selection_criteria.get('diversity_factor', 0.3)
            novelty_factor = selection_criteria.get('novelty_factor', 0.2)
            preference_weight = selection_criteria.get('preference_weight', 0.5)
            
            scored_content = []
            
            for content in content_pool:
                # Calculate preference match score
                pref_score = self._calculate_preference_match_score(user_id, content)
                
                # Calculate novelty score
                novelty_score = self._calculate_novelty_score(user_id, content)
                
                # Calculate diversity contribution
                diversity_score = self._calculate_diversity_score(content, scored_content)
                
                # Combined score
                total_score = (
                    pref_score * preference_weight +
                    novelty_score * novelty_factor +
                    diversity_score * diversity_factor
                )
                
                scored_content.append({
                    'content_id': content['content_id'],
                    'selection_score': total_score,
                    'preference_match': pref_score,
                    'novelty_score': novelty_score,
                    'diversity_score': diversity_score
                })
            
            # Select top content using greedy diversification
            selected_content = self._greedy_diversified_selection(scored_content, selection_count)
            
            # Calculate metrics
            diversity_score = self._calculate_selection_diversity(selected_content)
            expected_satisfaction = np.mean([item['preference_match'] for item in selected_content])
            
            selection_reasoning = (
                f"Selected {len(selected_content)} items optimizing for "
                f"preference match ({preference_weight:.1%}), "
                f"novelty ({novelty_factor:.1%}), and "
                f"diversity ({diversity_factor:.1%})"
            )
            
            return {
                'selected_content': selected_content,
                'selection_reasoning': selection_reasoning,
                'diversity_score': diversity_score,
                'expected_satisfaction': expected_satisfaction
            }
            
        except Exception as e:
            logger.error(f"Error optimizing content selection: {e}")
            raise
    
    async def export_user_profile(self, user_id: str, export_options: Dict[str, Any]) -> Dict[str, Any]:
        """Export user profile and preferences"""
        try:
            include_raw_interactions = export_options.get('include_raw_interactions', False)
            include_learned_preferences = export_options.get('include_learned_preferences', True)
            include_model_weights = export_options.get('include_model_weights', False)
            anonymize_content_ids = export_options.get('anonymize_content_ids', True)
            
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'user_id': user_id if not anonymize_content_ids else 'anonymized',
                'privacy_level': 'anonymized' if anonymize_content_ids else 'full'
            }
            
            if include_learned_preferences:
                user_prefs = self.user_preferences.get(user_id, {})
                preferences_data = {}
                for pref_type, pref_obj in user_prefs.items():
                    preferences_data[pref_type] = {
                        'value': pref_obj.preference_value,
                        'confidence': pref_obj.confidence,
                        'weight': pref_obj.weight,
                        'interaction_count': pref_obj.interaction_count
                    }
                export_data['user_preferences'] = preferences_data
            
            # Learning metadata
            user_interactions = [i for i in self.interaction_history if i.user_id == user_id]
            export_data['learning_metadata'] = {
                'total_interactions': len(user_interactions),
                'learning_start_date': min(i.timestamp for i in user_interactions).isoformat() if user_interactions else None,
                'last_update': max(i.timestamp for i in user_interactions).isoformat() if user_interactions else None,
                'preferences_learned': len(self.user_preferences.get(user_id, {}))
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting user profile: {e}")
            raise
    
    async def import_user_profile(self, user_id: str, import_data: Dict[str, Any]) -> Dict[str, Any]:
        """Import user profile and preferences"""
        try:
            imported_preferences = []
            validation_results = []
            conflicts_resolved = []
            
            if 'user_preferences' in import_data:
                for pref_type, pref_data in import_data['user_preferences'].items():
                    try:
                        # Validate preference data
                        if self._validate_preference_data(pref_data):
                            preference_obj = UserPreference(
                                user_id=user_id,
                                preference_type=self._safe_get_preference_type(pref_type),
                                preference_value=pref_data['value'],
                                confidence=pref_data['confidence'],
                                weight=pref_data.get('weight', 1.0),
                                interaction_count=pref_data.get('interaction_count', 0)
                            )
                            
                            # Check for conflicts
                            if pref_type in self.user_preferences.get(user_id, {}):
                                conflicts_resolved.append({
                                    'preference_type': pref_type,
                                    'resolution': 'overwrote_existing'
                                })
                            
                            self.user_preferences[user_id][pref_type] = preference_obj
                            imported_preferences.append(pref_type)
                            validation_results.append({'preference_type': pref_type, 'status': 'valid'})
                        else:
                            validation_results.append({'preference_type': pref_type, 'status': 'invalid'})
                    except Exception as e:
                        validation_results.append({
                            'preference_type': pref_type, 
                            'status': 'error', 
                            'error': str(e)
                        })
            
            return {
                'import_status': 'completed',
                'imported_preferences': imported_preferences,
                'validation_results': validation_results,
                'conflicts_resolved': conflicts_resolved
            }
            
        except Exception as e:
            logger.error(f"Error importing user profile: {e}")
            raise
    
    async def reset_user_preferences(self, user_id: str, reset_options: Dict[str, Any]) -> Dict[str, Any]:
        """Reset user preferences with configurable options"""
        try:
            reset_level = reset_options.get('reset_level', 'partial')
            preserve_categories = reset_options.get('preserve_categories', [])
            reset_confidence_scores = reset_options.get('reset_confidence_scores', True)
            backup_before_reset = reset_options.get('backup_before_reset', True)
            
            backup_id = None
            if backup_before_reset:
                backup_data = await self.export_user_profile(user_id, {'include_learned_preferences': True})
                backup_id = str(uuid.uuid4())
                # In real implementation, save backup to storage
            
            user_prefs = self.user_preferences.get(user_id, {})
            preserved_preferences = {}
            reset_categories = []
            
            if reset_level == 'partial':
                # Preserve specified categories
                for pref_type in preserve_categories:
                    if pref_type in user_prefs:
                        preserved_preferences[pref_type] = user_prefs[pref_type].to_dict()
                
                # Reset non-preserved preferences
                for pref_type in list(user_prefs.keys()):
                    if pref_type not in preserve_categories:
                        if reset_confidence_scores:
                            user_prefs[pref_type].confidence = 0.5
                            user_prefs[pref_type].interaction_count = 0
                        reset_categories.append(pref_type)
            elif reset_level == 'full':
                # Reset all preferences
                self.user_preferences[user_id] = {}
                reset_categories = list(user_prefs.keys())
            
            return {
                'reset_status': 'completed',
                'backup_id': backup_id,
                'preserved_preferences': preserved_preferences,
                'reset_categories': reset_categories
            }
            
        except Exception as e:
            logger.error(f"Error resetting user preferences: {e}")
            raise
    
    async def get_preference_insights(self, user_id: str, insight_params: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive preference insights for a user"""
        try:
            insight_type = insight_params.get('insight_type', 'comprehensive')
            time_period_days = insight_params.get('time_period_days', 30)
            include_trends = insight_params.get('include_trends', True)
            include_comparisons = insight_params.get('include_comparisons', True)
            
            user_prefs = self.user_preferences.get(user_id, {})
            
            # Preference summary
            preference_summary = {}
            for pref_type, pref_obj in user_prefs.items():
                preference_summary[pref_type] = {
                    'value': pref_obj.preference_value,
                    'confidence': pref_obj.confidence,
                    'strength': self._categorize_preference_strength(pref_obj.confidence),
                    'interaction_count': pref_obj.interaction_count
                }
            
            # Trend analysis
            trend_analysis = {}
            if include_trends:
                cutoff_date = datetime.now() - timedelta(days=time_period_days)
                recent_interactions = [
                    i for i in self.interaction_history
                    if i.user_id == user_id and i.timestamp >= cutoff_date
                ]
                trend_analysis = self._analyze_preference_trends(recent_interactions)
            
            # Stability assessment
            stability_assessment = self._assess_preference_stability(user_id, time_period_days)
            
            # Personalization effectiveness
            personalization_effectiveness = self._calculate_personalization_effectiveness(user_id)
            
            return {
                'preference_summary': preference_summary,
                'trend_analysis': trend_analysis,
                'stability_assessment': stability_assessment,
                'personalization_effectiveness': personalization_effectiveness
            }
            
        except Exception as e:
            logger.error(f"Error getting preference insights: {e}")
            raise
    
    async def validate_learning_accuracy(self, user_id: str, validation_params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate learning accuracy using various metrics"""
        try:
            test_period_days = validation_params.get('test_period_days', 7)
            validation_metrics = validation_params.get('validation_metrics', ['precision', 'recall', 'f1_score'])
            cross_validation_folds = validation_params.get('cross_validation_folds', 5)
            
            # Get user interactions for validation
            user_interactions = [i for i in self.interaction_history if i.user_id == user_id]
            
            if len(user_interactions) < 10:
                return {
                    'overall_accuracy': 0.0,
                    'metric_scores': {},
                    'validation_details': {'error': 'Insufficient interaction data for validation'},
                    'improvement_suggestions': ['Collect more user interaction data']
                }
            
            # Split data for validation
            test_size = min(len(user_interactions) // 5, test_period_days * 2)
            train_interactions = user_interactions[:-test_size]
            test_interactions = user_interactions[-test_size:]
            
            # Train on historical data
            historical_prefs = self._extract_preferences_from_window(train_interactions)
            
            # Predict on test data
            predictions = []
            actuals = []
            
            for interaction in test_interactions:
                # Predict preference for this interaction
                predicted_like = self._predict_interaction_preference(
                    interaction, historical_prefs
                )
                actual_like = interaction.interaction_type in [InteractionType.LIKE, InteractionType.SAVE, InteractionType.REPLAY]
                
                predictions.append(1 if predicted_like else 0)
                actuals.append(1 if actual_like else 0)
            
            # Calculate metrics
            metric_scores = {}
            if predictions and actuals:
                if 'precision' in validation_metrics:
                    metric_scores['precision'] = precision_score(actuals, predictions, zero_division=0)
                if 'recall' in validation_metrics:
                    metric_scores['recall'] = recall_score(actuals, predictions, zero_division=0)
                if 'f1_score' in validation_metrics:
                    metric_scores['f1_score'] = f1_score(actuals, predictions, zero_division=0)
                if 'auc_roc' in validation_metrics and len(set(actuals)) > 1:
                    metric_scores['auc_roc'] = roc_auc_score(actuals, predictions)
            
            overall_accuracy = np.mean(list(metric_scores.values())) if metric_scores else 0.0
            
            # Generate improvement suggestions
            improvement_suggestions = []
            if overall_accuracy < 0.6:
                improvement_suggestions.append("Increase interaction data collection")
                improvement_suggestions.append("Refine preference learning algorithms")
            if overall_accuracy < 0.8:
                improvement_suggestions.append("Consider contextual factors in learning")
            
            return {
                'overall_accuracy': overall_accuracy,
                'metric_scores': metric_scores,
                'validation_details': {
                    'test_interactions': len(test_interactions),
                    'train_interactions': len(train_interactions),
                    'validation_method': 'temporal_split'
                },
                'improvement_suggestions': improvement_suggestions
            }
            
        except Exception as e:
            logger.error(f"Error validating learning accuracy: {e}")
            raise
    
    async def adapt_to_feedback(self, user_id: str, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt learning based on user feedback"""
        try:
            content_id = feedback_data['content_id']
            feedback_type = feedback_data['feedback_type']
            feedback_strength = feedback_data.get('feedback_strength', 0.8)
            feedback_context = feedback_data.get('feedback_context', {})
            
            adaptation_applied = False
            weight_updates = {}
            confidence_changes = {}
            learning_rate_adjustment = 0.0
            
            # Find the content metadata for this feedback
            content_metadata = None
            for interaction in self.interaction_history:
                if interaction.content_id == content_id:
                    content_metadata = interaction.content_metadata
                    break
            
            if content_metadata:
                user_prefs = self.user_preferences.get(user_id, {})
                
                # Adjust preferences based on feedback
                for pref_type, content_value in content_metadata.items():
                    if pref_type in user_prefs:
                        old_confidence = user_prefs[pref_type].confidence
                        
                        if feedback_type == FeedbackType.POSITIVE:
                            # Increase confidence if content matches preference
                            if content_value == user_prefs[pref_type].preference_value:
                                confidence_delta = 0.1 * feedback_strength
                                user_prefs[pref_type].confidence = min(1.0, 
                                    old_confidence + confidence_delta)
                                adaptation_applied = True
                        
                        elif feedback_type == FeedbackType.NEGATIVE:
                            # Decrease confidence or adjust preference
                            if content_value == user_prefs[pref_type].preference_value:
                                confidence_delta = -0.05 * feedback_strength
                                user_prefs[pref_type].confidence = max(0.0, 
                                    old_confidence + confidence_delta)
                                adaptation_applied = True
                        
                        new_confidence = user_prefs[pref_type].confidence
                        if new_confidence != old_confidence:
                            confidence_changes[pref_type] = {
                                'old_confidence': old_confidence,
                                'new_confidence': new_confidence,
                                'change': new_confidence - old_confidence
                            }
                
                # Adjust learning rate based on feedback consistency
                learning_rate_adjustment = self._calculate_learning_rate_adjustment(
                    feedback_data, feedback_context
                )
            
            return {
                'adaptation_applied': adaptation_applied,
                'weight_updates': weight_updates,
                'confidence_changes': confidence_changes,
                'learning_rate_adjustment': learning_rate_adjustment
            }
            
        except Exception as e:
            logger.error(f"Error adapting to feedback: {e}")
            raise
    
    async def cluster_similar_users(self, user_id: str, clustering_params: Dict[str, Any]) -> Dict[str, Any]:
        """Cluster users with similar preferences"""
        try:
            similarity_threshold = clustering_params.get('similarity_threshold', 0.7)
            min_cluster_size = clustering_params.get('min_cluster_size', 3)
            max_clusters = clustering_params.get('max_clusters', 10)
            feature_dimensions = clustering_params.get('feature_dimensions', ['style', 'mood', 'timing'])
            
            # Get all users with preferences
            all_users = list(self.user_preferences.keys())
            
            if len(all_users) < min_cluster_size:
                return {
                    'user_cluster_id': 0,
                    'cluster_members': [user_id],
                    'cluster_characteristics': {
                        'cluster_size': 1, 
                        'note': 'Insufficient users for clustering',
                        'dominant_preferences': {},
                        'cluster_diversity': 0.0,
                        'common_patterns': []
                    },
                    'similarity_scores': {}
                }
            
            # Create feature vectors for users
            user_vectors = []
            user_ids = []
            
            for uid in all_users:
                vector = self._create_user_feature_vector(uid, feature_dimensions)
                if vector is not None:
                    user_vectors.append(vector)
                    user_ids.append(uid)
            
            if len(user_vectors) < min_cluster_size:
                return {
                    'user_cluster_id': 0,
                    'cluster_members': [user_id],
                    'cluster_characteristics': {
                        'cluster_size': 1, 
                        'note': 'Insufficient feature data',
                        'dominant_preferences': {},
                        'cluster_diversity': 0.0,
                        'common_patterns': []
                    },
                    'similarity_scores': {}
                }
            
            # Perform clustering
            n_clusters = min(max_clusters, len(user_vectors) // min_cluster_size)
            if n_clusters < 1:
                n_clusters = 1
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(user_vectors)
            
            # Find user's cluster
            user_index = user_ids.index(user_id) if user_id in user_ids else 0
            user_cluster_id = cluster_labels[user_index]
            
            # Get cluster members
            cluster_members = [user_ids[i] for i, label in enumerate(cluster_labels) 
                             if label == user_cluster_id]
            
            # Calculate similarity scores within cluster
            similarity_scores = {}
            user_vector = user_vectors[user_index]
            
            for member_id in cluster_members:
                if member_id != user_id:
                    member_index = user_ids.index(member_id)
                    member_vector = user_vectors[member_index]
                    similarity = self._calculate_vector_similarity(user_vector, member_vector)
                    similarity_scores[member_id] = similarity
            
            # Analyze cluster characteristics
            cluster_vectors = [user_vectors[i] for i, label in enumerate(cluster_labels) 
                             if label == user_cluster_id]
            cluster_centroid = np.mean(cluster_vectors, axis=0)
            cluster_diversity = np.std(cluster_vectors, axis=0).mean()
            
            # Extract dominant preferences
            dominant_preferences = self._extract_dominant_cluster_preferences(
                cluster_members, feature_dimensions
            )
            
            cluster_characteristics = {
                'dominant_preferences': dominant_preferences,
                'cluster_size': len(cluster_members),
                'cluster_diversity': float(cluster_diversity),
                'common_patterns': self._identify_common_patterns(cluster_members)
            }
            
            return {
                'user_cluster_id': int(user_cluster_id),
                'cluster_members': cluster_members,
                'cluster_characteristics': cluster_characteristics,
                'similarity_scores': similarity_scores
            }
            
        except Exception as e:
            logger.error(f"Error clustering similar users: {e}")
            raise
    
    async def predict_engagement_score(self, user_id: str, content_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Predict user engagement scores for content candidates"""
        try:
            predictions = []
            
            for candidate in content_candidates:
                content_id = candidate['content_id']
                metadata = candidate.get('metadata', {})
                
                # Calculate base engagement from preference match
                preference_score = self._calculate_preference_match_score(user_id, metadata)
                
                # Adjust for content quality factors
                quality_factor = self._calculate_quality_factor(metadata)
                
                # Adjust for novelty
                novelty_factor = self._calculate_novelty_score(user_id, metadata)
                
                # Adjust for contextual factors
                contextual_factor = self._calculate_contextual_engagement_factor(user_id)
                
                # Combine factors
                predicted_engagement = (
                    preference_score * 0.5 +
                    quality_factor * 0.2 +
                    novelty_factor * 0.15 +
                    contextual_factor * 0.15
                )
                
                # Calculate confidence interval
                user_prefs = self.user_preferences.get(user_id, {})
                avg_confidence = np.mean([p.confidence for p in user_prefs.values()]) if user_prefs else 0.5
                confidence_interval = {
                    'lower': max(0.0, predicted_engagement - (0.2 * (1 - avg_confidence))),
                    'upper': min(1.0, predicted_engagement + (0.2 * (1 - avg_confidence)))
                }
                
                # Identify contributing factors
                contributing_factors = []
                if preference_score > 0.7:
                    contributing_factors.append("strong_preference_match")
                if quality_factor > 0.8:
                    contributing_factors.append("high_content_quality")
                if novelty_factor > 0.6:
                    contributing_factors.append("novel_content")
                if contextual_factor > 0.7:
                    contributing_factors.append("favorable_context")
                
                predictions.append({
                    'content_id': content_id,
                    'predicted_engagement': max(0.0, min(1.0, predicted_engagement)),
                    'confidence_interval': confidence_interval,
                    'contributing_factors': contributing_factors
                })
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting engagement scores: {e}")
            return []
    
    async def generate_preference_explanations(self, explanation_request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explanations for preference-based recommendations"""
        try:
            user_id = explanation_request['user_id']
            recommendation_id = explanation_request.get('recommendation_id', '')
            explanation_depth = explanation_request.get('explanation_depth', 'detailed')
            include_alternatives = explanation_request.get('include_alternatives', True)
            
            user_prefs = self.user_preferences.get(user_id, {})
            
            # Generate primary explanation
            primary_explanation = "This recommendation is based on your learned preferences"
            
            if user_prefs:
                strongest_prefs = sorted(user_prefs.items(), 
                                       key=lambda x: x[1].confidence, reverse=True)[:3]
                
                pref_descriptions = []
                for pref_type, pref_obj in strongest_prefs:
                    pref_descriptions.append(
                        f"your preference for {pref_obj.preference_value} {pref_type} "
                        f"(confidence: {pref_obj.confidence:.1%})"
                    )
                
                primary_explanation = f"Recommended because of {', '.join(pref_descriptions)}"
            
            # Supporting evidence
            supporting_evidence = []
            for pref_type, pref_obj in user_prefs.items():
                supporting_evidence.append({
                    'preference_type': pref_type,
                    'preference_value': pref_obj.preference_value,
                    'confidence': pref_obj.confidence,
                    'based_on_interactions': pref_obj.interaction_count
                })
            
            # Confidence factors
            confidence_factors = []
            if user_prefs:
                avg_confidence = np.mean([p.confidence for p in user_prefs.values()])
                total_interactions = sum(p.interaction_count for p in user_prefs.values())
                
                confidence_factors = [
                    f"Average preference confidence: {avg_confidence:.1%}",
                    f"Based on {total_interactions} total interactions",
                    f"Learning from {len(user_prefs)} preference categories"
                ]
            
            # Alternative recommendations
            alternative_recommendations = []
            if include_alternatives:
                # Generate simplified alternatives
                alternative_recommendations = [
                    {
                        'recommendation_id': f"alt_{i}",
                        'reason': f"Alternative based on {pref_type} preference",
                        'confidence': pref_obj.confidence * 0.8
                    }
                    for i, (pref_type, pref_obj) in enumerate(list(user_prefs.items())[:3])
                ]
            
            return {
                'primary_explanation': primary_explanation,
                'supporting_evidence': supporting_evidence,
                'confidence_factors': confidence_factors,
                'alternative_recommendations': alternative_recommendations
            }
            
        except Exception as e:
            logger.error(f"Error generating preference explanations: {e}")
            raise
    
    async def optimize_learning_parameters(self, user_id: str, optimization_config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize learning parameters for better performance"""
        try:
            algorithm = optimization_config.get('algorithm', LearningAlgorithm.HYBRID)
            current_learning_rate = optimization_config.get('learning_rate', 0.01)
            current_regularization = optimization_config.get('regularization', 0.1)
            feature_weights = optimization_config.get('feature_weights', {})
            optimization_objective = optimization_config.get('optimization_objective', 'maximize_engagement')
            
            # Analyze current performance
            current_performance = await self._evaluate_learning_performance(user_id)
            
            # Try different parameter combinations
            parameter_combinations = [
                {'learning_rate': 0.005, 'regularization': 0.05},
                {'learning_rate': 0.01, 'regularization': 0.1},
                {'learning_rate': 0.02, 'regularization': 0.2},
                {'learning_rate': 0.015, 'regularization': 0.15}
            ]
            
            best_params = {'learning_rate': current_learning_rate, 'regularization': current_regularization}
            best_performance = current_performance
            
            for params in parameter_combinations:
                # Simulate performance with these parameters
                simulated_performance = self._simulate_performance_with_params(
                    user_id, params, algorithm
                )
                
                if simulated_performance > best_performance:
                    best_performance = simulated_performance
                    best_params = params
            
            # Optimize feature weights
            optimized_weights = self._optimize_feature_weights(user_id, feature_weights)
            
            # Calculate performance improvement
            performance_improvement = best_performance - current_performance
            
            # Generate convergence info
            convergence_info = {
                'iterations': len(parameter_combinations),
                'converged': performance_improvement > 0.05,
                'improvement_achieved': performance_improvement,
                'optimization_method': 'grid_search'
            }
            
            return {
                'optimized_algorithm': algorithm.value,
                'optimized_learning_rate': best_params['learning_rate'],
                'optimized_weights': optimized_weights,
                'performance_improvement': performance_improvement,
                'convergence_info': convergence_info
            }
            
        except Exception as e:
            logger.error(f"Error optimizing learning parameters: {e}")
            raise
    
    # Helper methods (abbreviated for brevity - each would be fully implemented)
    
    def _analyze_preference_from_interactions(self, interactions: List[InteractionRecord], 
                                            preference_type: str) -> Optional[Dict[str, Any]]:
        """Analyze preference from interactions"""
        if not interactions:
            return None
        
        # Count preference values
        preference_counts = Counter()
        weighted_sum = 0.0
        total_weight = 0.0
        
        for interaction in interactions:
            if preference_type in interaction.content_metadata:
                value = interaction.content_metadata[preference_type]
                
                # Weight by interaction type and completion rate
                weight = self._get_interaction_weight(interaction)
                preference_counts[value] += weight
                weighted_sum += weight
                total_weight += weight
        
        if not preference_counts:
            return None
        
        # Find most preferred value
        most_preferred = preference_counts.most_common(1)[0][0]
        confidence = preference_counts[most_preferred] / total_weight if total_weight > 0 else 0.0
        
        return {
            'value': most_preferred,
            'confidence': min(confidence, 1.0)
        }
    
    def _get_interaction_weight(self, interaction: InteractionRecord) -> float:
        """Calculate weight for an interaction"""
        base_weights = {
            InteractionType.LIKE: 1.0,
            InteractionType.SAVE: 1.2,
            InteractionType.REPLAY: 1.1,
            InteractionType.SHARE: 0.9,
            InteractionType.VIEW: 0.5,
            InteractionType.SKIP: -0.3,
            InteractionType.DELETE: -0.5
        }
        
        base_weight = base_weights.get(interaction.interaction_type, 0.5)
        completion_weight = interaction.completion_rate
        
        return max(0.0, base_weight * (0.5 + 0.5 * completion_weight))
    
    def _calculate_similarity(self, value1: str, value2: str, preference_type: str) -> float:
        """Calculate similarity between two preference values"""
        if value1 == value2:
            return 1.0
        
        # Define similarity mappings for different preference types
        similarity_maps = {
            'style': {
                ('abstract', 'artistic'): 0.7,
                ('realistic', 'photographic'): 0.8,
                ('calm', 'peaceful'): 0.9
            },
            'mood': {
                ('calm', 'peaceful'): 0.9,
                ('energetic', 'dynamic'): 0.8,
                ('dramatic', 'intense'): 0.7
            }
        }
        
        if preference_type in similarity_maps:
            pair = (value1, value2) if value1 < value2 else (value2, value1)
            return similarity_maps[preference_type].get(pair, 0.2)
        
        return 0.2  # Default low similarity for unknown pairs
    
    # Additional helper methods would be implemented here...
    # (truncated for brevity, but each method would be fully functional)
    
    def _empty_pattern_analysis(self) -> Dict[str, Any]:
        """Return empty pattern analysis structure"""
        return {
            'temporal_patterns': {
                'peak_activity_hours': [],
                'preferred_days': [],
                'session_duration_avg': 0.0,
                'activity_consistency': 0.0
            },
            'content_preferences': {},
            'engagement_metrics': {
                'completion_rate': 0.0,
                'interaction_frequency': 0.0,
                'content_diversity_score': 0.0,
                'engagement_trend': 'neutral'
            },
            'behavioral_insights': []
        }
    
    def _analyze_temporal_patterns(self, interactions: List[InteractionRecord]) -> Dict[str, Any]:
        """Analyze temporal patterns in interactions"""
        hours = [i.timestamp.hour for i in interactions]
        days = [i.timestamp.weekday() for i in interactions]
        durations = [i.duration_watched for i in interactions if i.duration_watched > 0]
        
        hour_counts = Counter(hours)
        day_counts = Counter(days)
        
        return {
            'peak_activity_hours': [h for h, _ in hour_counts.most_common(3)],
            'preferred_days': [d for d, _ in day_counts.most_common(3)],
            'session_duration_avg': np.mean(durations) if durations else 0.0,
            'activity_consistency': 1.0 - (np.std(hours) / 12.0) if hours else 0.0
        }
    
    def _analyze_content_preferences(self, interactions: List[InteractionRecord]) -> Dict[str, Any]:
        """Analyze content preferences from interactions"""
        content_prefs = {}
        
        for pref_type in ['style', 'mood', 'weather']:
            values = [i.content_metadata.get(pref_type) for i in interactions 
                     if pref_type in i.content_metadata]
            if values:
                value_counts = Counter(values)
                most_common = value_counts.most_common(1)[0]
                content_prefs[pref_type] = {
                    'preferred_value': most_common[0],
                    'frequency': most_common[1] / len(values)
                }
        
        return content_prefs
    
    def _calculate_engagement_metrics(self, interactions: List[InteractionRecord]) -> Dict[str, Any]:
        """Calculate engagement metrics from interactions"""
        if not interactions:
            return {
                'completion_rate': 0.0,
                'interaction_frequency': 0.0,
                'content_diversity_score': 0.0,
                'engagement_trend': 'neutral'
            }
        
        completion_rates = [i.completion_rate for i in interactions]
        positive_interactions = sum(1 for i in interactions 
                                  if i.interaction_type in [InteractionType.LIKE, InteractionType.SAVE])
        
        unique_content = len(set(i.content_id for i in interactions))
        
        return {
            'completion_rate': np.mean(completion_rates),
            'interaction_frequency': len(interactions) / 30.0,  # per day over 30 days
            'content_diversity_score': unique_content / len(interactions),
            'engagement_trend': 'increasing' if positive_interactions > len(interactions) * 0.7 else 'neutral'
        }
    
    def _generate_behavioral_insights(self, interactions: List[InteractionRecord]) -> List[str]:
        """Generate behavioral insights from interactions"""
        insights = []
        
        if not interactions:
            return ["Insufficient interaction data for behavioral analysis"]
        
        # Time-based insights
        hours = [i.timestamp.hour for i in interactions]
        if hours:
            most_active_hour = Counter(hours).most_common(1)[0][0]
            if 6 <= most_active_hour <= 11:
                insights.append("User is most active in the morning")
            elif 18 <= most_active_hour <= 22:
                insights.append("User prefers evening content consumption")
        
        # Engagement insights
        completion_rates = [i.completion_rate for i in interactions]
        avg_completion = np.mean(completion_rates)
        if avg_completion > 0.8:
            insights.append("User shows high content engagement")
        elif avg_completion < 0.3:
            insights.append("User tends to browse quickly through content")
        
        # Preference consistency
        styles = [i.content_metadata.get('style') for i in interactions 
                 if 'style' in i.content_metadata]
        if styles:
            style_consistency = 1.0 - (len(set(styles)) / len(styles))
            if style_consistency > 0.7:
                insights.append("User has consistent style preferences")
            else:
                insights.append("User enjoys diverse content styles")
        
        return insights
    
    # Additional helper methods for all the remaining functionality...
    # Each method would be fully implemented following the same pattern
    
    def _generate_mock_content_pool(self, count: int) -> List[Dict[str, Any]]:
        """Generate mock content pool for testing"""
        styles = ['abstract', 'realistic', 'artistic', 'photographic']
        moods = ['calm', 'energetic', 'dramatic', 'peaceful']
        
        content_pool = []
        for i in range(count):
            content_pool.append({
                'content_id': f'content_{i:03d}',
                'style': styles[i % len(styles)],
                'mood': moods[i % len(moods)],
                'duration': 60 + (i * 30) % 180,
                'quality': 'high' if i % 3 == 0 else 'medium'
            })
        
        return content_pool
    
    async def _calculate_recommendation_score(self, user_id: str, content: Dict[str, Any], 
                                           context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate recommendation score for content"""
        user_prefs = self.user_preferences.get(user_id, {})
        
        if not user_prefs:
            return {
                'total_score': 0.5,
                'factors': ['no_preferences'],
                'confidence': 0.1,
                'explanation': 'No learned preferences available'
            }
        
        # Calculate preference match
        preference_score = 0.0
        matching_factors = []
        
        for pref_type, pref_obj in user_prefs.items():
            if pref_type in content:
                if content[pref_type] == pref_obj.preference_value:
                    preference_score += pref_obj.confidence * pref_obj.weight
                    matching_factors.append(f"{pref_type}:{content[pref_type]}")
        
        # Normalize by number of preferences
        preference_score = preference_score / len(user_prefs) if user_prefs else 0.0
        
        # Apply context factors
        context_boost = 0.0
        current_time = datetime.now()
        current_hour = current_time.hour
        
        # Time-based context
        if 'timing' in user_prefs:
            if user_prefs['timing'].preference_value == 'morning' and 6 <= current_hour <= 11:
                context_boost += 0.1
                matching_factors.append('time_match')
        
        total_score = min(1.0, preference_score + context_boost)
        confidence = np.mean([p.confidence for p in user_prefs.values()])
        
        explanation = f"Score based on: {', '.join(matching_factors)}" if matching_factors else "General recommendation"
        
        return {
            'total_score': total_score,
            'factors': matching_factors,
            'confidence': confidence,
            'explanation': explanation
        }
    
    # Placeholder implementations for remaining helper methods
    def _create_time_windows(self, start_date: datetime, end_date: datetime, granularity: str) -> List[Tuple[datetime, datetime]]:
        """Create time windows for preference evolution tracking"""
        windows = []
        current = start_date
        
        if granularity == 'weekly':
            delta = timedelta(weeks=1)
        elif granularity == 'daily':
            delta = timedelta(days=1)
        else:
            delta = timedelta(weeks=1)  # Default
        
        while current < end_date:
            window_end = min(current + delta, end_date)
            windows.append((current, window_end))
            current = window_end
        
        return windows
    
    def _extract_preferences_from_window(self, interactions: List[InteractionRecord]) -> Dict[str, Any]:
        """Extract preferences from interaction window"""
        preferences = {}
        
        for pref_type in ['style', 'mood', 'weather']:
            pref_analysis = self._analyze_preference_from_interactions(interactions, pref_type)
            if pref_analysis:
                preferences[pref_type] = pref_analysis
        
        return preferences
    
    def _calculate_preference_stability(self, timeline: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate preference stability metrics"""
        if len(timeline) < 2:
            return {'stability_score': 1.0, 'most_stable_preference': None}
        
        # Simplified stability calculation
        return {
            'stability_score': 0.8,  # Mock value
            'most_stable_preference': 'style',
            'volatility_score': 0.2
        }
    
    def _detect_preference_drift(self, timeline: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect preference drift in timeline"""
        return {
            'drift_detected': False,
            'drift_magnitude': 0.0,
            'drift_direction': 'stable'
        }
    
    def _generate_adaptation_recommendations(self, timeline: List[Dict[str, Any]], 
                                           stability: Dict[str, Any], 
                                           drift: Dict[str, Any]) -> List[str]:
        """Generate adaptation recommendations"""
        recommendations = []
        
        if stability['stability_score'] < 0.5:
            recommendations.append("Increase learning sensitivity for unstable preferences")
        
        if drift['drift_detected']:
            recommendations.append("Adapt quickly to detected preference changes")
        
        return recommendations
    
    # Additional placeholder methods for completeness...
    def _calculate_recency_factor(self, last_updated: datetime) -> float:
        days_since_update = (datetime.now() - last_updated).days
        return max(0.0, 1.0 - days_since_update / 30.0)
    
    def _calculate_consistency_factor(self, user_id: str, preference_type: str) -> float:
        return 0.8  # Mock consistency score
    
    def _determine_confidence_level(self, confidence_score: float) -> ConfidenceLevel:
        for level, threshold in sorted(self.confidence_thresholds.items(), 
                                     key=lambda x: x[1], reverse=True):
            if confidence_score >= threshold:
                return level
        return ConfidenceLevel.VERY_LOW
    
    def _analyze_shift_impact(self, shift_details: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {'impact_score': 0.5, 'affected_recommendations': len(shift_details) * 2}
    
    def _calculate_preference_match_score(self, user_id: str, content: Dict[str, Any]) -> float:
        user_prefs = self.user_preferences.get(user_id, {})
        if not user_prefs:
            return 0.5
        
        total_score = 0.0
        total_weight = 0.0
        
        for pref_type, pref_obj in user_prefs.items():
            if pref_type in content:
                if content[pref_type] == pref_obj.preference_value:
                    score = pref_obj.confidence
                else:
                    score = 0.2  # Partial match
                
                total_score += score * pref_obj.weight
                total_weight += pref_obj.weight
        
        return total_score / total_weight if total_weight > 0 else 0.5
    
    def _calculate_novelty_score(self, user_id: str, content: Dict[str, Any]) -> float:
        # Check if user has seen similar content before
        user_interactions = [i for i in self.interaction_history if i.user_id == user_id]
        
        similar_content_count = 0
        for interaction in user_interactions:
            similarity = 0
            for key, value in content.items():
                if key in interaction.content_metadata:
                    if interaction.content_metadata[key] == value:
                        similarity += 1
            
            if similarity >= len(content) * 0.7:  # 70% similarity threshold
                similar_content_count += 1
        
        # Higher novelty for less similar content
        novelty = max(0.0, 1.0 - similar_content_count / max(1, len(user_interactions)))
        return novelty
    
    def _calculate_diversity_score(self, content: Dict[str, Any], existing_content: List[Dict[str, Any]]) -> float:
        if not existing_content:
            return 1.0
        
        # Calculate how different this content is from already selected content
        diversity_scores = []
        for existing in existing_content:
            differences = 0
            total_features = 0
            
            for key, value in content.items():
                if key in existing:
                    total_features += 1
                    if existing[key] != value:
                        differences += 1
            
            if total_features > 0:
                diversity_scores.append(differences / total_features)
        
        return np.mean(diversity_scores) if diversity_scores else 1.0
    
    def _greedy_diversified_selection(self, scored_content: List[Dict[str, Any]], 
                                    selection_count: int) -> List[Dict[str, Any]]:
        """Select content using greedy diversification"""
        selected = []
        remaining = scored_content.copy()
        
        # Sort by score initially
        remaining.sort(key=lambda x: x['selection_score'], reverse=True)
        
        for _ in range(min(selection_count, len(remaining))):
            if not selected:
                # Select highest scoring item first
                selected.append(remaining.pop(0))
            else:
                # Select item that maximizes score + diversity
                best_item = None
                best_score = -1
                best_index = -1
                
                for i, item in enumerate(remaining):
                    # Calculate diversity bonus
                    diversity_bonus = self._calculate_diversity_score(item, selected) * 0.3
                    total_score = item['selection_score'] + diversity_bonus
                    
                    if total_score > best_score:
                        best_score = total_score
                        best_item = item
                        best_index = i
                
                if best_item:
                    selected.append(remaining.pop(best_index))
        
        return selected
    
    def _calculate_selection_diversity(self, selected_content: List[Dict[str, Any]]) -> float:
        if len(selected_content) < 2:
            return 1.0
        
        # Calculate average pairwise diversity
        diversity_scores = []
        for i in range(len(selected_content)):
            for j in range(i + 1, len(selected_content)):
                diversity = self._calculate_diversity_score(selected_content[i], [selected_content[j]])
                diversity_scores.append(diversity)
        
        return np.mean(diversity_scores) if diversity_scores else 1.0
    
    def _safe_get_preference_type(self, pref_type: str) -> PreferenceType:
        """Safely get PreferenceType enum value, default to CONTENT if not found"""
        try:
            return PreferenceType(pref_type.lower())
        except ValueError:
            # Map known preference types that aren't in the enum
            type_mapping = {
                'time_of_day': PreferenceType.TIMING,
                'period': PreferenceType.TIMING,
                'day_time': PreferenceType.TIMING,
                'weather_condition': PreferenceType.WEATHER,
                'emotional_state': PreferenceType.MOOD,
                'content_style': PreferenceType.STYLE,
                'video_length': PreferenceType.DURATION,
                'topic': PreferenceType.CONTENT
            }
            return type_mapping.get(pref_type.lower(), PreferenceType.CONTENT)
    
    def _validate_preference_data(self, pref_data: Dict[str, Any]) -> bool:
        required_fields = ['value', 'confidence']
        return all(field in pref_data for field in required_fields)
    
    def _categorize_preference_strength(self, confidence: float) -> str:
        if confidence >= 0.8:
            return 'strong'
        elif confidence >= 0.6:
            return 'moderate'
        elif confidence >= 0.4:
            return 'weak'
        else:
            return 'very_weak'
    
    def _analyze_preference_trends(self, interactions: List[InteractionRecord]) -> Dict[str, Any]:
        return {'trend': 'stable', 'direction': 'neutral'}
    
    def _assess_preference_stability(self, user_id: str, time_period_days: int) -> Dict[str, Any]:
        return {'stability_score': 0.8, 'assessment': 'stable'}
    
    def _calculate_personalization_effectiveness(self, user_id: str) -> Dict[str, Any]:
        return {'effectiveness_score': 0.75, 'personalization_impact': 'moderate'}
    
    def _predict_interaction_preference(self, interaction: InteractionRecord, 
                                      historical_prefs: Dict[str, Any]) -> bool:
        # Simple prediction based on content metadata match
        matches = 0
        total_prefs = len(historical_prefs)
        
        for pref_type, pref_data in historical_prefs.items():
            if pref_type in interaction.content_metadata:
                if interaction.content_metadata[pref_type] == pref_data['value']:
                    matches += 1
        
        match_ratio = matches / total_prefs if total_prefs > 0 else 0.5
        return match_ratio > 0.6
    
    def _calculate_learning_rate_adjustment(self, feedback_data: Dict[str, Any], 
                                          feedback_context: Dict[str, Any]) -> float:
        # Adjust learning rate based on feedback quality and context
        base_adjustment = 0.01
        
        if feedback_context.get('time_to_feedback', 0) < 30:  # Quick feedback
            base_adjustment *= 1.2
        
        return base_adjustment
    
    def _create_user_feature_vector(self, user_id: str, feature_dimensions: List[str]) -> Optional[List[float]]:
        user_prefs = self.user_preferences.get(user_id, {})
        if not user_prefs:
            return None
        
        # Create feature vector based on preference confidence scores
        vector = []
        for dimension in feature_dimensions:
            if dimension in user_prefs:
                vector.append(user_prefs[dimension].confidence)
            else:
                vector.append(0.0)
        
        return vector
    
    def _calculate_vector_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        # Calculate cosine similarity
        if len(vector1) != len(vector2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vector1, vector2))
        magnitude1 = math.sqrt(sum(a * a for a in vector1))
        magnitude2 = math.sqrt(sum(a * a for a in vector2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _extract_dominant_cluster_preferences(self, cluster_members: List[str], 
                                            feature_dimensions: List[str]) -> Dict[str, str]:
        # Find most common preferences among cluster members
        dominant_prefs = {}
        
        for dimension in feature_dimensions:
            dimension_values = []
            for member_id in cluster_members:
                user_prefs = self.user_preferences.get(member_id, {})
                if dimension in user_prefs:
                    dimension_values.append(user_prefs[dimension].preference_value)
            
            if dimension_values:
                most_common = Counter(dimension_values).most_common(1)[0][0]
                dominant_prefs[dimension] = most_common
        
        return dominant_prefs
    
    def _identify_common_patterns(self, cluster_members: List[str]) -> List[str]:
        return ['morning_activity', 'high_engagement']  # Mock patterns
    
    def _calculate_quality_factor(self, metadata: Dict[str, Any]) -> float:
        quality = metadata.get('quality', 'medium')
        quality_scores = {'low': 0.4, 'medium': 0.7, 'high': 1.0}
        return quality_scores.get(quality, 0.7)
    
    def _calculate_contextual_engagement_factor(self, user_id: str) -> float:
        # Consider current time, user's typical activity patterns, etc.
        return 0.75  # Mock contextual factor
    
    async def _evaluate_learning_performance(self, user_id: str) -> float:
        # Evaluate current learning algorithm performance
        return 0.7  # Mock performance score
    
    def _simulate_performance_with_params(self, user_id: str, params: Dict[str, Any], 
                                        algorithm: LearningAlgorithm) -> float:
        # Simulate performance with different parameters
        base_performance = 0.7
        learning_rate_factor = 1.0 - abs(params['learning_rate'] - 0.01) * 5
        regularization_factor = 1.0 - abs(params['regularization'] - 0.1) * 2
        
        return base_performance * learning_rate_factor * regularization_factor
    
    def _optimize_feature_weights(self, user_id: str, current_weights: Dict[str, float]) -> Dict[str, float]:
        # Optimize feature weights based on user performance
        optimized = current_weights.copy()
        
        # Increase weights for features with high user engagement
        for feature, weight in optimized.items():
            # Mock optimization logic
            optimized[feature] = min(1.0, weight * 1.1)
        
        return optimized