"""
playlists.py
------------
Implement playlist classes for organizing tracks.

Classes to implement:
  - Playlist
    - CollaborativePlaylist
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from streaming.users import User
  from streaming.tracks import Track

class Playlist:
  def __init__(self, playlist_id:str, name:str, owner:User):
    self.playlist_id = playlist_id
    self.name = name
    self.owner = owner
    self.tracks: list[Track] = []
    
  def add_track(self, track):
    if track not in self.tracks:
      self.tracks.append(track)
  
  def remove_track(self, track_id):
    self.tracks = [t for t in self.tracks if t.track_id != track_id]
  
  def total_duration_seconds(self) -> int:
    return sum(t.duration_seconds for t in self.tracks)
  

class CollaborativePlaylist(Playlist):
  def __init__(self, playlist_id:str, name:str, owner:User):
    super().__init__(playlist_id, name, owner)
    self.contributors: list[User] = [owner] # owner by default
    
  def add_contributor(self, user):
    if user not in self.contributors:
      self.contributors.append(user)
  
  def remove_contributor(self, user):
    if user != self.owner:
      self.contributors = [c for c in self.contributors if c != user]