#!/usr/bin/env python3
"""
XOR Persistence of Vision Video Effect Tool

Applies the XOR persistence of vision effect to input videos, creating
an output where shapes are only visible while they're moving.

The effect works by XOR-drawing edge-detected frames onto a persistent
canvas. When pixels toggle on/off repeatedly, static areas become noise
while moving edges remain perceptible due to persistence of vision.
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from moviepy import VideoFileClip, ImageSequenceClip


def parse_resolution(resolution_str: str) -> tuple[int, int]:
    """Parse resolution string like '160x120' into (width, height)."""
    try:
        parts = resolution_str.lower().split('x')
        if len(parts) != 2:
            raise ValueError()
        return int(parts[0]), int(parts[1])
    except (ValueError, IndexError):
        raise argparse.ArgumentTypeError(
            f"Invalid resolution format '{resolution_str}'. Use WIDTHxHEIGHT (e.g., 160x120)"
        )


def extract_edges(frame: np.ndarray, line_width: int = 1) -> np.ndarray:
    """
    Extract edges from a frame using Canny edge detection.
    
    Args:
        frame: BGR image frame
        line_width: Width of edge lines (applied via dilation)
    
    Returns:
        Binary edge image (0 or 255)
    """
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 1.4)
    
    # Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)
    
    # Dilate edges if line_width > 1
    if line_width > 1:
        kernel = np.ones((line_width, line_width), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
    
    return edges


def process_video(
    input_path: str,
    output_path: str,
    keep_audio: bool = True,
    resolution: tuple[int, int] = (160, 120),
    line_width: int = 1,
    max_duration: float = 30.0,
    fps: int = 30,
    invert_output: bool = False
) -> None:
    """
    Process a video with the XOR persistence of vision effect.
    
    Args:
        input_path: Path to input video file
        output_path: Path for output video file
        keep_audio: Whether to include original audio
        resolution: Target resolution for the pixel effect (width, height)
        line_width: Width of edge lines
        max_duration: Maximum video duration in seconds
        fps: Output frame rate
        invert_output: If True, show white edges on black; if False, black edges on white
    """
    print(f"Loading video: {input_path}")
    
    # Load video with moviepy for easy audio handling
    video = VideoFileClip(input_path)
    
    # Check duration
    if video.duration > max_duration:
        print(f"Warning: Video is {video.duration:.1f}s, truncating to {max_duration}s")
        video = video.subclip(0, max_duration)
    
    original_size = (int(video.w), int(video.h))
    target_w, target_h = resolution
    
    print(f"Original size: {original_size[0]}x{original_size[1]}")
    print(f"Processing at: {target_w}x{target_h}")
    print(f"Duration: {video.duration:.2f}s, FPS: {fps}")
    
    # Initialize canvas with random noise (the key to the effect!)
    # Random black (0) and white (255) pixels
    canvas = np.random.choice([0, 255], size=(target_h, target_w)).astype(np.uint8)
    
    # Process frames
    processed_frames = []
    frame_count = int(video.duration * fps)
    
    print(f"Processing {frame_count} frames...")
    
    for i, t in enumerate(np.linspace(0, video.duration, frame_count, endpoint=False)):
        # Get frame at time t
        frame = video.get_frame(t)
        
        # Convert RGB to BGR for OpenCV
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Downscale to target resolution (nearest neighbor for crisp pixels)
        small_frame = cv2.resize(frame_bgr, (target_w, target_h), interpolation=cv2.INTER_NEAREST)
        
        # Extract edges
        edges = extract_edges(small_frame, line_width)
        
        # XOR the edges onto the noisy canvas
        # Where edges exist (255), toggle the canvas pixel
        # This makes edges "invisible" when static but perceptible when moving
        canvas = cv2.bitwise_xor(canvas, edges)
        
        # Output is the noisy canvas directly
        # (invert_output swaps black/white ratio but effect is the same)
        if invert_output:
            output_small = 255 - canvas
        else:
            output_small = canvas.copy()
        
        # Upscale back to original size with nearest neighbor (crisp pixels)
        output_large = cv2.resize(output_small, original_size, interpolation=cv2.INTER_NEAREST)
        
        # Convert to RGB for moviepy
        output_rgb = cv2.cvtColor(
            cv2.cvtColor(output_large, cv2.COLOR_GRAY2BGR),
            cv2.COLOR_BGR2RGB
        )
        
        processed_frames.append(output_rgb)
        
        # Progress indicator
        if (i + 1) % 30 == 0 or i == frame_count - 1:
            print(f"  Processed {i + 1}/{frame_count} frames ({100*(i+1)/frame_count:.1f}%)")
    
    print("Compiling output video...")
    
    # Create video from frames
    output_clip = ImageSequenceClip(processed_frames, fps=fps)
    
    # Add audio if requested
    if keep_audio and video.audio is not None:
        print("Adding audio track...")
        output_clip = output_clip.set_audio(video.audio)
    elif keep_audio and video.audio is None:
        print("Note: Input video has no audio track")
    else:
        print("Audio removed as requested")
    
    # Write output
    print(f"Writing to: {output_path}")
    output_clip.write_videofile(
        output_path,
        fps=fps,
        codec='libx264',
        audio_codec='aac' if keep_audio and video.audio else None
    )
    
    # Cleanup
    video.close()
    output_clip.close()
    
    print("Done!")


def main():
    parser = argparse.ArgumentParser(
        description="Apply XOR persistence of vision effect to a video",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python xor_vision.py input.mp4 output.mp4
  python xor_vision.py input.mp4 output.mp4 --no-audio
  python xor_vision.py input.mp4 output.mp4 --resolution 80x60 --line-width 2
        """
    )
    
    parser.add_argument(
        "input",
        help="Input video file path"
    )
    
    parser.add_argument(
        "output",
        nargs="?",
        default="output_xor.mp4",
        help="Output video file path (default: output_xor.mp4)"
    )
    
    parser.add_argument(
        "--keep-audio",
        dest="keep_audio",
        action="store_true",
        default=True,
        help="Keep original audio (default)"
    )
    
    parser.add_argument(
        "--no-audio",
        dest="keep_audio",
        action="store_false",
        help="Remove audio from output"
    )
    
    parser.add_argument(
        "--resolution",
        type=parse_resolution,
        default=(160, 120),
        help="Processing resolution for pixel effect (default: 160x120)"
    )
    
    parser.add_argument(
        "--line-width",
        type=int,
        default=1,
        choices=range(1, 6),
        metavar="1-5",
        help="Width of edge lines (default: 1)"
    )
    
    parser.add_argument(
        "--max-duration",
        type=float,
        default=30.0,
        help="Maximum video duration in seconds (default: 30)"
    )
    
    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="Output frame rate (default: 30)"
    )
    
    parser.add_argument(
        "--invert",
        action="store_true",
        help="Invert output (white edges on black background)"
    )
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    # Process the video
    try:
        process_video(
            input_path=args.input,
            output_path=args.output,
            keep_audio=args.keep_audio,
            resolution=args.resolution,
            line_width=args.line_width,
            max_duration=args.max_duration,
            fps=args.fps,
            invert_output=args.invert
        )
    except Exception as e:
        print(f"Error processing video: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
