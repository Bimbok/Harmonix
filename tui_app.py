import locale
import os

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header,
    Footer,
    Input,
    DataTable,
    Static,
    Button,
    ProgressBar,
    Markdown,
    Label,
)
from textual.reactive import reactive

# from textual.worker import Worker
from textual import events

from player_engine import MusicEngine

os.environ["LC_NUMERIC"] = "C"
locale.setlocale(locale.LC_NUMERIC, "C")


class StatusBar(Static):
    """Custom status bar widget."""

    status_text = reactive("🎵 Ready to play")

    def render(self):
        return self.status_text


class NowPlayingCard(Static):
    """Card showing currently playing song info."""

    song_title = reactive("No song playing")
    song_artist = reactive("")
    song_album = reactive("")

    def compose(self) -> ComposeResult:
        yield Label(self.song_title, id="np_title")
        yield Label(self.song_artist, id="np_artist")
        yield Label(self.song_album, id="np_album")

    def watch_song_title(self, new_val):
        try:
            self.query_one("#np_title", Label).update(new_val)
        except Exception:
            pass

    def watch_song_artist(self, new_val):
        try:
            self.query_one("#np_artist", Label).update(new_val)
        except Exception:
            pass

    def watch_song_album(self, new_val):
        try:
            self.query_one("#np_album", Label).update(new_val)
        except Exception:
            pass


