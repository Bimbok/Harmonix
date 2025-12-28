#!/bin/bash

# Modern TUI Music Player - Setup Script
# This script helps you set up all dependencies

echo "🎵 Modern TUI Music Player - Setup Script - By Bimbok"
echo "====================================================="
echo ""

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
  OS="macos"
else
  OS="unknown"
fi

echo "Detected OS: $OS"
echo ""

# Install system dependencies
echo "📦 Installing system dependencies..."
if [ "$OS" == "linux" ]; then
  if command -v apt &>/dev/null; then
    echo "Using apt package manager..."
    sudo apt update
    sudo apt install -y mpv python3 python3-pip python3-venv
  elif command -v pacman &>/dev/null; then
    echo "Using pacman package manager..."
    sudo pacman -S --noconfirm mpv python python-pip
  elif command -v dnf &>/dev/null; then
    echo "Using dnf package manager..."
    sudo dnf install -y mpv python3 python3-pip
  else
    echo "❌ Unknown package manager. Please install mpv and python3 manually."
    exit 1
  fi
elif [ "$OS" == "macos" ]; then
  if command -v brew &>/dev/null; then
    echo "Using Homebrew..."
    brew install mpv python3
  else
    echo "❌ Homebrew not found. Please install from https://brew.sh"
    exit 1
  fi
else
  echo "❌ Unsupported OS. Please install dependencies manually."
  exit 1
fi

echo "✅ System dependencies installed"
echo ""

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
  python3 -m venv venv
  echo "✅ Virtual environment created"
else
  echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo ""
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install textual python-mpv ytmusicapi

echo "✅ Python packages installed"
echo ""

# Check if files exist
echo "📂 Checking for required files..."
required_files=("tui_app.py" "player_engine.py" "styles.tcss")
missing_files=()

for file in "${required_files[@]}"; do
  if [ ! -f "$file" ]; then
    missing_files+=("$file")
  fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
  echo "❌ Missing required files:"
  for file in "${missing_files[@]}"; do
    echo "   - $file"
  done
  echo ""
  echo "Please ensure all required files are in the current directory:"
  echo "   - tui_app.py"
  echo "   - player_engine.py"
  echo "   - styles.tcss"
  exit 1
fi

echo "✅ All required files found"
echo ""

# Create launcher script
echo "📝 Creating launcher script..."
cat >run_music_player.sh <<'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python tui_app.py
EOF

chmod +x run_music_player.sh
echo "✅ Launcher script created: run_music_player.sh"
echo ""

# Test MPV installation
echo "🧪 Testing MPV installation..."
if command -v mpv &>/dev/null; then
  echo "✅ MPV is installed and accessible"
else
  echo "⚠️  Warning: MPV command not found in PATH"
fi

echo ""
echo "================================================"
echo "✨ Setup complete! You're ready to play music!"
echo "================================================"
echo ""
echo "To start the music player:"
echo "   ./run_music_player.sh"
echo ""
echo "Or manually:"
echo "   source venv/bin/activate"
echo "   python tui_app.py"
echo ""
echo "📖 Quick Start:"
echo "   1. Type a song name in the search box"
echo "   2. Press Enter to search"
echo "   3. Click a result to play"
echo "   4. Use Space to pause/play"
echo "   5. Press ? for help"
echo ""
echo "⌨️  Key Shortcuts:"
echo "   Space  - Play/Pause"
echo "   N      - Next song"
echo "   P      - Previous song"
echo "   S      - Shuffle"
echo "   R      - Repeat"
echo "   Q      - Quit"
echo ""
echo "Enjoy your music! 🎵"
