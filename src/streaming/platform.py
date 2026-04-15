"""
platform.py
-----------
Implement the central StreamingPlatform class that orchestrates all domain entities
and provides query methods for analytics.

Classes to implement:
  - StreamingPlatform
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime, timedelta

from streaming.users import PremiumUser, FreeUser, FamilyAccountUser, FamilyMember
from streaming.tracks import Song
from streaming.playlists import CollaborativePlaylist

if TYPE_CHECKING:
  from streaming.users import User
  from streaming.tracks import Track
  from streaming.artists import Artist
  from streaming.albums import Album
  from streaming.playlists import Playlist
  from streaming.sessions import ListeningSession

class StreamingPlatform:
  def __init__(self, name:str):
    self.name = name
    self._catalogue: dict[str, Track] = {}
    self._users: dict[str, User] = {}
    self._artists: dict[str, Artist] = {}
    self._albums: dict[str, Album] = {}
    self._playlists: dict[str, Playlist] = {}
    self._sessions: list[ListeningSession] = []
  
  def add_track(self, track: Track):
    self._catalogue[track.track_id] = track
  
  def add_user(self, user: User):
    self._users[user.user_id] = user
  
  def add_artist(self, artist: Artist):
    self._artists[artist.artist_id] = artist
  
  def add_album(self, album: Album):
    self._albums[album.album_id] = album
  
  def add_playlist(self, playlist: Playlist):
    self._playlists[playlist.playlist_id] = playlist
  
  def record_session(self, session: ListeningSession):
    self._sessions.append(session)
    session.user.add_session(session)
  
  def get_track(self, track_id: str) -> Track | None:
    return self._catalogue.get(track_id)
  
  def get_user(self, user_id: str) -> User | None:
    return self._users.get(user_id)
  
  def get_artist(self, artist_id: str) -> Artist | None:
    return self._artists.get(artist_id)
  
  def get_album(self, album_id: str) -> Album | None:
    return self._albums.get(album_id)
  
  def all_users(self) -> list[User]:
    return list(self._users.values())
  
  def all_tracks(self) -> list[Track]:
    return list(self._catalogue.values())
  
  # ___________________ 10 Query Methods ______________________
  
  # Q1
  def total_listening_time_minutes(self, start: datetime, end: datetime) -> float:
    """Returns total listening time in minutes accross the platform for every session"""
    return sum(session.duration_listened_minutes() for session in self._sessions if start <= session.timestamp <= end)
  
  # Q2
  def avg_unique_tracks_per_premium_user(self, days: int = 30) -> float:
    """Gets all the premium users from the platform and then makes a list of length of unique tracks for each premium user"""
    """When going through sessions it checks if the session timestamp matches with the cutoff time defined at the beginning"""
    """At the end, a simple arithmetic mean is calculated for the average"""
    from_date = datetime.now() - timedelta(days=days)
    premium_users = [user for user in self.all_users() if isinstance(user, PremiumUser)]
    
    if len(premium_users) == 0:
      return 0.0
    
    unique_tracks_count = [len({s.track.track_id for s in self._sessions if s.timestamp >= from_date and s.user == user})
                           for user in premium_users]
    
    return sum(unique_tracks_count) / len(unique_tracks_count)
  
  # Q3
  def track_with_most_distinct_listeners(self) -> Track | None:
    """Creates a dictionary storing track as key and a set of users as value"""
    """At the end gets the maximum element from the dictionary based of the length of value which is simply number of disctinct listeners"""
    if len(self._sessions) == 0:
      return None
    
    track_user = {}
    for session in self._sessions:
      track_id = session.track.track_id
      user = session.user
      
      if track_id not in track_user:
        track_user[track_id] = set()
      
      track_user[track_id].add(user)
    
    max_track_id = max(track_user.items(), key = lambda x: len(x[1]))[0]
    return self.get_track(max_track_id)
  
  # Q4
  def avg_session_duration_by_user_type(self) -> list[tuple[str, float]]:
    """avg(lst) function calculates arithmetic mean of a list"""
    """get_users_avg_by_type(type) runs avg() function on a list containing durations of listening times for respective users"""
    """get_users_avg_by_type(type) was created to avoid redundancy and to make the code more clear"""
    
    def avg(lst):
      return sum(lst) / len(lst) if lst else 0.0
    
    def get_users_avg_by_type(type):
      return avg([session.duration_listened_seconds for session in self._sessions if isinstance(session.user, type)])
    
    types_averages = {
      "FreeUser" : get_users_avg_by_type(FreeUser),
      "PremiumUser" : get_users_avg_by_type(PremiumUser),
      "FamilyAccountUser" : get_users_avg_by_type(FamilyAccountUser),
      "FamilyMember" : get_users_avg_by_type(FamilyMember)
    }
    
    return sorted(types_averages.items(), key=lambda x: x[1], reverse=True)
  
  # Q5
  def total_listening_time_underage_sub_users_minutes(self, age_threshold: int = 18) -> float:
    """Gets total listening times in minutes for all FamilyMember users under age_threshold"""
    return sum(user.total_listening_minutes() for user in self.all_users()
               if isinstance(user, FamilyMember) and user.age < age_threshold)
  
  # Q6
  def top_artists_by_listening_time(self, n: int = 5) -> list[tuple[Artist, float]]:
    """Creates a dictionary having artists as keys and their listening time as values"""
    """If artist does not exists, key is initialized with value 0, and afterwards it just adds up the durations to the value"""
    """A reversely sorted list based on the value is returned at the end"""
    """[:n] specifies top return top n elements"""
    artist_listening_time = {}
    for session in self._sessions:
      if isinstance(session.track, Song):
        artist = session.track.artist
        artist_listening_time[artist] = artist_listening_time.get(artist, 0) + session.duration_listened_minutes()
    
    return sorted(artist_listening_time.items(), key=lambda x: x[1], reverse=True)[:n]
  
  # Q7
  def user_top_genre(self, user_id: str) -> tuple[str, float] | None:
    """Function gets genre with most listening time for a user prioritizing count, if counts are same it checks duration"""
    """Tries to get user object through user_id and if user does not exist it returns None"""
    """Fetches all sessions of that user"""
    """Creates dictionary that stores genres as keys and a dictionary of count and duration as values"""
    """Checks maximum count first. If there are multiple elements with same max count, it checks max duration"""
    user = self.get_user(user_id)
    if not user:
      return None
    
    user_sessions = [session for session in self._sessions if session.user == user]
    
    if not user_sessions:
      return None
    
    genre_info = {}
    for session in user_sessions:
        genre = session.track.genre
        if genre not in genre_info:
          genre_info[genre] = {"count": 0, "duration": 0}
        
        genre_info[genre]["count"] += 1
        genre_info[genre]["duration"] += session.duration_listened_seconds
    
    # Max count value
    max_count = max(info["count"] for info in genre_info.values()) 
    
    # Elements with the max count value that may have different durations
    same_val_max = [(genre, info["duration"]) for genre, info in genre_info.items() if info["count"] == max_count]
    
    # Calculates maxium based on durations of the elements containing the max count
    most_frequent_genre = max(same_val_max, key=lambda x: x[1])[0]
    
    duration_most_frequent = genre_info[most_frequent_genre]["duration"]
    total_duration = sum(info["duration"] for info in genre_info.values())
    
    percentage = (duration_most_frequent / total_duration) * 100 if total_duration > 0 else 0
    
    return (most_frequent_genre, percentage)
  
  # Q8
  def collaborative_playlists_with_many_artists(self, threshold: int = 3) -> list[CollaborativePlaylist]:
    """get_unique_artists(lst) gets unique artists for all tracks in playlist tracks"""
    """Loops and gets CollaborativePlaylists if length of unique artists of that playlist is greater than threshold"""
    def get_unique_artists(lst):
      return {track.artist.artist_id for track in lst if isinstance(track, Song)}
    
    return [playlist for playlist in self._playlists.values()
            if isinstance(playlist, CollaborativePlaylist) and len(get_unique_artists(playlist.tracks)) > threshold]
  
  # Q9
  def avg_tracks_per_playlist_type(self) -> dict[str, float]:
    """Returns average number of tracks for Playlist and CollaborativePlaylist"""
    def get_playlists(collaborative):
      return [len(playlist.tracks) for playlist in self._playlists.values() if isinstance(playlist, CollaborativePlaylist) == collaborative]
    
    superclass_playlists = get_playlists(collaborative=False)
    collaborative_playlists = get_playlists(collaborative=True)
    
    def avg(lst):
      return sum(lst) / len(lst) if lst else 0.0
    
    return {
      "Playlist" : avg(superclass_playlists),
      "CollaborativePlaylist" : avg(collaborative_playlists)
    }
  
  # Q10
  def users_who_completed_albums(self) -> list[tuple[User, list[str]]]:
    """Fetches all albums that have tracks"""
    """For each user it fetches their unique tracks listened"""
    """Gets album title for each album if the track ids of the album are a subset of unique user tracks"""
    """Example: track ids = {1, 2, 3} and user tracks listened = {1, 2, 3, 4}. Meaning track ids are a subset of user tracks listened"""
    valid_albums = [album for album in self._albums.values() if album.tracks]
    
    result = []
    
    for user in self.all_users():
      unique_user_tracks = user.unique_tracks_listened()
      completed_albums = [album.title for album in valid_albums if album.track_ids().issubset(unique_user_tracks)]
      
      if completed_albums:
        result.append((user, completed_albums))
        
    return result