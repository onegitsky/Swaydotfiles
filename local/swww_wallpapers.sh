#!/bin/bash

# Directory containing your wallpapers (change this to your wallpaper folder)
WALLPAPER_DIR="$HOME/Pictures/Wallpapers/browser"

# Ensure the directory exists
if [ ! -d "$WALLPAPER_DIR" ]; then
    echo "Wallpaper directory not found: $WALLPAPER_DIR"
    exit 1
fi

# Get a random wallpaper from the directory
WALLPAPER=$(find "$WALLPAPER_DIR" -type f \( -iname "*.jpg" -o -iname "*.png" -o -iname "*.gif" \) | shuf -n 1)

# Check if a wallpaper was found
if [ -z "$WALLPAPER" ]; then
    echo "No wallpapers found in $WALLPAPER_DIR"
    exit 1
fi

# Check if daemon is running, if returns null then starts daemon
if ! pgrep -f "swww-daemon" > /dev/null; then
    swww-daemon --format xrgb &
    sleep 1
fi

# Apply the wallpaper with a smooth animation using swww
swww img "$WALLPAPER" --transition-type center --transition-step 90 --transition-fps 60 --transition-duration 1

# Optional: Output the current wallpaper (useful for Waybar feedback)
echo "Set wallpaper to: $WALLPAPER"
