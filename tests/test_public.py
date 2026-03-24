"""
test_public.py
--------------
Public test suite template.

This file provides a minimal framework and examples to guide you in writing
comprehensive tests for your StreamingPlatform implementation. Each test class
corresponds to one of the 10 query methods (Q1-Q10).

You should:
1. Study the examples provided
2. Complete the stub tests (marked with TODO or pass statements)
3. Add additional test cases for edge cases and boundary conditions
4. Verify your implementation passes all tests

Run with:
    pytest tests/test_public.py -v
"""

import pytest
from datetime import datetime, timedelta
from conftest import FIXED_NOW, RECENT, OLD
from streaming.platform import StreamingPlatform
from streaming.users import FreeUser, PremiumUser, FamilyAccountUser, FamilyMember
from streaming.playlists import Playlist, CollaborativePlaylist
from streaming.artists import Artist
from streaming.tracks import Track, AlbumTrack, Song
from streaming.albums import Album
from streaming.sessions import ListeningSession

# ===========================================================================
# Q1 - Total cumulative listening time for a given period
# ===========================================================================

class TestTotalListeningTime:
    """Test the total_listening_time_minutes(start, end) method.
    
    This method should sum up all session durations that fall within
    the specified datetime window (inclusive on both ends).
    """

    def test_returns_float(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a float."""
        start = RECENT - timedelta(hours=1)
        end = FIXED_NOW
        result = platform.total_listening_time_minutes(start, end)
        assert isinstance(result, float)

    def test_empty_window_returns_zero(self, platform: StreamingPlatform) -> None:
        """Test that a time window with no sessions returns 0.0."""
        far_future = FIXED_NOW + timedelta(days=365)
        result = platform.total_listening_time_minutes(
            far_future, far_future + timedelta(hours=1)
        )
        assert result == 0.0

    # TODO: Add a test that verifies the correct value for a known time period.
    #       Calculate the expected total based on the fixture data in conftest.py.
    
    global expected_recent_seconds
    expected_recent_seconds = sum([
        180, 180, 210, 195,
        180, 180, 240, 240, 300, 260, 260,
        180, 210, 195, 260,
        240, 200, 200,
        300, 300, 180, 220,
        200, 200, 240,
        200, 300, 300, 180,
        180,
        180,
        250,
        230
    ])
    
    global expected_old_seconds
    expected_old_seconds = sum([240, 195, 220, 180])
    
    global expected_recent_minutes
    expected_recent_minutes = expected_recent_seconds / 60
    
    def test_known_period_value(self, platform: StreamingPlatform) -> None:
        start = RECENT - timedelta(days=1)
        end = RECENT + timedelta(days=1)
        result = platform.total_listening_time_minutes(start, end)
        
        assert expected_recent_minutes == result
    
    # __________ADDITIONAL____________
    
    def test_known_period_value_inclusivity(self, platform: StreamingPlatform) -> None:
        result_start = platform.total_listening_time_minutes(RECENT, RECENT + timedelta(days=1))
        result_end = platform.total_listening_time_minutes(RECENT - timedelta(days=1), RECENT)
        
        assert expected_recent_minutes == result_start
        assert expected_recent_minutes == result_end
        
    def test_known_period_value_exact(self, platform: StreamingPlatform) -> None:
        result = platform.total_listening_time_minutes(RECENT, RECENT)
        
        assert expected_recent_minutes == result
        
    def test_known_period_value_including_old(self, platform: StreamingPlatform) -> None:
        total_seconds = expected_old_seconds + expected_recent_seconds
        total_minutes = total_seconds / 60
        
        start_before_old = OLD - timedelta(days=1)
        end_after_recent = RECENT + timedelta(days=1)
        
        result = platform.total_listening_time_minutes(start_before_old, end_after_recent)
        
        assert total_minutes == result

# ===========================================================================
# Q2 - Average unique tracks per PremiumUser in the last N days
# ===========================================================================

class TestAvgUniqueTracksPremium:
    """Test the avg_unique_tracks_per_premium_user(days) method.
    
    This method should:
    - Count distinct tracks per PremiumUser in the last N days
    - Exclude FreeUser, FamilyAccountUser, and FamilyMember
    - Return 0.0 if there are no premium users
    """

    def test_returns_float(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a float."""
        result = platform.avg_unique_tracks_per_premium_user(days=30)
        assert isinstance(result, float)

    def test_no_premium_users_returns_zero(self) -> None:
        """Test with a platform that has no premium users."""
        p = StreamingPlatform("EmptyPlatform")
        p.add_user(FreeUser("u99", "Nobody", age=25))
        assert p.avg_unique_tracks_per_premium_user() == 0.0

    # TODO: Add a test with the fixture platform that verifies the correct
    #       average for premium users. You'll need to count unique tracks
    #       per premium user and calculate the average.
    
    def test_correct_value(self, platform: StreamingPlatform) -> None:
        expected_counts = [4, 4, 2, 3, 2, 3] # bob + prem2-6 (ONLY RECENT unique tracks)
        expected_average = sum(expected_counts) / len(expected_counts)
        
        result = platform.avg_unique_tracks_per_premium_user()
        
        assert result == expected_average
        
    # __________ADDITIONAL____________
    
    def test_1day(self, platform: StreamingPlatform) -> None:
        result_1day = platform.avg_unique_tracks_per_premium_user(days=1)
        assert result_1day == 0.0
        
    def test_100days(self, platform: StreamingPlatform) -> None:
        result_100days = platform.avg_unique_tracks_per_premium_user(days=100)
        expected_100days = [4, 4, 3, 3, 3, 3] # All time
        
        assert result_100days == sum(expected_100days) / len(expected_100days)

# ===========================================================================
# Q3 - Track with the most distinct listeners
# ===========================================================================

class TestTrackMostDistinctListeners:
    """Test the track_with_most_distinct_listeners() method.
    
    This method should:
    - Count the number of unique users who have listened to each track
    - Return the track with the highest count
    - Return None if the platform has no sessions
    """

    def test_empty_platform_returns_none(self) -> None:
        """Test that an empty platform returns None."""
        p = StreamingPlatform("Empty")
        assert p.track_with_most_distinct_listeners() is None

    # TODO: Add a test that verifies the correct track is returned.
    #       Count listeners per track from the fixture data.
    def test_correct_track(self, platform: StreamingPlatform) -> None:
        correct_track = "t1"
        result = platform.track_with_most_distinct_listeners()
        
        assert result is not None
        assert result.track_id == correct_track
        
    # __________ADDITIONAL____________
    
    def test_single_session(self) -> None:
        new_platform = StreamingPlatform("SingleSession")
        
        test_track = Track("test1", "Test Track", 100, "pop")
        test_user = FreeUser("u1", "Test User", 25)
        
        new_platform.add_track(test_track)
        new_platform.add_user(test_user)
        
        test_session = ListeningSession("s1", test_user, test_track, datetime.now(), 180)
        new_platform.record_session(test_session)
        
        result = new_platform.track_with_most_distinct_listeners()
        assert result is not None
        assert result.track_id == "test1"


# ===========================================================================
# Q4 - Average session duration per user subtype, ranked
# ===========================================================================

class TestAvgSessionDurationByType:
    """Test the avg_session_duration_by_user_type() method.
    
    This method should:
    - Calculate average session duration (in seconds) for each user type
    - Return a list of (type_name, average_duration) tuples
    - Sort results from longest to shortest duration
    """

    def test_returns_list_of_tuples(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a list of (str, float) tuples."""
        result = platform.avg_session_duration_by_user_type()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, tuple) and len(item) == 2
            assert isinstance(item[0], str) and isinstance(item[1], float)

    def test_sorted_descending(self, platform: StreamingPlatform) -> None:
        """Verify results are sorted by duration (longest first)."""
        result = platform.avg_session_duration_by_user_type()
        durations = [r[1] for r in result]
        assert durations == sorted(durations, reverse=True)

    # TODO: Add tests to verify all user types are present and have correct averages.
    def test_all_user_types_present(self, platform: StreamingPlatform) -> None:
        result = platform.avg_session_duration_by_user_type()
        
        types_result = [i[0] for i in result]
        expected_types = ["FreeUser", "PremiumUser", "FamilyAccountUser", "FamilyMember"]
        
        for expected in expected_types:
            assert expected in types_result
        
    # __________ADDITIONAL____________
    
    def test_correct_averages(self, platform: StreamingPlatform) -> None:
        result = platform.avg_session_duration_by_user_type()
        result_dict = dict(result)
        
        free_durations = [180, 180, 210, 195, 240, 250]
        expected_free_avg = sum(free_durations) / len(free_durations)
        assert expected_free_avg == result_dict["FreeUser"]
        
        premium_durations = [180,180,240,240,300,260,260,
                            180,210,195,195,260,
                            240,200,200,220,
                            300,300,180,220,
                            200,200,240,180,
                            200,300,300,180] 
        expected_premium_avg = sum(premium_durations) / len(premium_durations)
        assert expected_premium_avg == result_dict["PremiumUser"]
        
        family_account_user_durations = [230]
        expected_family_account_user = sum(family_account_user_durations) / len(family_account_user_durations)
        assert expected_family_account_user == result_dict["FamilyAccountUser"]
        
        family_member_durations = [180, 180]
        expected_family_member = sum(family_member_durations) / len(family_member_durations)
        assert expected_family_member == result_dict["FamilyMember"]


# ===========================================================================
# Q5 - Total listening time for underage sub-users
# ===========================================================================

class TestUnderageSubUserListening:
    """Test the total_listening_time_underage_sub_users_minutes(age_threshold) method.
    
    This method should:
    - Count only sessions for FamilyMember users under the age threshold
    - Convert to minutes
    - Return 0.0 if no underage users or their sessions exist
    """

    def test_returns_float(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a float."""
        result = platform.total_listening_time_underage_sub_users_minutes()
        assert isinstance(result, float)

    def test_no_family_users(self) -> None:
        """Test a platform with no family accounts."""
        p = StreamingPlatform("NoFamily")
        p.add_user(FreeUser("u1", "Solo", age=20))
        assert p.total_listening_time_underage_sub_users_minutes() == 0.0

    # TODO: Add tests for correct values with default and custom thresholds.
    def test_correct_value_default_threshold(self, platform: StreamingPlatform) -> None:
        assert platform.total_listening_time_underage_sub_users_minutes() == (180.0 / 60)

    def test_custom_threshold(self, platform: StreamingPlatform) -> None:
        assert platform.total_listening_time_underage_sub_users_minutes(age_threshold=22) == (360.0 / 60)
    
    # __________ADDITIONAL____________
    
    def test_threshold_zero(self, platform: StreamingPlatform) -> None:
        assert platform.total_listening_time_underage_sub_users_minutes(age_threshold=0) == 0.0
        
    def test_threshold_exclusivity(self, platform: StreamingPlatform) -> None:
        assert platform.total_listening_time_underage_sub_users_minutes(age_threshold=13) == 0.0
        assert platform.total_listening_time_underage_sub_users_minutes(age_threshold=21) == (180.0 / 60)


# ===========================================================================
# Q6 - Top N artists by total listening time
# ===========================================================================

class TestTopArtistsByListeningTime:
    """Test the top_artists_by_listening_time(n) method.
    
    This method should:
    - Rank artists by total cumulative listening time (minutes)
    - Only count Song tracks (exclude Podcast and AudiobookTrack)
    - Return a list of (Artist, minutes) tuples
    - Sort from highest to lowest listening time
    """

    def test_returns_list_of_tuples(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a list of (Artist, float) tuples."""
        from streaming.artists import Artist
        result = platform.top_artists_by_listening_time(n=3)
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, tuple) and len(item) == 2
            assert isinstance(item[0], Artist) and isinstance(item[1], float)

    def test_sorted_descending(self, platform: StreamingPlatform) -> None:
        """Verify results are sorted by listening time (highest first)."""
        result = platform.top_artists_by_listening_time(n=5)
        minutes = [r[1] for r in result]
        assert minutes == sorted(minutes, reverse=True)

    def test_respects_n_parameter(self, platform: StreamingPlatform) -> None:
        """Verify only the top N artists are returned."""
        result = platform.top_artists_by_listening_time(n=2)
        assert len(result) <= 2

    # TODO: Add a test that verifies the correct artists and values.
    def test_top_artist(self, platform: StreamingPlatform) -> None:
        result = platform.top_artists_by_listening_time(n=5)
        result_dict = {artist.name: minutes for artist, minutes in result}
        
        expected = {
            "Pixels": (180+180+210+195 + 180+180 + 180+210+195+195 + 180 + 200 + 200 + 180 + 180 + 180 + 180) / 60,
            "Rocker": (240 + 240+240 + 240 + 200+200+200 + 240) / 60,
            "Hip-Hopper": (300 + 300+300 + 300+300) / 60,
            "ElectroWave": (260+260 + 260 + 220 + 220) / 60,
            "JazzMaster" : (250) / 60
        }
        
        assert result_dict == pytest.approx(expected, rel=1e-19)
        
    # __________ADDITIONAL____________
    
    def test_proper_name_minutes_descend_order(self, platform: StreamingPlatform) -> None:
        result = platform.top_artists_by_listening_time(n=5)
        
        expected = [
            ("Pixels", (180+180+210+195 + 180+180 + 180+210+195+195 + 180 + 200 + 200 + 180 + 180 + 180 + 180) / 60),
            ("Rocker", (240 + 240+240 + 240 + 200+200+200 + 240) / 60),
            ("Hip-Hopper", (300 + 300+300 + 300+300) / 60),
            ("ElectroWave", (260+260 + 260 + 220 + 220) / 60),
            ("JazzMaster", (250) / 60)
        ]
        
        for i in range(5):
            assert result[i][0].name == expected[i][0]
            assert result[i][1] == pytest.approx(expected[i][1])
            
    def test_proper_name_minutes_descend_custom(self, platform: StreamingPlatform) -> None:
        result = platform.top_artists_by_listening_time(n=2)
        
        expected = [
            ("Pixels", (180+180+210+195 + 180+180 + 180+210+195+195 + 180 + 200 + 200 + 180 + 180 + 180 + 180) / 60),
            ("Rocker", (240 + 240+240 + 240 + 200+200+200 + 240) / 60)
        ]
        
        for i in range(2):
            assert result[i][0].name == expected[i][0]
            assert result[i][1] == pytest.approx(expected[i][1])
    
    def test_one_top_artist(self, platform: StreamingPlatform) -> None:
        result = platform.top_artists_by_listening_time(n=1)
        artist_name = result[0][0].name
        minutes = result[0][1]
        
        expected = (180+180+210+195 + 180+180 + 180+210+195+195 + 180 + 200 + 200 + 180 + 180 + 180 + 180) / 60
        
        assert artist_name == "Pixels"
        assert minutes == pytest.approx(expected, rel=1e-19)
        
    def test_n_zero(self, platform: StreamingPlatform) -> None:
        result = platform.top_artists_by_listening_time(n=0)
        assert len(result) == 0


# ===========================================================================
# Q7 - User's top genre and percentage
# ===========================================================================

class TestUserTopGenre:
    """Test the user_top_genre(user_id) method.
    
    This method should:
    - Find the genre with the most listening time for a user
    - Return (genre_name, percentage_of_total_time)
    - Return None if user doesn't exist or has no sessions
    """

    def test_returns_tuple_or_none(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a tuple or None."""
        result = platform.user_top_genre("u1")
        if result is not None:
            assert isinstance(result, tuple) and len(result) == 2
            assert isinstance(result[0], str) and isinstance(result[1], float)

    def test_nonexistent_user_returns_none(self, platform: StreamingPlatform) -> None:
        """Test that a nonexistent user ID returns None."""
        assert platform.user_top_genre("does_not_exist") is None

    def test_percentage_in_valid_range(self, platform: StreamingPlatform) -> None:
        """Verify percentage is between 0 and 100."""
        for user in platform.all_users():
            result = platform.user_top_genre(user.user_id)
            if result is not None:
                _, pct = result
                assert 0.0 <= pct <= 100.0

    # TODO: Add a test that verifies the correct genre and percentage for a known user.
    def test_correct_top_genre(self, platform: StreamingPlatform) -> None:
        result_1 = platform.user_top_genre("u1")
        if result_1 is not None:
            assert result_1[0] == "pop"
            assert result_1[1] == pytest.approx(60.95617529880478, rel=1e-9)
            
        result_2 = platform.user_top_genre("u2")
        if result_2 is not None:
            assert result_2[0] == "electronic"
            assert result_2[1] == pytest.approx(31.32530120481928, rel=1e-9)
    
    # __________ADDITIONAL____________
    
    def test_user_no_sessions(self, platform: StreamingPlatform) -> None:
        p = StreamingPlatform("Test")
        
        user = FreeUser("test_top_genre", "Dipl. Ing. Tarik AYVAZI", 18)
        p.add_user(user)
        
        result = p.user_top_genre(user.user_id)
        assert result == None
        
    def test_one_genre_user(self, platform: StreamingPlatform) -> None:
        result = platform.user_top_genre("u9")
        if result is not None:
            assert result[0] == "pop"
            assert result[1] == 100.0 # 100%
            
    def test_frequency_vs_duration_feature(self, platform: StreamingPlatform) -> None:
        
        # Tests 3x 50 seconds vs 1x 200 seconds, and because of frequency it should return (150/350)*100 not (200/350)*100
        
        p = StreamingPlatform("CustomGenres")
        
        artist = Artist("a1", "Test Artist", "pop")
        p.add_artist(artist)
        
        track_a1 = AlbumTrack("t1", "Track A1", 50, "genre_a", artist, 1)
        track_a2 = AlbumTrack("t2", "Track A2", 50, "genre_a", artist, 2)
        track_a3 = AlbumTrack("t3", "Track A3", 50, "genre_a", artist, 3)
        track_b = AlbumTrack("t4", "Track B", 200, "genre_b", artist, 4)
        
        for track in [track_a1, track_a2, track_a3, track_b]:
            p.add_track(track)
            
        user = FreeUser("u1", "Test User", 25)
        p.add_user(user)
        
        now = datetime.now()
        p.record_session(ListeningSession("s1", user, track_a1, now, 50))
        p.record_session(ListeningSession("s2", user, track_a2, now, 50))
        p.record_session(ListeningSession("s3", user, track_a3, now, 50))
        p.record_session(ListeningSession("s4", user, track_b, now, 200))
        
        result = p.user_top_genre("u1")
        assert result is not None
        assert result[0] == "genre_a"  # Most frequent by count
        assert result[1] == pytest.approx(42.85714285714286, rel=1e-9)


# ===========================================================================
# Q8 - CollaborativePlaylists with more than threshold distinct artists
# ===========================================================================

class TestCollaborativePlaylistsManyArtists:
    """Test the collaborative_playlists_with_many_artists(threshold) method.
    
    This method should:
    - Return all CollaborativePlaylist instances with >threshold distinct artists
    - Only count Song tracks (exclude Podcast and AudiobookTrack)
    - Return playlists in registration order
    """

    def test_returns_list_of_collaborative_playlists(
        self, platform: StreamingPlatform
    ) -> None:
        """Verify the method returns a list of CollaborativePlaylist objects."""
        result = platform.collaborative_playlists_with_many_artists()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, CollaborativePlaylist)

    def test_higher_threshold_returns_empty(
        self, platform: StreamingPlatform
    ) -> None:
        """Test that a high threshold returns an empty list."""
        result = platform.collaborative_playlists_with_many_artists(threshold=100)
        assert result == []

    # TODO: Add tests that verify the correct playlists are returned with
    #       different threshold values.
    def test_default_threshold(self, platform: StreamingPlatform) -> None:
        result = platform.collaborative_playlists_with_many_artists()
        
        playlist_ids = [playlist.playlist_id for playlist in result]
        assert playlist_ids == ["cp2", "cp3"]
        
    # __________ADDITIONAL____________
    
    def test_order_as_registered(self, platform: StreamingPlatform) -> None:
        result = platform.collaborative_playlists_with_many_artists(threshold=0)
        
        playlist_ids = [playlist.playlist_id for playlist in result]
        assert playlist_ids == ["cp1", "cp2", "cp3", "cp4"]
    
    def test_for_single_output(self, platform: StreamingPlatform) -> None:
        result = platform.collaborative_playlists_with_many_artists(threshold=5)
        
        playlist_ids = [playlist.playlist_id for playlist in result]
        assert playlist_ids == ["cp3"]

# ===========================================================================
# Q9 - Average tracks per playlist type
# ===========================================================================

class TestAvgTracksPerPlaylistType:
    """Test the avg_tracks_per_playlist_type() method.
    
    This method should:
    - Calculate average track count for standard Playlist instances
    - Calculate average track count for CollaborativePlaylist instances
    - Return a dict with keys "Playlist" and "CollaborativePlaylist"
    - Return 0.0 for types with no instances
    """

    def test_returns_dict_with_both_keys(
        self, platform: StreamingPlatform
    ) -> None:
        """Verify the method returns a dict with both playlist types."""
        result = platform.avg_tracks_per_playlist_type()
        assert isinstance(result, dict)
        assert "Playlist" in result
        assert "CollaborativePlaylist" in result

    # TODO: Add tests that verify the correct averages for each playlist type.
    def test_standard_playlist_average(self, platform: StreamingPlatform) -> None:
        result = platform.avg_tracks_per_playlist_type()["Playlist"]
        assert result == 3.0

    def test_collaborative_playlist_average(
        self, platform: StreamingPlatform
    ) -> None:
        result = platform.avg_tracks_per_playlist_type()["CollaborativePlaylist"]
        assert result == 4.0
        
    # __________ADDITIONAL____________
    
    def test_no_playlist_one_type(self, platform: StreamingPlatform) -> None:
        p = StreamingPlatform("Collaborative Empty")
        
        standard_playlist = Playlist("test_p", "Standard Playlist", FreeUser("user_test", "Tarik", 18))
        standard_playlist.add_track(AlbumTrack("test_t", "Track", 180, "pop", Artist("artist_test", "Artist", "pop"), 1))
        p.add_playlist(standard_playlist)
        
        result = p.avg_tracks_per_playlist_type()
        
        assert result == {
            "Playlist" : 1.0,
            "CollaborativePlaylist" : 0.0
        }

    def test_empty_playlist(self, platform: StreamingPlatform) -> None:
        p = StreamingPlatform("Empty Playlist Platform")
        
        u = FreeUser("user_2", "Tarik", 18)
        playlist = Playlist("test_playlist", "Standard Playlist", u)
        c_playlist = CollaborativePlaylist("test_cp", "Coll Playlist", u)
        
        p.add_playlist(playlist)
        p.add_playlist(c_playlist)
        
        result = p.avg_tracks_per_playlist_type()
        
        assert result == {
            "Playlist" : 0.0,
            "CollaborativePlaylist" : 0.0
        }
        
    def test_no_playlist(self, platform: StreamingPlatform) -> None:
        p = StreamingPlatform("No Playlist Platform")
        result = p.avg_tracks_per_playlist_type()
        
        assert result == {
            "Playlist" : 0.0,
            "CollaborativePlaylist" : 0.0
        }

# ===========================================================================
# Q10 - Users who completed at least one full album
# ===========================================================================

class TestUsersWhoCompletedAlbums:
    """Test the users_who_completed_albums() method.
    
    This method should:
    - Return users who have listened to every track on at least one album
    - Return (User, [album_titles]) tuples
    - Include all completed albums for each user
    - Ignore albums with no tracks
    """

    def test_returns_list_of_tuples(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a list of (User, list) tuples."""
        from streaming.users import User
        result = platform.users_who_completed_albums()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, tuple) and len(item) == 2
            assert isinstance(item[0], User) and isinstance(item[1], list)

    def test_completed_album_titles_are_strings(
        self, platform: StreamingPlatform
    ) -> None:
        """Verify all completed album titles are strings."""
        result = platform.users_who_completed_albums()
        for _, titles in result:
            assert all(isinstance(t, str) for t in titles)

    # TODO: Add tests that verify the correct users and albums are identified.
    def test_correct_users_identified(self, platform: StreamingPlatform) -> None:
        result = platform.users_who_completed_albums()
        
        expected_user_ids = {"u1", "u2", "u3", "u4", "u5", "u7"}
        not_expected = {"u6", "u8", "u9", "u10", "u11"}
        actual_user_ids = {i[0].user_id for i in result}
        
        assert expected_user_ids == actual_user_ids
        assert expected_user_ids.intersection(not_expected) == set()

    def test_correct_album_titles(self, platform: StreamingPlatform) -> None:
        result = platform.users_who_completed_albums()

        result_dict = {user.user_id : albums for user, albums in result}
                             # user_id     # albums  completed                       
        expected_completed = [("u1", {"Digital Dreams"}),
                              ("u2", {"Digital Hallucinacions"}),
                              ("u3", {"Digital Dreams"}),
                              ("u4", {"Analogue Dreams"}),
                              ("u5", {"Digital Hallucinacions"}),
                              ("u7", {"Digital Hallucinacions"})
                            ]
        
        for test in expected_completed:
            assert test[0] in result_dict
            assert test[1] == set(result_dict[test[0]])
            assert len(test[1]) == len(result_dict[test[0]])
            
    # __________ADDITIONAL____________
    
    def test_album_completion_different_scenarios(self, platform: StreamingPlatform) -> None:
        p = StreamingPlatform("Album Completion Testing Platform")
        
        artist = Artist("a1", "Test Artist", "pop")
        p.add_artist(artist)
        
        album1 = Album("alb1", "Album One", artist, 2023)
        album2 = Album("alb2", "Album Two", artist, 2023)
        
        track1 = AlbumTrack("t1", "Song 1", 180, "pop", artist, 1)
        track2 = AlbumTrack("t2", "Song 2", 200, "pop", artist, 2)
        track3 = AlbumTrack("t3", "Song 3", 240, "pop", artist, 1)
        track4 = AlbumTrack("t4", "Song 4", 220, "pop", artist, 2)
        
        for track in [track1, track2, track3, track4]:
            p.add_track(track)
            
        album1.add_track(track1)
        album1.add_track(track2)
        album2.add_track(track3)
        album2.add_track(track4)
        
        p.add_album(album1)
        p.add_album(album2)
        
        user1 = FreeUser("u1", "Complete All", 25)
        user2 = FreeUser("u2", "Complete One", 30)
        user3 = FreeUser("u3", "Complete None", 35)
    
        for user in [user1, user2, user3]:
            p.add_user(user)
            
        now = datetime.now()
        
        # User 1 - Both albums
        p.record_session(ListeningSession("s1", user1, track1, now, 180))
        p.record_session(ListeningSession("s2", user1, track2, now, 200))
        p.record_session(ListeningSession("s3", user1, track3, now, 240))
        p.record_session(ListeningSession("s4", user1, track4, now, 220))

        # User 2 - alb1 only
        p.record_session(ListeningSession("s5", user2, track1, now, 180))
        p.record_session(ListeningSession("s6", user2, track2, now, 200))

        # User 3 - one from each album but completes none
        p.record_session(ListeningSession("s7", user3, track1, now, 180))
        p.record_session(ListeningSession("s8", user3, track3, now, 240))
        
        result = p.users_who_completed_albums()
        result_dict = {user.user_id : albums for user, albums in result}
        
                             # user_id     # albums  completed                       
        expected_completed = [("u1", {"Album One", "Album Two"}),
                              ("u2", {"Album One"}),
                            ]
        
        for test in expected_completed:
            assert test[0] in result_dict
            assert test[1] == set(result_dict[test[0]])
            assert len(test[1]) == len(result_dict[test[0]])
        
        assert "u3" not in result_dict