# 🎵 Modern TUI Music Player - Harmonix

A beautiful, feature-rich terminal music player with YouTube Music integration built with Python, Textual, and MPV.

## ✨ New Features & Improvements

### Demo
<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/b743e371-708b-4eff-a740-ef3107612867" />

<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/78fc88c8-8643-4ca5-9064-a95a0859be7b" />

### 🎨 UI/UX Enhancements
- **Modern Design**: Complete UI redesign with color-coded sections
- **Now Playing Card**: Dedicated card showing current song info (title, artist, album)
- **Status Bar**: Real-time status updates for all actions
- **Better Layout**: Optimized split-pane layout with search, queue, and lyrics
- **Zebra Striping**: Alternating row colors for better readability
- **Visual Feedback**: Highlights for current playing song in queue
- **Responsive Design**: Adapts to different terminal sizes

### 🎛️ Playback Features
- **Smart Shuffle**: Plays all songs before repeating (no immediate repeats)
- **Three Repeat Modes**: Off → All → One
- **Seek Controls**: Jump forward/backward 10 seconds
- **Pause/Resume**: Full playback control
- **Stop Function**: Complete stop with reset
- **Auto-advance**: Automatically plays next song when current ends

### 📋 Queue Management
- **Add to Queue**: Add songs without interrupting playback (Ctrl+A)
- **Remove from Queue**: Delete individual songs (D key)
- **Clear Queue**: Remove all songs at once (C key)
- **Queue Navigation**: Click any song to jump to it
- **Visual Indicator**: See which song is currently playing

### 🔍 Search Improvements
- **Better Results**: Shows album info in search results
- **More Results**: Fetches up to 30 songs per search
- **Search History**: Keeps track of your searches
- **Click to Play**: Instant playback from search results
- **Error Handling**: Graceful handling of failed searches

### ⌨️ Keyboard Shortcuts

#### Playback
- `Space` - Play/Pause toggle
- `N` - Next song
- `P` - Previous song
- `S` - Toggle shuffle mode
- `R` - Cycle repeat mode (Off → All → One)

#### Navigation
- `←` - Seek backward 10 seconds
- `→` - Seek forward 10 seconds
- `↑` - Volume up (+10%)
- `↓` - Volume down (-10%)

#### Queue Management
- `Ctrl+A` - Add selected song to queue
- `C` - Clear entire queue
- `D` - Remove selected song from queue

#### General
- `/` - Focus search box
- `?` - Show help in lyrics panel
- `Q` - Quit application

### 🎵 Enhanced Features
- **Lyrics Caching**: Faster lyrics loading for previously played songs
- **Better Error Messages**: User-friendly error handling
- **Volume Control**: Precise volume adjustment with visual feedback
- **Time Display**: Shows current position and total duration
- **Progress Bar**: Visual representation of playback progress
- **Clock**: Header shows current time

## 📦 Installation

### Prerequisites
```bash
# Install system dependencies
# Ubuntu/Debian
sudo apt install mpv python3-pip

# macOS
brew install mpv python3

# Arch Linux
sudo pacman -S mpv python
```

### Python Dependencies
```bash
pip install textual mpv ytmusicapi python-mpv
```

### Setup
```bash
# Clone or download the files
# Ensure all three files are in the same directory:
# - tui_app.py
# - player_engine.py
# - styles.tcss

# Run the app
python tui_app.py
```

## 🚀 Usage Guide

### Basic Workflow
1. **Search**: Type in the search box and press Enter
2. **Play**: Click on a search result to play immediately
3. **Add to Queue**: Press `Ctrl+A` to add selected song to queue
4. **Control Playback**: Use space bar, N/P keys, or buttons
5. **View Lyrics**: Lyrics load automatically in the right pane

### Tips
- Use Tab to navigate between panels
- Arrow keys work in tables for selection
- Mouse clicks work on all buttons and table rows
- Status bar shows feedback for all actions

## 🏗️ Architecture

### Files Structure
```
├── tui_app.py          # Main TUI application
├── player_engine.py    # Music playback engine
└── styles.tcss         # Textual CSS styles
```

### Key Components

#### MusicEngine (`player_engine.py`)
- MPV integration for audio playback
- YouTube Music API for search and lyrics
- Queue management with shuffle/repeat
- Smart caching for better performance

#### MusicPlayerApp (`tui_app.py`)
- Textual-based TUI interface
- Event handling and user interactions
- Reactive updates for real-time feedback
- Worker threads for async operations

#### Styles (`styles.tcss`)
- Modern color scheme
- Responsive layout
- Button states and hover effects
- Custom component styling

## 🐛 Bug Fixes

### Fixed Issues
1. ✅ Locale crash on non-US systems (LC_NUMERIC set to C)
2. ✅ Better MPV initialization order
3. ✅ Proper error handling for failed API calls
4. ✅ Fixed auto-advance logic
5. ✅ Improved queue index tracking
6. ✅ Better volume control boundaries
7. ✅ Fixed seek functionality
8. ✅ Proper pause state management

### Known Limitations
- Requires active internet connection
- Depends on YouTube Music availability
- Some songs may not have lyrics available
- Search results limited to YouTube Music catalog

## 🎯 Future Enhancements

Potential features for future versions:
- [ ] Playlist save/load functionality
- [ ] Search filters (by artist, album, year)
- [ ] Equalizer controls
- [ ] Crossfade between songs
- [ ] Download songs for offline play
- [ ] Song recommendations based on listening history
- [ ] Multiple queue support
- [ ] Import playlists from YouTube Music
- [ ] Export/Import settings
- [ ] Themes/color schemes

## 🤝 Contributing

Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📄 License

This is a personal project for educational purposes.

## 🙏 Credits

Built with:
- [Textual](https://textual.textualize.io/) - TUI framework
- [python-mpv](https://github.com/jaseg/python-mpv) - MPV Python bindings
- [ytmusicapi](https://github.com/sigma67/ytmusicapi) - YouTube Music API
- [MPV](https://mpv.io/) - Media player

---

**Enjoy your music! 🎵**

For help within the app, press `?` to see all keyboard shortcuts.
