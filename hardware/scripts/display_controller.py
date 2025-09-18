#!/usr/bin/env python3
"""
Video Display Controller for Raspberry Pi
T052: Controls video playback on HDMI display
Phase 1 - Manual video management system
"""

import os
import sys
import time
import json
import logging
import subprocess
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
VIDEO_DIR = "/home/aipainting/videos"  # Default video directory
LOG_FILE = "/var/log/display_controller.log"
CHECK_INTERVAL = 2  # Seconds between API checks

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DisplayController")


class VideoPlayer:
    """Manages video playback using OMXPlayer or VLC"""
    
    def __init__(self, player_type: str = "omxplayer"):
        self.player_type = player_type
        self.current_process: Optional[subprocess.Popen] = None
        self.current_video_id: Optional[str] = None
        self.is_playing: bool = False
        self.is_paused: bool = False
        
    def play(self, video_path: str, video_id: str, loop: bool = False) -> bool:
        """Start playing a video"""
        try:
            # Stop any current playback
            self.stop()
            
            # Check if video file exists
            if not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                return False
            
            # Build command based on player type
            if self.player_type == "omxplayer":
                cmd = ["omxplayer", "-b", "--no-osd"]
                if loop:
                    cmd.append("--loop")
                cmd.append(video_path)
            elif self.player_type == "vlc":
                cmd = ["cvlc", "--fullscreen", "--no-video-title-show"]
                if loop:
                    cmd.append("--loop")
                cmd.append(video_path)
            else:
                logger.error(f"Unknown player type: {self.player_type}")
                return False
            
            # Start the player process
            logger.info(f"Starting playback: {video_path}")
            self.current_process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            self.current_video_id = video_id
            self.is_playing = True
            self.is_paused = False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start playback: {e}")
            return False
    
    def pause(self) -> bool:
        """Pause current playback"""
        if self.current_process and self.is_playing and not self.is_paused:
            try:
                if self.player_type == "omxplayer":
                    # Send 'p' key to pause/unpause omxplayer
                    self.current_process.stdin.write(b'p')
                    self.current_process.stdin.flush()
                elif self.player_type == "vlc":
                    # Send space key to pause/unpause VLC
                    self.current_process.stdin.write(b' ')
                    self.current_process.stdin.flush()
                
                self.is_paused = True
                logger.info("Playback paused")
                return True
            except Exception as e:
                logger.error(f"Failed to pause: {e}")
        return False
    
    def resume(self) -> bool:
        """Resume paused playback"""
        if self.current_process and self.is_playing and self.is_paused:
            try:
                if self.player_type == "omxplayer":
                    # Send 'p' key to pause/unpause omxplayer
                    self.current_process.stdin.write(b'p')
                    self.current_process.stdin.flush()
                elif self.player_type == "vlc":
                    # Send space key to pause/unpause VLC
                    self.current_process.stdin.write(b' ')
                    self.current_process.stdin.flush()
                
                self.is_paused = False
                logger.info("Playback resumed")
                return True
            except Exception as e:
                logger.error(f"Failed to resume: {e}")
        return False
    
    def stop(self) -> bool:
        """Stop current playback"""
        if self.current_process:
            try:
                # Send quit command
                if self.player_type == "omxplayer":
                    self.current_process.stdin.write(b'q')
                    self.current_process.stdin.flush()
                elif self.player_type == "vlc":
                    self.current_process.terminate()
                
                # Wait for process to end
                self.current_process.wait(timeout=5)
                
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't stop gracefully
                self.current_process.kill()
            except Exception as e:
                logger.error(f"Error stopping playback: {e}")
            
            finally:
                self.current_process = None
                self.current_video_id = None
                self.is_playing = False
                self.is_paused = False
                logger.info("Playback stopped")
                
        return True
    
    def is_running(self) -> bool:
        """Check if player process is still running"""
        if self.current_process:
            return self.current_process.poll() is None
        return False


