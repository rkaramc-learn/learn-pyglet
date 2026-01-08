"""Game state machine and state transitions."""

from enum import Enum, auto


class GameState(Enum):
    """Enumeration of all possible game states."""

    PLAYING = auto()  # Game is actively running
    PAUSED = auto()  # Game is paused (not yet implemented)
    GAME_OVER_WIN = auto()  # Player won (kitten exhausted)
    GAME_OVER_LOSE = auto()  # Player lost (mouse health reached 0)


class GameStateManager:
    """Manages game state transitions and state-related logic.

    Provides a clean interface for state queries and transitions.
    """

    def __init__(self) -> None:
        """Initialize game state to PLAYING."""
        self.state = GameState.PLAYING

    def set_state(self, new_state: GameState) -> None:
        """Transition to a new game state.

        Args:
            new_state: The target game state.
        """
        self.state = new_state

    def is_playing(self) -> bool:
        """Check if game is currently playing.

        Returns:
            True if state is PLAYING, False otherwise.
        """
        return self.state == GameState.PLAYING

    def is_game_over(self) -> bool:
        """Check if game is in an end state (win or lose).

        Returns:
            True if state is GAME_OVER_WIN or GAME_OVER_LOSE, False otherwise.
        """
        return self.state in (GameState.GAME_OVER_WIN, GameState.GAME_OVER_LOSE)

    def is_player_won(self) -> bool:
        """Check if player has won.

        Returns:
            True if state is GAME_OVER_WIN, False otherwise.
        """
        return self.state == GameState.GAME_OVER_WIN

    def is_player_lost(self) -> bool:
        """Check if player has lost.

        Returns:
            True if state is GAME_OVER_LOSE, False otherwise.
        """
        return self.state == GameState.GAME_OVER_LOSE

    def win(self) -> None:
        """Transition to win state."""
        self.state = GameState.GAME_OVER_WIN

    def lose(self) -> None:
        """Transition to lose state."""
        self.state = GameState.GAME_OVER_LOSE

    def reset(self) -> None:
        """Reset game to PLAYING state."""
        self.state = GameState.PLAYING
