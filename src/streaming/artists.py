"""
artists.py
----------
Implement the Artist class representing musicians and content creators.

Classes to implement:
  - Artist
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from streaming.tracks import Track

class Artist:
  def __init__(self, artist_id:str, name:str, genre:str):
    self.artist_id = artist_id
    self.name = name
    self.genre = genre
    self.tracks: list[Track] = []
    
  def add_track(self, track: Track):
    self.tracks.append(track)
  
  def track_count(self) -> int:
    return len(self.tracks)