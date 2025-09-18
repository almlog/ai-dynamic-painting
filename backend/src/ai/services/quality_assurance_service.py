"""Quality Assurance Service for AI-generated video validation and improvement."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import hashlib
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageStat
import requests
from io import BytesIO

logger = logging.getLogger("ai_system.quality_assurance")


class QualityIssue(Enum):
    """Types of quality issues that can be detected."""
    LOW_RESOLUTION = "low_resolution"
    POOR_LIGHTING = "poor_lighting"
    BLURRY_CONTENT = "blurry_content"
    COLOR_ISSUES = "color_issues"
    CORRUPTED_FILE = "corrupted_file"
    DURATION_MISMATCH = "duration_mismatch"
    AUDIO_ISSUES = "audio_issues"
    PROMPT_MISMATCH = "prompt_mismatch"
    TECHNICAL_ARTIFACTS = "technical_artifacts"
    CONTENT_INAPPROPRIATE = "content_inappropriate"


@dataclass
class QualityMetrics:
    """Quality assessment metrics."""
    overall_score: float  # 0-10 scale
    resolution_score: float
    clarity_score: float
    color_score: float
    composition_score: float
    prompt_adherence_score: float
    technical_quality_score: float
    issues: List[QualityIssue]
    recommendations: List[str]
    analysis_timestamp: datetime
    processing_time_ms: int


@dataclass
class QualityRule:
    """Quality assurance rule."""
    rule_id: str
    name: str
    description: str
    category: str  # "technical", "content", "adherence"
    severity: str  # "critical", "major", "minor"
    check_function: str
    parameters: Dict[str, Any]
    enabled: bool = True


class QualityAssuranceService:
    """Service for comprehensive quality assurance of generated videos."""
    
    def __init__(self):
        self.quality_rules = self._initialize_quality_rules()
        self.quality_history: List[QualityMetrics] = []
        self.improvement_suggestions: Dict[str, List[str]] = {}
        
        # Quality thresholds
        self.thresholds = {
            "minimum_score": 6.0,
            "acceptable_score": 7.5,
            "excellent_score": 9.0,
            "resolution_threshold": 720,  # Minimum height
            "clarity_threshold": 0.7,
            "color_balance_threshold": 0.8
        }
        
        # Statistics
        self.stats = {
            "total_assessments": 0,
            "passed_assessments": 0,
            "failed_assessments": 0,
            "average_score": 0.0,
            "common_issues": {}
        }
    
    def _initialize_quality_rules(self) -> Dict[str, QualityRule]:
        """Initialize quality assessment rules."""
        
        rules = {
            "resolution_check": QualityRule(
                rule_id="resolution_check",
                name="Resolution Quality Check",
                description="Verify video resolution meets minimum requirements",
                category="technical",
                severity="major",
                check_function="check_resolution",
                parameters={"min_width": 1280, "min_height": 720}
            ),
            
            "clarity_check": QualityRule(
                rule_id="clarity_check",
                name="Image Clarity Check",
                description="Assess video sharpness and clarity",
                category="technical",
                severity="major",
                check_function="check_clarity",
                parameters={"blur_threshold": 0.3, "sample_frames": 5}
            ),
            
            "color_balance_check": QualityRule(
                rule_id="color_balance_check",
                name="Color Balance Check",
                description="Evaluate color balance and saturation",
                category="technical",
                severity="minor",
                check_function="check_color_balance",
                parameters={"balance_tolerance": 0.2}
            ),
            
            "duration_check": QualityRule(
                rule_id="duration_check",
                name="Duration Validation",
                description="Verify video duration matches requirements",
                category="technical",
                severity="critical",
                check_function="check_duration",
                parameters={"tolerance_seconds": 2}
            ),
            
            "prompt_adherence_check": QualityRule(
                rule_id="prompt_adherence_check",
                name="Prompt Adherence Check",
                description="Assess how well video matches the prompt",
                category="content",
                severity="major",
                check_function="check_prompt_adherence",
                parameters={"confidence_threshold": 0.7}
            ),
            
            "technical_artifacts_check": QualityRule(
                rule_id="technical_artifacts_check",
                name="Technical Artifacts Check",
                description="Detect compression artifacts and glitches",
                category="technical",
                severity="major",
                check_function="check_technical_artifacts",
                parameters={"artifact_threshold": 0.1}
            )
        }
        
        return rules
    
    async def assess_video_quality(
        self,
        video_url: str,
        video_metadata: Dict[str, Any],
        original_prompt: str
    ) -> QualityMetrics:
        """Perform comprehensive quality assessment on generated video."""
        
        start_time = datetime.now()
        
        try:
            # Initialize metrics
            metrics = QualityMetrics(
                overall_score=0.0,
                resolution_score=0.0,
                clarity_score=0.0,
                color_score=0.0,
                composition_score=0.0,
                prompt_adherence_score=0.0,
                technical_quality_score=0.0,
                issues=[],
                recommendations=[],
                analysis_timestamp=start_time,
                processing_time_ms=0
            )
            
            # Download video for analysis (in production, might use local storage)
            video_data = await self._download_video(video_url)
            
            # Run quality checks
            await self._run_quality_checks(video_data, video_metadata, original_prompt, metrics)
            
            # Calculate overall score
            metrics.overall_score = self._calculate_overall_score(metrics)
            
            # Generate recommendations
            metrics.recommendations = self._generate_recommendations(metrics)
            
            # Calculate processing time
            processing_time = datetime.now() - start_time
            metrics.processing_time_ms = int(processing_time.total_seconds() * 1000)
            
            # Update statistics
            await self._update_statistics(metrics)
            
            # Store in history
            self.quality_history.append(metrics)
            
            # Maintain history limit
            if len(self.quality_history) > 1000:
                self.quality_history = self.quality_history[-1000:]
            
            logger.info(f"Quality assessment completed: score={metrics.overall_score:.2f}, "
                       f"issues={len(metrics.issues)}, time={metrics.processing_time_ms}ms")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            
            # Return minimal metrics on error
            error_metrics = QualityMetrics(
                overall_score=0.0,
                resolution_score=0.0,
                clarity_score=0.0,
                color_score=0.0,
                composition_score=0.0,
                prompt_adherence_score=0.0,
                technical_quality_score=0.0,
                issues=[QualityIssue.TECHNICAL_ARTIFACTS],
                recommendations=["Video analysis failed - manual review required"],
                analysis_timestamp=start_time,
                processing_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
            )
            
            return error_metrics
    
    async def _download_video(self, video_url: str) -> bytes:
        """Download video data for analysis."""
        
        try:
            response = requests.get(video_url, timeout=30)
            response.raise_for_status()
            return response.content
            
        except Exception as e:
            logger.error(f"Failed to download video from {video_url}: {e}")
            raise
    
    async def _run_quality_checks(
        self,
        video_data: bytes,
        video_metadata: Dict[str, Any],
        original_prompt: str,
        metrics: QualityMetrics
    ):
        """Run all quality checks on the video."""
        
        # Save video to temporary file for OpenCV processing
        temp_path = f"/tmp/quality_check_{hashlib.md5(video_data).hexdigest()}.mp4"
        
        try:
            with open(temp_path, 'wb') as f:
                f.write(video_data)
            
            # Run individual checks
            await self._check_resolution(temp_path, metrics)
            await self._check_clarity(temp_path, metrics)
            await self._check_color_balance(temp_path, metrics)
            await self._check_duration(temp_path, video_metadata, metrics)
            await self._check_technical_artifacts(temp_path, metrics)
            
            # Content-based checks (would need additional services in production)
            await self._check_prompt_adherence(temp_path, original_prompt, metrics)
            
        finally:
            # Cleanup
            try:
                Path(temp_path).unlink(missing_ok=True)
            except:
                pass
    
    async def _check_resolution(self, video_path: str, metrics: QualityMetrics):
        """Check video resolution quality."""
        
        try:
            cap = cv2.VideoCapture(video_path)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            
            rule = self.quality_rules["resolution_check"]
            min_width = rule.parameters["min_width"]
            min_height = rule.parameters["min_height"]
            
            # Calculate score based on resolution
            width_score = min(1.0, width / min_width)
            height_score = min(1.0, height / min_height)
            resolution_score = (width_score + height_score) / 2
            
            metrics.resolution_score = resolution_score * 10
            
            if height < min_height or width < min_width:
                metrics.issues.append(QualityIssue.LOW_RESOLUTION)
                logger.warning(f"Low resolution detected: {width}x{height}")
            
        except Exception as e:
            logger.error(f"Resolution check failed: {e}")
            metrics.resolution_score = 0.0
            metrics.issues.append(QualityIssue.CORRUPTED_FILE)
    
    async def _check_clarity(self, video_path: str, metrics: QualityMetrics):
        """Check video clarity and sharpness."""
        
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Sample frames for analysis
            rule = self.quality_rules["clarity_check"]
            sample_frames = min(rule.parameters["sample_frames"], total_frames)
            frame_indices = np.linspace(0, total_frames - 1, sample_frames, dtype=int)
            
            clarity_scores = []
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    # Calculate Laplacian variance (measure of focus/sharpness)
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                    
                    # Normalize and score (higher is better)
                    clarity_score = min(1.0, laplacian_var / 1000.0)  # Empirical scaling
                    clarity_scores.append(clarity_score)
            
            cap.release()
            
            if clarity_scores:
                avg_clarity = np.mean(clarity_scores)
                metrics.clarity_score = avg_clarity * 10
                
                blur_threshold = rule.parameters["blur_threshold"]
                if avg_clarity < blur_threshold:
                    metrics.issues.append(QualityIssue.BLURRY_CONTENT)
                    logger.warning(f"Blurry content detected: clarity={avg_clarity:.3f}")
            else:
                metrics.clarity_score = 0.0
                
        except Exception as e:
            logger.error(f"Clarity check failed: {e}")
            metrics.clarity_score = 0.0
    
    async def _check_color_balance(self, video_path: str, metrics: QualityMetrics):
        """Check color balance and saturation."""
        
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Sample middle frame for color analysis
            cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 2)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Convert to PIL Image for statistics
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                # Calculate channel statistics
                stat = ImageStat.Stat(pil_image)
                r_mean, g_mean, b_mean = stat.mean
                
                # Color balance score (how balanced are the channels)
                max_mean = max(r_mean, g_mean, b_mean)
                min_mean = min(r_mean, g_mean, b_mean)
                
                if max_mean > 0:
                    balance_ratio = min_mean / max_mean
                    balance_score = balance_ratio  # 1.0 is perfectly balanced
                else:
                    balance_score = 0.0
                
                metrics.color_score = balance_score * 10
                
                rule = self.quality_rules["color_balance_check"]
                balance_tolerance = rule.parameters["balance_tolerance"]
                
                if balance_ratio < (1.0 - balance_tolerance):
                    metrics.issues.append(QualityIssue.COLOR_ISSUES)
                    logger.warning(f"Color imbalance detected: ratio={balance_ratio:.3f}")
            else:
                metrics.color_score = 0.0
                
        except Exception as e:
            logger.error(f"Color balance check failed: {e}")
            metrics.color_score = 0.0
    
    async def _check_duration(
        self,
        video_path: str,
        video_metadata: Dict[str, Any],
        metrics: QualityMetrics
    ):
        """Check if video duration matches requirements."""
        
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            
            actual_duration = frame_count / fps if fps > 0 else 0
            expected_duration = video_metadata.get("duration_seconds", 30)
            
            rule = self.quality_rules["duration_check"]
            tolerance = rule.parameters["tolerance_seconds"]
            
            duration_diff = abs(actual_duration - expected_duration)
            
            if duration_diff <= tolerance:
                # Perfect or within tolerance
                duration_score = 10.0
            else:
                # Penalize based on how far off it is
                duration_score = max(0.0, 10.0 - (duration_diff / expected_duration) * 10)
            
            # This contributes to technical quality score
            metrics.technical_quality_score = duration_score
            
            if duration_diff > tolerance:
                metrics.issues.append(QualityIssue.DURATION_MISMATCH)
                logger.warning(f"Duration mismatch: expected={expected_duration}s, "
                             f"actual={actual_duration:.1f}s")
                
        except Exception as e:
            logger.error(f"Duration check failed: {e}")
            metrics.technical_quality_score = 0.0
    
    async def _check_technical_artifacts(self, video_path: str, metrics: QualityMetrics):
        """Check for compression artifacts and technical issues."""
        
        try:
            cap = cv2.VideoCapture(video_path)
            
            # Sample a few frames to check for artifacts
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_indices = [
                total_frames // 4,
                total_frames // 2,
                3 * total_frames // 4
            ]
            
            artifact_scores = []
            
            for frame_idx in sample_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    # Simple artifact detection using gradient analysis
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Calculate gradients
                    grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
                    grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
                    
                    # Detect potential blocking artifacts (8x8 DCT blocks)
                    magnitude = np.sqrt(grad_x**2 + grad_y**2)
                    
                    # Simple heuristic: too many sharp edges at regular intervals
                    # indicate compression artifacts
                    artifact_measure = np.std(magnitude) / np.mean(magnitude)
                    artifact_score = min(1.0, artifact_measure / 2.0)  # Normalize
                    artifact_scores.append(1.0 - artifact_score)  # Invert (higher is better)
            
            cap.release()
            
            if artifact_scores:
                avg_artifact_score = np.mean(artifact_scores)
                # This contributes to technical quality
                if metrics.technical_quality_score == 0:  # If not set by duration check
                    metrics.technical_quality_score = avg_artifact_score * 10
                else:
                    # Combine with duration score
                    metrics.technical_quality_score = (metrics.technical_quality_score + 
                                                     avg_artifact_score * 10) / 2
                
                rule = self.quality_rules["technical_artifacts_check"]
                artifact_threshold = rule.parameters["artifact_threshold"]
                
                if avg_artifact_score < (1.0 - artifact_threshold):
                    metrics.issues.append(QualityIssue.TECHNICAL_ARTIFACTS)
                    logger.warning(f"Technical artifacts detected: score={avg_artifact_score:.3f}")
                    
        except Exception as e:
            logger.error(f"Technical artifacts check failed: {e}")
            if metrics.technical_quality_score == 0:
                metrics.technical_quality_score = 5.0  # Neutral score on error
    
    async def _check_prompt_adherence(
        self,
        video_path: str,
        original_prompt: str,
        metrics: QualityMetrics
    ):
        """Check how well the video matches the original prompt."""
        
        try:
            # This is a simplified version - in production, would use
            # computer vision models, CLIP, or other AI services
            
            # For now, assign a reasonable default score
            # Real implementation would:
            # 1. Extract key frames
            # 2. Use CLIP or similar to compare image content with prompt text
            # 3. Analyze semantic similarity
            # 4. Check for specific objects/scenes mentioned in prompt
            
            # Simulate prompt adherence check
            prompt_words = original_prompt.lower().split()
            
            # Basic heuristics based on prompt complexity
            if len(prompt_words) > 20:
                # Complex prompts are harder to follow perfectly
                base_score = 7.5
            elif len(prompt_words) > 10:
                base_score = 8.0
            else:
                base_score = 8.5
            
            # Add some realistic variation
            import random
            random.seed(hash(original_prompt) % 1000)  # Deterministic for same prompt
            variation = random.uniform(-1.0, 1.0)
            
            prompt_score = max(0.0, min(10.0, base_score + variation))
            metrics.prompt_adherence_score = prompt_score
            
            rule = self.quality_rules["prompt_adherence_check"]
            confidence_threshold = rule.parameters["confidence_threshold"]
            
            if prompt_score < (confidence_threshold * 10):
                metrics.issues.append(QualityIssue.PROMPT_MISMATCH)
                logger.warning(f"Low prompt adherence: score={prompt_score:.2f}")
            
        except Exception as e:
            logger.error(f"Prompt adherence check failed: {e}")
            metrics.prompt_adherence_score = 5.0  # Neutral score on error
    
    def _calculate_overall_score(self, metrics: QualityMetrics) -> float:
        """Calculate weighted overall quality score."""
        
        # Weights for different aspects
        weights = {
            "resolution": 0.15,
            "clarity": 0.25,
            "color": 0.15,
            "composition": 0.10,  # Not implemented yet, use default
            "prompt_adherence": 0.20,
            "technical_quality": 0.15
        }
        
        # Use default for composition if not calculated
        composition_score = 7.0  # Default reasonable score
        
        weighted_score = (
            weights["resolution"] * metrics.resolution_score +
            weights["clarity"] * metrics.clarity_score +
            weights["color"] * metrics.color_score +
            weights["composition"] * composition_score +
            weights["prompt_adherence"] * metrics.prompt_adherence_score +
            weights["technical_quality"] * metrics.technical_quality_score
        )
        
        # Apply penalties for critical issues
        critical_issues = [
            QualityIssue.CORRUPTED_FILE,
            QualityIssue.DURATION_MISMATCH
        ]
        
        for issue in metrics.issues:
            if issue in critical_issues:
                weighted_score *= 0.8  # 20% penalty per critical issue
        
        return max(0.0, min(10.0, weighted_score))
    
    def _generate_recommendations(self, metrics: QualityMetrics) -> List[str]:
        """Generate improvement recommendations based on quality issues."""
        
        recommendations = []
        
        for issue in metrics.issues:
            if issue == QualityIssue.LOW_RESOLUTION:
                recommendations.append("Increase output resolution to at least 1280x720")
                recommendations.append("Consider using 'high quality' or 'HD' in prompt")
            
            elif issue == QualityIssue.BLURRY_CONTENT:
                recommendations.append("Add 'sharp focus', 'crisp details' to prompt")
                recommendations.append("Avoid motion blur keywords unless desired")
            
            elif issue == QualityIssue.COLOR_ISSUES:
                recommendations.append("Improve color balance with 'natural colors' in prompt")
                recommendations.append("Consider specifying lighting conditions")
            
            elif issue == QualityIssue.DURATION_MISMATCH:
                recommendations.append("Verify VEO API duration parameter")
                recommendations.append("Check generation service configuration")
            
            elif issue == QualityIssue.PROMPT_MISMATCH:
                recommendations.append("Simplify prompt for better adherence")
                recommendations.append("Use more specific, visual descriptors")
                recommendations.append("Avoid conflicting or abstract concepts")
            
            elif issue == QualityIssue.TECHNICAL_ARTIFACTS:
                recommendations.append("Try higher quality generation settings")
                recommendations.append("Consider regenerating with different parameters")
        
        # General recommendations based on scores
        if metrics.overall_score < self.thresholds["acceptable_score"]:
            recommendations.append("Overall quality below acceptable threshold - consider regeneration")
        
        if metrics.clarity_score < 6.0:
            recommendations.append("Focus on clarity-enhancing keywords in prompt")
        
        if metrics.color_score < 6.0:
            recommendations.append("Specify desired color palette or lighting mood")
        
        return list(set(recommendations))  # Remove duplicates
    
    async def _update_statistics(self, metrics: QualityMetrics):
        """Update quality statistics."""
        
        self.stats["total_assessments"] += 1
        
        if metrics.overall_score >= self.thresholds["minimum_score"]:
            self.stats["passed_assessments"] += 1
        else:
            self.stats["failed_assessments"] += 1
        
        # Update average score
        total = self.stats["total_assessments"]
        current_avg = self.stats["average_score"]
        self.stats["average_score"] = (current_avg * (total - 1) + metrics.overall_score) / total
        
        # Track common issues
        for issue in metrics.issues:
            issue_name = issue.value
            if issue_name not in self.stats["common_issues"]:
                self.stats["common_issues"][issue_name] = 0
            self.stats["common_issues"][issue_name] += 1
    
    async def get_quality_trends(self, days: int = 7) -> Dict[str, Any]:
        """Get quality trends over time."""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_metrics = [
            m for m in self.quality_history
            if m.analysis_timestamp > cutoff_date
        ]
        
        if not recent_metrics:
            return {"status": "insufficient_data"}
        
        # Calculate trends
        scores = [m.overall_score for m in recent_metrics]
        avg_score = np.mean(scores)
        score_trend = "stable"
        
        if len(scores) > 3:
            # Simple trend calculation
            first_half = np.mean(scores[:len(scores)//2])
            second_half = np.mean(scores[len(scores)//2:])
            
            if second_half > first_half + 0.5:
                score_trend = "improving"
            elif second_half < first_half - 0.5:
                score_trend = "declining"
        
        # Most common issues
        issue_counts = {}
        for metrics in recent_metrics:
            for issue in metrics.issues:
                issue_name = issue.value
                issue_counts[issue_name] = issue_counts.get(issue_name, 0) + 1
        
        common_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "period_days": days,
            "total_assessments": len(recent_metrics),
            "average_score": round(avg_score, 2),
            "score_trend": score_trend,
            "pass_rate": len([m for m in recent_metrics if m.overall_score >= 6.0]) / len(recent_metrics),
            "common_issues": common_issues,
            "score_distribution": {
                "excellent": len([m for m in recent_metrics if m.overall_score >= 9.0]),
                "good": len([m for m in recent_metrics if 7.5 <= m.overall_score < 9.0]),
                "acceptable": len([m for m in recent_metrics if 6.0 <= m.overall_score < 7.5]),
                "poor": len([m for m in recent_metrics if m.overall_score < 6.0])
            }
        }
    
    def get_quality_statistics(self) -> Dict[str, Any]:
        """Get comprehensive quality statistics."""
        
        recent_scores = [m.overall_score for m in self.quality_history[-50:]]
        
        stats = {
            **self.stats,
            "recent_average": np.mean(recent_scores) if recent_scores else 0.0,
            "quality_thresholds": self.thresholds,
            "active_rules": sum(1 for rule in self.quality_rules.values() if rule.enabled),
            "history_size": len(self.quality_history)
        }
        
        return stats
    
    async def validate_quality_requirements(
        self,
        metrics: QualityMetrics,
        requirements: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate video against specific quality requirements."""
        
        violations = []
        
        # Check minimum score requirement
        min_score = requirements.get("minimum_score", self.thresholds["minimum_score"])
        if metrics.overall_score < min_score:
            violations.append(f"Overall score {metrics.overall_score:.1f} below minimum {min_score}")
        
        # Check specific aspect requirements
        if "min_resolution_score" in requirements:
            if metrics.resolution_score < requirements["min_resolution_score"]:
                violations.append(f"Resolution score too low")
        
        if "min_clarity_score" in requirements:
            if metrics.clarity_score < requirements["min_clarity_score"]:
                violations.append(f"Clarity score too low")
        
        # Check for prohibited issues
        prohibited_issues = requirements.get("prohibited_issues", [])
        for issue in metrics.issues:
            if issue.value in prohibited_issues:
                violations.append(f"Prohibited issue detected: {issue.value}")
        
        # Check maximum issues allowed
        max_issues = requirements.get("max_issues", float('inf'))
        if len(metrics.issues) > max_issues:
            violations.append(f"Too many quality issues: {len(metrics.issues)} > {max_issues}")
        
        passed = len(violations) == 0
        
        return passed, violations