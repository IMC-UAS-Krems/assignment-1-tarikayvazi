"""
albums.py
---------
Implement the Album class for collections of AlbumTrack objects.

Classes to implement:
  - Album
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from streaming.artists import Artist
  from streaming.tracks import AlbumTrack

class Album:
  def __init__(self, album_id:str, title:str, artist:Artist, release_year:int):
    self.album_id = album_id
    self.title = title
    self.artist = artist
    self.release_year = release_year
    self.tracks: list[AlbumTrack] = []
    
  def add_track(self, track: AlbumTrack):
    track.album = self
    self.tracks.append(track)
    self.tracks.sort(key=lambda x: x.track_number) # SATISFY test_add_track_sorts_by_number(self)
  
  def track_ids(self) -> set[str]:
    return {t.track_id for t in self.tracks}
  
  def duration_seconds(self) -> int:
    return sum(t.duration_seconds for t in self.tracks)