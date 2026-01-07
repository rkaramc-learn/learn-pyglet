"""Tests for the game state machine."""

import unittest

from pyglet_readme.game_state import GameState, GameStateManager


class TestGameState(unittest.TestCase):
    """Test the GameState enum."""

    def test_game_state_values(self) -> None:
        """Test that GameState has all required values."""
        self.assertEqual(GameState.PLAYING.name, "PLAYING")
        self.assertEqual(GameState.PAUSED.name, "PAUSED")
        self.assertEqual(GameState.GAME_OVER_WIN.name, "GAME_OVER_WIN")
        self.assertEqual(GameState.GAME_OVER_LOSE.name, "GAME_OVER_LOSE")

    def test_game_state_uniqueness(self) -> None:
        """Test that GameState values are unique."""
        states = [
            GameState.PLAYING,
            GameState.PAUSED,
            GameState.GAME_OVER_WIN,
            GameState.GAME_OVER_LOSE,
        ]
        self.assertEqual(len(states), len(set(states)))


class TestGameStateManager(unittest.TestCase):
    """Test the GameStateManager class."""

    def test_state_manager_initial_state(self) -> None:
        """Test that GameStateManager starts in PLAYING state."""
        manager = GameStateManager()
        self.assertEqual(manager.state, GameState.PLAYING)

    def test_set_state(self) -> None:
        """Test setting a new state."""
        manager = GameStateManager()
        manager.set_state(GameState.GAME_OVER_WIN)
        self.assertEqual(manager.state, GameState.GAME_OVER_WIN)

    def test_is_playing_true(self) -> None:
        """Test is_playing returns True when in PLAYING state."""
        manager = GameStateManager()
        self.assertTrue(manager.is_playing())

    def test_is_playing_false(self) -> None:
        """Test is_playing returns False when not in PLAYING state."""
        manager = GameStateManager()
        manager.set_state(GameState.GAME_OVER_WIN)
        self.assertFalse(manager.is_playing())

    def test_is_game_over_false_when_playing(self) -> None:
        """Test is_game_over returns False when playing."""
        manager = GameStateManager()
        self.assertFalse(manager.is_game_over())

    def test_is_game_over_true_on_win(self) -> None:
        """Test is_game_over returns True on win."""
        manager = GameStateManager()
        manager.set_state(GameState.GAME_OVER_WIN)
        self.assertTrue(manager.is_game_over())

    def test_is_game_over_true_on_lose(self) -> None:
        """Test is_game_over returns True on lose."""
        manager = GameStateManager()
        manager.set_state(GameState.GAME_OVER_LOSE)
        self.assertTrue(manager.is_game_over())

    def test_is_game_over_false_when_paused(self) -> None:
        """Test is_game_over returns False when paused."""
        manager = GameStateManager()
        manager.set_state(GameState.PAUSED)
        self.assertFalse(manager.is_game_over())

    def test_is_player_won_true(self) -> None:
        """Test is_player_won returns True on win state."""
        manager = GameStateManager()
        manager.set_state(GameState.GAME_OVER_WIN)
        self.assertTrue(manager.is_player_won())

    def test_is_player_won_false_on_lose(self) -> None:
        """Test is_player_won returns False on lose state."""
        manager = GameStateManager()
        manager.set_state(GameState.GAME_OVER_LOSE)
        self.assertFalse(manager.is_player_won())

    def test_is_player_won_false_when_playing(self) -> None:
        """Test is_player_won returns False when playing."""
        manager = GameStateManager()
        self.assertFalse(manager.is_player_won())

    def test_is_player_lost_true(self) -> None:
        """Test is_player_lost returns True on lose state."""
        manager = GameStateManager()
        manager.set_state(GameState.GAME_OVER_LOSE)
        self.assertTrue(manager.is_player_lost())

    def test_is_player_lost_false_on_win(self) -> None:
        """Test is_player_lost returns False on win state."""
        manager = GameStateManager()
        manager.set_state(GameState.GAME_OVER_WIN)
        self.assertFalse(manager.is_player_lost())

    def test_is_player_lost_false_when_playing(self) -> None:
        """Test is_player_lost returns False when playing."""
        manager = GameStateManager()
        self.assertFalse(manager.is_player_lost())

    def test_win_transition(self) -> None:
        """Test win() method transitions to GAME_OVER_WIN."""
        manager = GameStateManager()
        manager.win()
        self.assertEqual(manager.state, GameState.GAME_OVER_WIN)
        self.assertTrue(manager.is_player_won())

    def test_lose_transition(self) -> None:
        """Test lose() method transitions to GAME_OVER_LOSE."""
        manager = GameStateManager()
        manager.lose()
        self.assertEqual(manager.state, GameState.GAME_OVER_LOSE)
        self.assertTrue(manager.is_player_lost())

    def test_reset(self) -> None:
        """Test reset() method returns to PLAYING state."""
        manager = GameStateManager()
        manager.win()
        self.assertTrue(manager.is_game_over())
        
        manager.reset()
        self.assertEqual(manager.state, GameState.PLAYING)
        self.assertTrue(manager.is_playing())

    def test_state_transitions_sequence(self) -> None:
        """Test a sequence of state transitions."""
        manager = GameStateManager()
        
        # Start playing
        self.assertTrue(manager.is_playing())
        self.assertFalse(manager.is_game_over())
        
        # Win
        manager.win()
        self.assertFalse(manager.is_playing())
        self.assertTrue(manager.is_game_over())
        self.assertTrue(manager.is_player_won())
        
        # Reset to playing
        manager.reset()
        self.assertTrue(manager.is_playing())
        self.assertFalse(manager.is_game_over())
        
        # Lose
        manager.lose()
        self.assertFalse(manager.is_playing())
        self.assertTrue(manager.is_game_over())
        self.assertTrue(manager.is_player_lost())

    def test_multiple_state_changes(self) -> None:
        """Test multiple rapid state changes."""
        manager = GameStateManager()
        
        manager.set_state(GameState.PAUSED)
        self.assertEqual(manager.state, GameState.PAUSED)
        
        manager.set_state(GameState.PLAYING)
        self.assertEqual(manager.state, GameState.PLAYING)
        
        manager.win()
        self.assertEqual(manager.state, GameState.GAME_OVER_WIN)
        
        manager.reset()
        self.assertEqual(manager.state, GameState.PLAYING)


if __name__ == "__main__":
    unittest.main()
