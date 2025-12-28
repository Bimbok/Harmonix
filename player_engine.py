import mpv
import random
from ytmusicapi import YTMusic
from typing import Optional, List, Dict


class MusicEngine:
    def __init__(self):
        # Initialize MPV with yt-dlp enabled
        self.player = mpv.MPV(ytdl=True, video=False)
        self.api = YTMusic()

        # State
        self.queue: List[Dict] = []
        self.current_index = -1
        self.shuffle_mode = False
        self.repeat_mode = "off"  # options: "off", "all", "one"
        self._original_queue = []  # Store original queue for unshuffle
        self._shuffle_history = []  # Track played songs in shuffle

        # Cache
        self._lyrics_cache = {}

    def search(self, query: str, limit: int = 20) -> List[Dict]:
        """Search for songs with error handling."""
        try:
            results = self.api.search(query, filter="songs", limit=limit)
            clean_results = []
            for item in results:
                clean_results.append(
                    {
                        "title": item.get("title", "Unknown"),
                        "artist": item["artists"][0]["name"]
                        if item.get("artists")
                        else "Unknown Artist",
                        "id": item.get("videoId", ""),
                        "duration": item.get("duration", "N/A"),
                        "album": item.get("album", {}).get("name", "Unknown Album")
                        if item.get("album")
                        else "Unknown Album",
                    }
                )
            return clean_results
        except Exception as e:
            return []

    def add_to_queue(self, song_dict: Dict):
        """Add a song to the queue."""
        self.queue.append(song_dict)

    def remove_from_queue(self, index: int):
        """Remove a song from the queue by index."""
        if 0 <= index < len(self.queue):
            removed = self.queue.pop(index)
            # Adjust current index if needed
            if index < self.current_index:
                self.current_index -= 1
            elif index == self.current_index:
                # If I removed the current song, stop playback
                self.stop()
                self.current_index = -1
            return removed
        return None

    def clear_queue(self):
        """Clear the entire queue."""
        self.queue.clear()
        self.current_index = -1
        self.stop()

    def move_in_queue(self, from_idx: int, to_idx: int):
        """Move a song in the queue."""
        if 0 <= from_idx < len(self.queue) and 0 <= to_idx < len(self.queue):
            song = self.queue.pop(from_idx)
            self.queue.insert(to_idx, song)

            # Adjust current_index
            if from_idx == self.current_index:
                self.current_index = to_idx
            elif from_idx < self.current_index <= to_idx:
                self.current_index -= 1
            elif to_idx <= self.current_index < from_idx:
                self.current_index += 1

    def play_index(self, index: int):
        """Play a specific index from the queue."""
        if 0 <= index < len(self.queue):
            self.current_index = index
            song = self.queue[index]
            self.play_video(song["id"])

    def play_video(self, video_id: str):
        """Directly play a video ID."""
        try:
            url = f"https://music.youtube.com/watch?v={video_id}"
            self.player.play(url)
            self.player.wait_for_property("duration", timeout=5)
        except Exception as e:
            pass  # Handle silently, UI will show error

    def toggle_pause(self):
        """Toggle play/pause."""
        try:
            self.player.pause = not self.player.pause
        except:
            pass

    def stop(self):
        """Stop playback."""
        try:
            self.player.stop()
        except:
            pass

    def seek(self, seconds: float, relative: bool = False):
        """Seek to a position (absolute) or by amount (relative)."""
        try:
            if relative:
                self.player.seek(seconds, "relative")
            else:
                self.player.seek(seconds, "absolute")
        except:
            pass

    def set_volume(self, level: int):
        """Set volume (0-100)."""
        self.player.volume = max(0, min(100, level))

    @property
    def volume(self) -> int:
        """Get current volume."""
        try:
            return int(self.player.volume)
        except (TypeError, ValueError):
            return 100

    @property
    def position(self) -> float:
        """Current playback position in seconds."""
        try:
            return self.player.time_pos or 0
        except (TypeError, ValueError):
            return 0

    @property
    def duration(self) -> float:
        """Total duration in seconds."""
        try:
            return self.player.duration or 0
        except (TypeError, ValueError):
            return 0

    @property
    def is_playing(self) -> bool:
        """Check if currently playing."""
        try:
            return not self.player.pause and not self.player.core_idle
        except:
            return False

    @property
    def is_paused(self) -> bool:
        """Check if paused."""
        try:
            return self.player.pause
        except:
            return False

    def toggle_shuffle(self):
        """Toggle shuffle mode."""
        self.shuffle_mode = not self.shuffle_mode
        if self.shuffle_mode:
            # Store original queue order
            self._original_queue = self.queue.copy()
            self._shuffle_history = (
                [self.current_index] if self.current_index >= 0 else []
            )
        else:
            # Restore original order
            if self._original_queue:
                current_song = (
                    self.queue[self.current_index] if self.current_index >= 0 else None
                )
                self.queue = self._original_queue.copy()
                # Find where current song ended up
                if current_song:
                    try:
                        self.current_index = next(
                            i
                            for i, s in enumerate(self.queue)
                            if s["id"] == current_song["id"]
                        )
                    except StopIteration:
                        self.current_index = 0
            self._shuffle_history.clear()

    def play_next(self):
        """Play the next song based on modes."""
        if not self.queue:
            return

        if self.repeat_mode == "one":
            self.play_index(self.current_index)
            return

        next_idx = None

        if self.shuffle_mode:
            # Smart shuffle: don't repeat until all songs played
            unplayed = [
                i for i in range(len(self.queue)) if i not in self._shuffle_history
            ]

            if unplayed:
                next_idx = random.choice(unplayed)
                self._shuffle_history.append(next_idx)
            else:
                # All songs played, reset history and pick random
                self._shuffle_history.clear()
                next_idx = random.randint(0, len(self.queue) - 1)
                self._shuffle_history.append(next_idx)
        else:
            next_idx = self.current_index + 1

            if next_idx >= len(self.queue):
                if self.repeat_mode == "all":
                    next_idx = 0
                else:
                    # End of queue
                    self.stop()
                    return

        self.play_index(next_idx)

    def play_prev(self):
        """Play previous song."""
        if not self.queue:
            return

        # If we are more than 3 seconds in, restart song
        if self.position > 3:
            self.seek(0)
            return

        if self.shuffle_mode:
            # Go back in shuffle history
            if len(self._shuffle_history) > 1:
                self._shuffle_history.pop()  # Remove current
                prev_idx = self._shuffle_history[-1]
                self.play_index(prev_idx)
            else:
                # Just replay current
                self.play_index(self.current_index)
        else:
            prev_idx = self.current_index - 1
            if prev_idx < 0:
                if self.repeat_mode == "all":
                    prev_idx = len(self.queue) - 1
                else:
                    prev_idx = 0

            self.play_index(prev_idx)

    def cycle_repeat(self):
        """Cycle through repeat modes."""
        modes = ["off", "all", "one"]
        current_idx = modes.index(self.repeat_mode)
        self.repeat_mode = modes[(current_idx + 1) % len(modes)]
        return self.repeat_mode

    def get_lyrics(self, video_id: str) -> str:
        """Fetch lyrics for a song with caching."""
        # Check cache first
        if video_id in self._lyrics_cache:
            return self._lyrics_cache[video_id]

        try:
            watch_data = self.api.get_watch_playlist(video_id)
            if not watch_data or "lyrics" not in watch_data:
                result = "♪ Lyrics not available for this song ♪"
                self._lyrics_cache[video_id] = result
                return result

            lyrics_id = watch_data["lyrics"]
            lyrics_data = self.api.get_lyrics(lyrics_id)

            if lyrics_data and "lyrics" in lyrics_data:
                result = lyrics_data["lyrics"]
                self._lyrics_cache[video_id] = result
                return result

            result = "♪ Lyrics text not found ♪"
            self._lyrics_cache[video_id] = result
            return result

        except Exception as e:
            result = f"✗ Error fetching lyrics: {str(e)}"
            return result

    def get_current_song(self) -> Optional[Dict]:
        """Get the currently playing song."""
        if 0 <= self.current_index < len(self.queue):
            return self.queue[self.current_index]
        return None