class DisplayController:
    """Main controller that syncs with API and manages display"""
    
    def __init__(self):
        self.api_url = API_BASE_URL
        self.video_player = VideoPlayer()
        self.last_status: Optional[Dict[str, Any]] = None
        self.running = True
        
    def get_api_status(self) -> Optional[Dict[str, Any]]:
        """Fetch current status from API"""
        try:
            response = requests.get(f"{self.api_url}/api/display/status", timeout=5)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
        return None
    
    def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get video information from API"""
        try:
            response = requests.get(f"{self.api_url}/api/videos", timeout=5)
            if response.status_code == 200:
                data = response.json()
                for video in data.get("videos", []):
                    if video["id"] == video_id:
                        return video
        except requests.RequestException as e:
            logger.error(f"Failed to get video info: {e}")
        return None
    
    def sync_with_api(self):
        """Synchronize display state with API"""
        status = self.get_api_status()
        
        if not status:
            return
        
        # Check if status changed
        if self.last_status == status:
            return
        
        session = status.get("session")
        
        if not session:
            # No active session, stop playback
            if self.video_player.is_playing:
                logger.info("No active session, stopping playback")
                self.video_player.stop()
        else:
            # Active session exists
            video_id = session.get("video_id")
            playback_status = session.get("playback_status")
            loop_enabled = session.get("loop_enabled", False)
            
            # Handle different playback states
            if playback_status == "playing":
                if self.video_player.current_video_id != video_id:
                    # New video, start playback
                    video_info = self.get_video_info(video_id)
                    if video_info:
                        video_path = video_info.get("file_path")
                        if video_path:
                            # Convert relative path to absolute if needed
                            if not os.path.isabs(video_path):
                                video_path = os.path.join(VIDEO_DIR, video_path)
                            
                            logger.info(f"Starting new video: {video_id}")
                            self.video_player.play(video_path, video_id, loop_enabled)
                elif self.video_player.is_paused:
                    # Resume if paused
                    logger.info("Resuming playback")
                    self.video_player.resume()
                    
            elif playback_status == "paused":
                if self.video_player.is_playing and not self.video_player.is_paused:
                    logger.info("Pausing playback")
                    self.video_player.pause()
                    
            elif playback_status == "stopped":
                if self.video_player.is_playing:
                    logger.info("Stopping playback")
                    self.video_player.stop()
        
        self.last_status = status
    
    def run(self):
        """Main control loop"""
        logger.info("Display Controller started")
        
        try:
            while self.running:
                # Sync with API
                self.sync_with_api()
                
                # Check if player crashed
                if self.video_player.is_playing and not self.video_player.is_running():
                    logger.warning("Player process died unexpectedly")
                    self.video_player.is_playing = False
                    self.video_player.current_video_id = None
                
                # Wait before next check
                time.sleep(CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up...")
        self.video_player.stop()
        logger.info("Display Controller stopped")


def check_dependencies():
    """Check if required video players are installed"""
    players = ["omxplayer", "vlc"]
    available = []
    
    for player in players:
        try:
            subprocess.run(["which", player], check=True, capture_output=True)
            available.append(player)
        except subprocess.CalledProcessError:
            pass
    
    if not available:
        logger.error("No video player found. Please install omxplayer or vlc")
        sys.exit(1)
    
    logger.info(f"Available players: {', '.join(available)}")
    return available[0]  # Return first available player


def main():
    """Main entry point"""
    # Check dependencies
    player_type = check_dependencies()
    
    # Create video directory if it doesn't exist
    Path(VIDEO_DIR).mkdir(parents=True, exist_ok=True)
    
    # Start controller
    controller = DisplayController()
    controller.video_player.player_type = player_type
    
    logger.info(f"Using {player_type} for video playback")
    logger.info(f"Video directory: {VIDEO_DIR}")
    logger.info(f"API endpoint: {API_BASE_URL}")
    
    # Run the controller
    controller.run()


if __name__ == "__main__":
    main()