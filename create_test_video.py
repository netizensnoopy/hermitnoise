#!/usr/bin/env python3
"""
Generate a simple test video with moving shapes for testing the XOR effect.
"""

import cv2
import numpy as np

def create_test_video(output_path: str = "test_input.mp4", duration: float = 5.0, fps: int = 30):
    """Create a test video with bouncing shapes."""
    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Ball properties
    ball_x, ball_y = width // 2, height // 2
    ball_vx, ball_vy = 8, 6
    ball_radius = 40
    
    # Rectangle properties
    rect_x, rect_y = 100, 100
    rect_vx, rect_vy = -5, 4
    rect_w, rect_h = 80, 60
    
    total_frames = int(duration * fps)
    
    for frame_idx in range(total_frames):
        # Create white background
        frame = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        # Update ball position
        ball_x += ball_vx
        ball_y += ball_vy
        
        # Bounce ball off walls
        if ball_x - ball_radius <= 0 or ball_x + ball_radius >= width:
            ball_vx = -ball_vx
        if ball_y - ball_radius <= 0 or ball_y + ball_radius >= height:
            ball_vy = -ball_vy
        
        # Update rectangle position
        rect_x += rect_vx
        rect_y += rect_vy
        
        # Bounce rectangle off walls
        if rect_x <= 0 or rect_x + rect_w >= width:
            rect_vx = -rect_vx
        if rect_y <= 0 or rect_y + rect_h >= height:
            rect_vy = -rect_vy
        
        # Draw filled circle (ball)
        cv2.circle(frame, (int(ball_x), int(ball_y)), ball_radius, (0, 0, 200), -1)
        cv2.circle(frame, (int(ball_x), int(ball_y)), ball_radius, (0, 0, 0), 2)
        
        # Draw filled rectangle
        cv2.rectangle(frame, (int(rect_x), int(rect_y)), 
                     (int(rect_x + rect_w), int(rect_y + rect_h)), (0, 150, 0), -1)
        cv2.rectangle(frame, (int(rect_x), int(rect_y)), 
                     (int(rect_x + rect_w), int(rect_y + rect_h)), (0, 0, 0), 2)
        
        # Add some text that moves
        text_x = int(200 + 100 * np.sin(frame_idx * 0.1))
        text_y = int(400 + 30 * np.cos(frame_idx * 0.15))
        cv2.putText(frame, "XOR VISION", (text_x, text_y), 
                   cv2.FONT_HERSHEY_DUPLEX, 1.5, (100, 0, 100), 2)
        
        out.write(frame)
    
    out.release()
    print(f"Created test video: {output_path} ({total_frames} frames, {duration}s)")


if __name__ == "__main__":
    create_test_video()
