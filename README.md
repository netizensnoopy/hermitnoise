# Hermitnoise

## A XOR Persistence of Vision Video Effect

A Python tool that applies the mesmerizing XOR persistence of vision effect to videos. Shapes are only visible while they're moving—pause the video and they disappear into noise!

## How It Works

This effect exploits how your brain perceives motion:

1. **Edge Detection**: Each frame is processed with Canny edge detection
2. **XOR Drawing**: Edges are XOR'd onto a persistent canvas
3. **Pixel Toggle**: When a pixel is drawn where one exists, it toggles off
4. **Noise Accumulation**: Static areas become random noise patterns
5. **Motion Visibility**: Moving edges remain visible due to persistence of vision

The result: you can clearly see shapes moving, but pause the video and there's no visible shape—just random dots!

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Basic usage:
```bash
python xor_vision.py input_video.mp4 output.mp4
```

Remove audio:
```bash
python xor_vision.py input_video.mp4 output.mp4 --no-audio
```

Customize the pixel effect:
```bash
python xor_vision.py input_video.mp4 output.mp4 --resolution 80x60 --line-width 2
```

White edges on black background:
```bash
python xor_vision.py input_video.mp4 output.mp4 --invert
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--keep-audio` | ✓ | Keep original audio track |
| `--no-audio` | | Remove audio from output |
| `--resolution WxH` | 160x120 | Processing resolution (lower = bigger pixels) |
| `--line-width 1-5` | 1 | Edge line thickness |
| `--max-duration N` | 30 | Max video length in seconds |
| `--fps N` | 30 | Output frame rate |
| `--invert` | | White edges on black background |

## Tips

- **Best results**: Videos with clear movement and distinct edges
- **Lower resolution**: Creates bigger, more retro pixels
- **Higher line-width**: Makes edges more visible but adds more noise
- **Invert mode**: More dramatic effect, closer to the original demo
