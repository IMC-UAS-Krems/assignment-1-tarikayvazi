"""
platform.py
-----------
Implement the central StreamingPlatform class that orchestrates all domain entities
and provides query methods for analytics.

Classes to implement:
  - StreamingPlatform
"""
from datetime import datetime, timedelta
from streaming.users import User, PremiumUser, FreeUser, FamilyAccountUser, FamilyMember
from streaming.tracks import Track, Song
from streaming.artists import Artist
from streaming.albums import Album
from streaming.playlists import Playlist, CollaborativePlaylist
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
  
  def add_track(self, track):
    self._catalogue[track.track_id] = track
  
  def add_user(self, user):
    self._users[user.user_id] = user
  
  def add_artist(self, artist):
    self._artists[artist.artist_id] = artist
  
  def add_album(self, album):
    self._albums[album.album_id] = album
  
  def add_playlist(self, playlist):
    self._playlists[playlist.playlist_id] = playlist
  
  def record_session(self, session):
    self._sessions.append(session)
    session.user.add_session(session)
  
  def get_track(self, track_id) -> Track | None:
    return self._catalogue.get(track_id)
  
  def get_user(self, user_id) -> User | None:
    return self._users.get(user_id)
  
  def get_artist(self, artist_id) -> Artist | None:
    return self._artists.get(artist_id)
  
  def get_album(self, album_id) -> Album | None:
    return self._albums.get(album_id)
  
  def all_users(self) -> list[User]:
    return list(self._users.values())
  
  def all_tracks(self) -> list[Track]:
    return list(self._catalogue.values())
  
  # ___________________ 10 Query Methods ______________________
  
  # Q1
  def total_listening_time_minutes(self, start: datetime, end: datetime) -> float:
    return sum(session.duration_listened_minutes() for session in self._sessions if start <= session.timestamp <= end)
  
  # Q2
  def avg_unique_tracks_per_premium_user(self, days: int = 30) -> float:
    from_date = datetime.now() - timedelta(days=days)
    premium_users = [user for user in self.all_users() if isinstance(user, PremiumUser)]
    
    if len(premium_users) == 0:
      return 0.0
    
    unique_tracks_count = [len({s.track.track_id for s in self._sessions if s.timestamp >= from_date and s.user == user})
                           for user in premium_users]
    
    return sum(unique_tracks_count) / len(unique_tracks_count)
  
  # Q3
  def track_with_most_distinct_listeners(self) -> Track | None:
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
    return sum(user.total_listening_minutes() for user in self.all_users() if isinstance(user, FamilyMember) and user.age < age_threshold)
  
  # Q6
  def top_artists_by_listening_time(self, n: int = 5) -> list[tuple[Artist, float]]:
    artist_listening_time = {}
    for session in self._sessions:
      if isinstance(session.track, Song):
        artist = session.track.artist
        artist_listening_time[artist] = artist_listening_time.get(artist, 0) + session.duration_listened_minutes()
    
    return sorted(artist_listening_time.items(), key=lambda x: x[1], reverse=True)[:n]
  
  # Q7
  def user_top_genre(self, user_id: str) -> tuple[str, float] | None:
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
        
    max_count = max(info["count"] for info in genre_info.values())
    
    same_val_max = [(genre, info["duration"]) for genre, info in genre_info.items() if info["count"] == max_count]
      
    most_frequent_genre = max(same_val_max, key=lambda x: x[1])[0]
    
    duration_most_frequent = genre_info[most_frequent_genre]["duration"]
    total_duration = sum(info["duration"] for info in genre_info.values())
    
    percentage = (duration_most_frequent / total_duration) * 100 if total_duration > 0 else 0
    
    return (most_frequent_genre, percentage)
  
  # Q8
  def collaborative_playlists_with_many_artists(self, threshold: int = 3) -> list[CollaborativePlaylist]:
    
    def get_unique_artists(lst):
      return {track.artist.artist_id for track in lst if isinstance(track, Song)}
    
    return [playlist for playlist in self._playlists.values()
            if isinstance(playlist, CollaborativePlaylist) and len(get_unique_artists(playlist.tracks)) > threshold]
  
  # Q9
  def avg_tracks_per_playlist_type(self) -> dict[str, float]:
    
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
    
    valid_albums = [album for album in self._albums.values() if album.tracks]
    
    result = []
    
    for user in self.all_users():
      unique_user_tracks = user.unique_tracks_listened()
      completed_albums = [album.title for album in valid_albums if album.track_ids().issubset(unique_user_tracks)]
      
      if completed_albums:
        result.append((user, completed_albums))
        
    return result