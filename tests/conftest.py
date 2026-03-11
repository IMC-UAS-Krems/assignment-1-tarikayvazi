"""
conftest.py
-----------
Shared pytest fixtures used by both the public and private test suites.
"""

import pytest
from datetime import date, datetime, timedelta

from streaming.platform import StreamingPlatform
from streaming.artists import Artist
from streaming.albums import Album
from streaming.tracks import (
    AlbumTrack,
    SingleRelease,
    InterviewEpisode,
    NarrativeEpisode,
    AudiobookTrack,
)
from streaming.users import FreeUser, PremiumUser, FamilyAccountUser, FamilyMember
from streaming.sessions import ListeningSession
from streaming.playlists import Playlist, CollaborativePlaylist


# ---------------------------------------------------------------------------
# Helper - timestamps relative to the real current time so that the
# "last 30 days" window in Q2 always contains RECENT sessions.
# ---------------------------------------------------------------------------
FIXED_NOW = datetime.now().replace(microsecond=0)
RECENT = FIXED_NOW - timedelta(days=10)   # well within 30-day window
OLD    = FIXED_NOW - timedelta(days=60)   # outside 30-day window


@pytest.fixture
def platform() -> StreamingPlatform:
    """Return a fully populated StreamingPlatform instance."""
    platform = StreamingPlatform("TestStream")

    # ------------------------------------------------------------------
    # Artists
    # ------------------------------------------------------------------
    pixels = Artist("a1", "Pixels", genre="pop")
    rocker = Artist("a2", "Rocker", genre="rock")
    hiphoper = Artist("a3", "Hip-Hopper", genre="hip-hop")
    electro = Artist("a4", "ElectroWave", genre="electronic")
    classical = Artist("a5", "ClassicSoul", genre="classical")
    jazz = Artist("a6", "JazzMaster", genre="jazz")
    folk = Artist("a7", "FolkSinger", genre="folk")
    
    for a in (pixels, rocker, hiphoper, electro, classical, jazz, folk):
        platform.add_artist(a)

    # ------------------------------------------------------------------
    # Albums & AlbumTracks
    # ------------------------------------------------------------------
    dd = Album("alb1", "Digital Dreams", artist=pixels, release_year=2022)
    ad = Album("alb2", "Analogue Dreams", artist=rocker, release_year=2021)
    dh = Album("alb3", "Digital Hallucinacions", artist=hiphoper, release_year=2020)
    ae = Album("alb4", "Neon Lights", electro, 2023)
    ac = Album("alb5", "Symphony One", classical, 2019)
    jz = Album("alb6", "Jazzz", jazz, 2019)
    fk = Album("alb7", "Folkkk", folk, 2019)
    
    t1 = AlbumTrack("t1", "Pixel Rain", 180, "pop", artist=pixels, track_number=1)
    t2 = AlbumTrack("t2", "Grid Horizon", 210, "pop", artist=pixels, track_number=2)
    t3 = AlbumTrack("t3", "Vector Fields", 195, "pop", artist=pixels, track_number=3)
    
    t4 = AlbumTrack("t4", "Pixel Snow", 240, "rock", artist=rocker, track_number=1)
    t5 = AlbumTrack("t5", "Flexbox Horizon", 200, "rock", artist=rocker, track_number=2)
    
    t6 = AlbumTrack("t6", "Matrix Fields", 300, "hiphop", artist=hiphoper, track_number=1)
    
    t7 = AlbumTrack("t7", "Neon Pulse", 260, "electronic", artist=electro, track_number=1)
    t8 = AlbumTrack("t8", "Midnight Circuit", 220, "electronic", artist=electro, track_number=2)
    
    t9 = AlbumTrack("t9", "Allegro", 400, "classical", artist=classical,track_number= 1)
    t10 = AlbumTrack("t10", "Adagio", 500, "classical", artist=classical, track_number=2)
    
    t11 = AlbumTrack("t11", "Jazz Standard", 250, "jazz", artist=jazz, track_number=1)
    t12 = AlbumTrack("t12", "Smooth Night", 280, "jazz", artist=jazz, track_number=2)

    t13 = AlbumTrack("t13", "Mountain Story", 230, "folk", artist=folk, track_number=1)
    t14 = AlbumTrack("t14", "River Song", 210, "folk", artist=folk, track_number=2)
    
    for album, tracks in [(dd, [t1, t2, t3]), (ad, [t4, t5]), (dh, [t6]), (ae, [t7, t8]), (ac, [t9, t10]), (jz, [t11, t12]), (fk, [t13, t14])]:
        for track in tracks:
            album.add_track(track)
            platform.add_track(track)
            album.artist.add_track(track)
        platform.add_album(album)
    
    # ------------------------------------------------------------------
    # Different Tracks
    # ------------------------------------------------------------------
    
    single = SingleRelease("t11", "Single Hit", 200, "pop", pixels, release_date=date(2026, 3, 3))
    pixels.add_track(single)
    
    interview = InterviewEpisode("t12", "OOP with Dr. Stefan Klikovits", 2000, "tech", host="HighSchool Tarik AYVAZI", guest="Dr. Stefan Klikovits")
    narrative = NarrativeEpisode("t13", "Random Narrative", 1500, "random", "Tarik AYVAZI", season=2, episode_number=1)
    
    audiobook = AudiobookTrack("t14", "Krems History", 2300, "history", author="Tarik", narrator="AYVAZI")
    
    for track in (single, interview, narrative, audiobook):
        platform.add_track(track)
        
    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------
    alice = FreeUser("u1", "Alice", age=30)
    
    bob = PremiumUser("u2", "Bob", age=25, subscription_start=date(2023, 1, 1))
    prem2 = PremiumUser("u3", "Premium 2", 28, date(2025, 2, 10))
    prem3 = PremiumUser("u4", "Premium 3", 35, date(2022, 7, 1))
    prem4 = PremiumUser("u5", "Premium 4", 22, date(2026, 1, 1))
    prem5 = PremiumUser("u6", "Premium 5", 40, date(2025, 5, 30))
    prem6 = PremiumUser("u7", "Premium 6", 31, date(2023, 12, 31))
    
    parent = FamilyAccountUser("u8", "Parent", age=40)
    child1 = FamilyMember("u9", "Child 1", age=13, parent=parent)
    child2 = FamilyMember("u10", "Child 2", age=16, parent=parent)
    member3 = FamilyMember("u11", "Overage Member", age=21, parent=parent)
    
    for user in (alice, bob, prem2, prem3, prem4, prem5, prem6, parent, child1, child2, member3):
        platform.add_user(user)

    # ------------------------------------------------------------------
    # Listening Sessions
    # ------------------------------------------------------------------
    sessions = [
        
        ListeningSession("s1", alice, t1, RECENT, 180),
        ListeningSession("s2", alice, t1, RECENT, 180),
        ListeningSession("s3", alice, t2, RECENT, 210),
        ListeningSession("s4", alice, t3, RECENT, 195),
        ListeningSession("s5", alice, t4, OLD, 240),

        ListeningSession("s6", bob, t1, RECENT, 180),
        ListeningSession("s7", bob, t1, RECENT, 180),
        ListeningSession("s8", bob, t4, RECENT, 240),
        ListeningSession("s9", bob, t4, RECENT, 240),
        ListeningSession("s10", bob, t6, RECENT, 300),
        ListeningSession("s11", bob, t7, RECENT, 260),
        ListeningSession("s12", bob, t7, RECENT, 260),

        ListeningSession("s13", prem2, t1, RECENT, 180),
        ListeningSession("s14", prem2, t2, RECENT, 210),
        ListeningSession("s15", prem2, t3, RECENT, 195),
        ListeningSession("s16", prem2, t3, OLD, 195),
        ListeningSession("s17", prem2, t7, RECENT, 260),

        ListeningSession("s18", prem3, t4, RECENT, 240),
        ListeningSession("s19", prem3, t5, RECENT, 200),
        ListeningSession("s20", prem3, t5, RECENT, 200),
        ListeningSession("s21", prem3, t8, OLD, 220),

        ListeningSession("s22", prem4, t6, RECENT, 300),
        ListeningSession("s23", prem4, t6, RECENT, 300),
        ListeningSession("s24", prem4, t1, RECENT, 180),
        ListeningSession("s25", prem4, t8, RECENT, 220),

        ListeningSession("s26", prem5, single, RECENT, 200),
        ListeningSession("s27", prem5, single, RECENT, 200),
        ListeningSession("s28", prem5, t4, RECENT, 240),
        ListeningSession("s29", prem5, t1, OLD, 180),

        ListeningSession("s30", prem6, t5, RECENT, 200),
        ListeningSession("s31", prem6, t6, RECENT, 300),
        ListeningSession("s32", prem6, t6, RECENT, 300),
        ListeningSession("s33", prem6, t1, RECENT, 180),
        
        ListeningSession("s34", child1, t1, RECENT, 180),
        
        ListeningSession("s35", member3, t1, RECENT, 180),
        
        ListeningSession("s36", alice, t11, RECENT, 250),
        
        ListeningSession("s37", parent, t13, RECENT, 230)
    ]
    
    for session in sessions:
        platform.record_session(session)
        
    # ------------------------------------------------------------------
    # Playlists
    # ------------------------------------------------------------------
    
    p1 = Playlist("p1", "Alice Summer Mix", alice)
    for track in (t1, t4, t6):
        p1.add_track(track)
    
    cp1 = CollaborativePlaylist("cp1", "Collaborative Mix", bob)
    for c in (alice, child2):
        cp1.add_contributor(c)
    for track in (t1, t4, t6):
        cp1.add_track(track)
        
    cp2 = CollaborativePlaylist("cp2", "Diverse Mix", prem2)
    for c in (bob, child1, prem3):
        cp2.add_contributor(c)
    for track in (t1, t4, t6, t7):
        cp2.add_track(track)
        
    cp3 = CollaborativePlaylist("cp3", "Ultimate Mix", prem4)
    for c in (alice, bob, prem2, prem3, prem5, prem6):
        cp3.add_contributor(c)
    for track in (t1, t4, t6, t7, t11, t13):
        cp3.add_track(track)
        
    cp4 = CollaborativePlaylist("cp4", "Pixels Only", child1)
    for c in (child2, member3):
        cp4.add_contributor(c)
    for track in (t1, t2, t3):
        cp4.add_track(track)
        
    for playlist in (p1, cp1, cp2, cp3, cp4):
        platform.add_playlist(playlist)

    return platform


@pytest.fixture
def fixed_now() -> datetime:
    """Expose the shared FIXED_NOW constant to tests."""
    return FIXED_NOW


@pytest.fixture
def recent_ts() -> datetime:
    return RECENT


@pytest.fixture
def old_ts() -> datetime:
    return OLD