class MusicPlayerApp(App):
    """Modern TUI Music Player with YouTube Music integration."""

    CSS_PATH = "styles.tcss"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+a", "add_to_queue", "Add to Queue"),
        ("space", "toggle_pause", "Play/Pause"),
        ("n", "next_song", "Next"),
        ("p", "prev_song", "Prev"),
        ("s", "toggle_shuffle", "Shuffle"),
        ("r", "cycle_repeat", "Repeat"),
        ("c", "clear_queue", "Clear Queue"),
        ("d", "remove_selected", "Remove"),
        ("left", "seek_backward", "Seek -10s"),
        ("right", "seek_forward", "Seek +10s"),
        ("up", "volume_up", "Vol +"),
        ("down", "volume_down", "Vol -"),
        ("/", "focus_search", "Search"),
        ("?", "show_help", "Help"),
    ]

    # Reactive state
    current_title = reactive("🎵 Ready to play")
    play_button_label = reactive("▶ Play")

    def __init__(self):
        super().__init__()
        self.engine = MusicEngine()
        self._last_search_results = {}
        self._search_history = []

    def compose(self) -> ComposeResult:
        """Create the app layout."""
        yield Header(show_clock=True)

        # Main container with left and right panes
        with Container(id="main_container"):
            # LEFT PANE: Search & Queue
            with Vertical(id="left_pane"):
                yield Label("🔍 Search Music", classes="pane_title")
                with Horizontal(id="search_container"):
                    yield Input(
                        placeholder="Search songs, artists, albums...", id="search_box"
                    )
                    yield Button("🔍", id="btn_search", variant="primary")

                yield Label("Search Results", classes="section_title")
                yield DataTable(id="results_table", zebra_stripes=True)

                yield Label("📋 Queue", classes="section_title")
                with Horizontal(id="queue_controls"):
                    yield Button("Clear", id="btn_clear_queue", variant="error")
                    yield Button("Remove", id="btn_remove_selected", variant="warning")
                yield DataTable(id="queue_table", zebra_stripes=True)

            # RIGHT PANE: Now Playing & Lyrics
            with Vertical(id="right_pane"):
                yield Label("🎵 Now Playing", classes="pane_title")
                yield NowPlayingCard(id="now_playing_card")

                yield Label("📝 Lyrics", classes="section_title")
                with ScrollableContainer(id="lyrics_container"):
                    yield Markdown("*Lyrics will appear here...*", id="lyrics_view")

        # PLAYBACK CONTROLS
        with Container(id="controls_container"):
            # Status and time
            with Horizontal(id="status_row"):
                yield StatusBar(id="status_bar")
                yield Label("00:00 / 00:00", id="time_label")

            # Progress bar
            yield ProgressBar(total=100, show_eta=False, id="progress_bar")

            # Playback buttons
            with Horizontal(id="playback_buttons"):
                yield Button("⏮ Prev", id="btn_prev", variant="primary")
                yield Button("▶ Play", id="btn_play", variant="success")
                yield Button("⏭ Next", id="btn_next", variant="primary")
                yield Button("⏸ Pause", id="btn_pause")
                yield Button("⏹ Stop", id="btn_stop", variant="error")

            # Mode and volume controls
            with Horizontal(id="mode_controls"):
                yield Button("🔀 Shuffle: Off", id="btn_shuffle")
                yield Button("🔁 Repeat: Off", id="btn_repeat")
                yield Button("⏪ -10s", id="btn_seek_back")
                yield Button("⏩ +10s", id="btn_seek_forward")
                yield Label("🔊 Vol: 100%", id="vol_label")
                yield Button("−", id="btn_vol_down", classes="vol_btn")
                yield Button("+", id="btn_vol_up", classes="vol_btn")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the app when mounted."""
        # Setup Search Results Table
        results_table = self.query_one("#results_table", DataTable)
        results_table.add_columns("Title", "Artist", "Album", "Duration")
        results_table.cursor_type = "row"
        results_table.focus()

        # Setup Queue Table
        queue_table = self.query_one("#queue_table", DataTable)
        queue_table.add_columns("#", "Title", "Artist", "Duration")
        queue_table.cursor_type = "row"

        # Start periodic updates
        self.set_interval(0.5, self.update_playback_status)

        # Set initial status
        self.update_status("Ready to play music!")

    # ==================== EVENT HANDLERS ====================

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle search input submission."""
        if event.input.id == "search_box":
            await self.perform_search(event.value)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle all button clicks."""
        btn_id = event.button.id

        # Search
        if btn_id == "btn_search":
            search_box = self.query_one("#search_box", Input)
            await self.perform_search(search_box.value)

        # Playback controls
        elif btn_id == "btn_play":
            self.action_toggle_pause()
        elif btn_id == "btn_pause":
            self.action_toggle_pause()
        elif btn_id == "btn_next":
            self.action_next_song()
        elif btn_id == "btn_prev":
            self.action_prev_song()
        elif btn_id == "btn_stop":
            self.engine.stop()
            self.update_status("⏹ Stopped")

        # Modes
        elif btn_id == "btn_shuffle":
            self.action_toggle_shuffle()
        elif btn_id == "btn_repeat":
            self.action_cycle_repeat()

        # Seeking
        elif btn_id == "btn_seek_back":
            self.action_seek_backward()
        elif btn_id == "btn_seek_forward":
            self.action_seek_forward()

        # Volume
        elif btn_id == "btn_vol_up":
            self.action_volume_up()
        elif btn_id == "btn_vol_down":
            self.action_volume_down()

        # Queue management
        elif btn_id == "btn_clear_queue":
            self.action_clear_queue()
        elif btn_id == "btn_remove_selected":
            self.action_remove_selected()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in tables."""
        table = event.control
        row_key = event.row_key.value

        if table.id == "results_table":
            # Play from search results
            if row_key in self._last_search_results:
                song = self._last_search_results[row_key]
                self.engine.queue = [song]
                self.engine.current_index = 0
                self.engine.play_video(song["id"])
                self.refresh_queue_table()
                self.update_now_playing(song)
                self.update_status(f"▶ Playing: {song['title']}")

        elif table.id == "queue_table":
            # Jump to song in queue
            try:
                idx = int(row_key)
                self.engine.play_index(idx)
                if 0 <= idx < len(self.engine.queue):
                    self.update_now_playing(self.engine.queue[idx])
                    self.update_status("▶ Playing from queue")
            except (ValueError, IndexError):
                pass

    # ==================== SEARCH ====================

    async def perform_search(self, query: str):
        """Execute search."""
        if not query.strip():
            return

        self.update_status(f"🔍 Searching for '{query}'...")
        self._search_history.append(query)

        # Run search in worker to avoid blocking
        self.run_worker(self._search_worker(query), exclusive=False)

    async def _search_worker(self, query: str):
        """Worker function for searching."""
        results = self.engine.search(query, limit=30)

        # Update results table
        table = self.query_one("#results_table", DataTable)
        table.clear()

        self._last_search_results = {}
        seen_ids = set()

        for song in results:
            song_id = song["id"]
            if song_id in seen_ids:
                continue

            seen_ids.add(song_id)
            self._last_search_results[song_id] = song
            table.add_row(
                song["title"],
                song["artist"],
                song["album"],
                song["duration"],
                key=song_id,
            )

        self.update_status(f"✓ Found {len(seen_ids)} results for '{query}'")

    # ==================== QUEUE MANAGEMENT ====================

    def refresh_queue_table(self):
        """Update the queue display."""
        table = self.query_one("#queue_table", DataTable)
        table.clear()

        for idx, song in enumerate(self.engine.queue):
            # Highlight current song
            prefix = "▶" if idx == self.engine.current_index else " "
            table.add_row(
                f"{prefix}{idx + 1}",
                song["title"],
                song["artist"],
                song["duration"],
                key=str(idx),
            )

    # ==================== NOW PLAYING ====================

    def update_now_playing(self, song: dict):
        """Update now playing display."""
        card = self.query_one("#now_playing_card", NowPlayingCard)
        card.song_title = f"🎵 {song['title']}"
        card.song_artist = f"👤 {song['artist']}"
        card.song_album = f"💿 {song['album']}"

        self.query_one(Header).sub_title = f"♪ {song['title']} - {song['artist']}"

        # Fetch lyrics
        self.query_one("#lyrics_view", Markdown).update("*Loading lyrics...*")
        self.run_worker(self._fetch_lyrics_worker(song["id"]), exclusive=False)

    async def _fetch_lyrics_worker(self, video_id: str):
        """Worker for fetching lyrics."""
        lyrics = self.engine.get_lyrics(video_id)
        self.query_one("#lyrics_view", Markdown).update(lyrics)

    # ==================== PLAYBACK STATUS ====================

    def update_playback_status(self):
        """Periodic update of playback info."""
        pos = self.engine.position
        dur = self.engine.duration

        # Update time label
        time_label = self.query_one("#time_label", Label)
        time_label.update(f"{self.format_time(pos)} / {self.format_time(dur)}")

        # Update progress bar
        bar = self.query_one("#progress_bar", ProgressBar)
        if dur > 0:
            bar.update(total=dur, progress=pos)

        # Update play button state
        if self.engine.is_playing:
            self.play_button_label = "⏸ Pause"
        else:
            self.play_button_label = "▶ Play"

        # Auto-advance when song ends
        if dur > 0 and (dur - pos) < 0.5 and not self.engine.is_paused:
            if self.engine.queue and self.engine.current_index >= 0:
                self.action_next_song()

    def update_status(self, message: str):
        """Update status bar message."""
        status_bar = self.query_one("#status_bar", StatusBar)
        status_bar.status_text = message

    @staticmethod
    def format_time(seconds: float) -> str:
        """Format seconds as MM:SS."""
        minutes, secs = divmod(int(seconds), 60)
        return f"{minutes:02d}:{secs:02d}"

    # ==================== ACTIONS ====================

    def action_toggle_pause(self):
        """Toggle play/pause."""
        self.engine.toggle_pause()
        if self.engine.is_paused:
            self.update_status("⏸ Paused")
        else:
            self.update_status("▶ Playing")

    def action_next_song(self):
        """Play next song."""
        self.engine.play_next()
        if 0 <= self.engine.current_index < len(self.engine.queue):
            song = self.engine.queue[self.engine.current_index]
            self.update_now_playing(song)
            self.refresh_queue_table()
            self.update_status(f"▶ Next: {song['title']}")

    def action_prev_song(self):
        """Play previous song."""
        self.engine.play_prev()
        if 0 <= self.engine.current_index < len(self.engine.queue):
            song = self.engine.queue[self.engine.current_index]
            self.update_now_playing(song)
            self.refresh_queue_table()
            self.update_status(f"▶ Previous: {song['title']}")

    def action_toggle_shuffle(self):
        """Toggle shuffle mode."""
        self.engine.toggle_shuffle()
        btn = self.query_one("#btn_shuffle", Button)
        btn.label = f"🔀 Shuffle: {'On' if self.engine.shuffle_mode else 'Off'}"
        self.update_status(f"🔀 Shuffle: {'On' if self.engine.shuffle_mode else 'Off'}")

    def action_cycle_repeat(self):
        """Cycle repeat mode."""
        mode = self.engine.cycle_repeat()
        icons = {"off": "🔁", "all": "🔂", "one": "🔂"}
        btn = self.query_one("#btn_repeat", Button)
        btn.label = f"{icons[mode]} Repeat: {mode.capitalize()}"
        self.update_status(f"🔁 Repeat: {mode.capitalize()}")

    def action_add_to_queue(self):
        """Add selected search result to queue."""
        table = self.query_one("#results_table", DataTable)
        if table.has_focus and table.cursor_coordinate:
            try:
                row_key = table.coordinate_to_cell_key(
                    table.cursor_coordinate
                ).row_key.value
                if row_key in self._last_search_results:
                    song = self._last_search_results[row_key]
                    self.engine.add_to_queue(song)
                    self.refresh_queue_table()
                    self.update_status(f"✓ Added to queue: {song['title']}")
            except:
                pass

    def action_clear_queue(self):
        """Clear the entire queue."""
        self.engine.clear_queue()
        self.refresh_queue_table()
        self.update_status("🗑 Queue cleared")

    def action_remove_selected(self):
        """Remove selected song from queue."""
        table = self.query_one("#queue_table", DataTable)
        if table.has_focus and table.cursor_coordinate:
            try:
                row_key = table.coordinate_to_cell_key(
                    table.cursor_coordinate
                ).row_key.value
                idx = int(row_key)
                removed = self.engine.remove_from_queue(idx)
                if removed:
                    self.refresh_queue_table()
                    self.update_status(f"🗑 Removed: {removed['title']}")
            except:
                pass

    def action_seek_forward(self):
        """Seek forward 10 seconds."""
        self.engine.seek(10, relative=True)
        self.update_status("⏩ Seek +10s")

    def action_seek_backward(self):
        """Seek backward 10 seconds."""
        self.engine.seek(-10, relative=True)
        self.update_status("⏪ Seek -10s")

    def action_volume_up(self):
        """Increase volume."""
        new_vol = min(100, self.engine.volume + 10)
        self.engine.set_volume(new_vol)
        self.query_one("#vol_label", Label).update(f"🔊 Vol: {new_vol}%")
        self.update_status(f"🔊 Volume: {new_vol}%")

    def action_volume_down(self):
        """Decrease volume."""
        new_vol = max(0, self.engine.volume - 10)
        self.engine.set_volume(new_vol)
        icon = "🔇" if new_vol == 0 else "🔉" if new_vol < 50 else "🔊"
        self.query_one("#vol_label", Label).update(f"{icon} Vol: {new_vol}%")
        self.update_status(f"🔊 Volume: {new_vol}%")

    def action_focus_search(self):
        """Focus the search box."""
        self.query_one("#search_box", Input).focus()

    def action_show_help(self):
        """Show help message."""
        help_text = """
**Keyboard Shortcuts:**
• Space: Play/Pause
• N: Next song
• P: Previous song
• S: Toggle shuffle
• R: Cycle repeat mode
• C: Clear queue
• D: Remove selected
• ←/→: Seek ±10s
• ↑/↓: Volume ±10%
• /: Focus search
• Ctrl+A: Add to queue
• Q: Quit
"""
        self.query_one("#lyrics_view", Markdown).update(help_text)
        self.update_status("❓ Showing help")


if __name__ == "__main__":
    app = MusicPlayerApp()
    app.run()
