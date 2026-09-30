import pygame

from .snake import Snake
from .food import Food


# Colors
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 60, 60)
DARK_GREEN = (0, 140, 0)
GRAY = (40, 40, 40)


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.cell_size = 20
        self.grid_width = width // self.cell_size
        self.grid_height = height // self.cell_size

        self.font = pygame.font.SysFont("Arial", 30)
        self.title_font = pygame.font.SysFont("Arial", 50)
        self.small_font = pygame.font.SysFont("Arial", 24)

        # Difficulty speeds
        self.difficulties = {
            "Easy": 5,
            "Medium": 8,
            "Hard": 12
        }

        self.difficulty_names = ["Easy", "Medium", "Hard"]
        self.selected_difficulty = 1

        self.moves_per_second = self.difficulties["Medium"]

        self.snake = None
        self.food = None

        self.score = 0
        self._frame_counter = 0

        self.game_over = False
        self.show_menu = False

        # Sound setup
        self.sound_enabled = False
        self.eat_sound = None
        self.game_over_sound = None

        self._initialize_sounds()
        self.reset_game()

    def _initialize_sounds(self):
        """
        Initialize basic sound effects.

        If the system cannot initialize audio, the game continues
        without sound rather than crashing.
        """
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            self.eat_sound = self._create_beep(700, 100)
            self.game_over_sound = self._create_beep(200, 300)

            self.sound_enabled = (
                self.eat_sound is not None
                and self.game_over_sound is not None
            )

        except pygame.error:
            self.sound_enabled = False

    def _create_beep(self, frequency, duration_ms):
        """
        Create a simple generated beep.

        This avoids requiring external .wav files.
        """
        try:
            sample_rate = 44100
            sample_count = int(sample_rate * duration_ms / 1000)

            sound_buffer = bytearray()

            for i in range(sample_count):
                # Simple square wave
                period = sample_rate / frequency
                value = 180 if (i % period) < period / 2 else -180

                sound_buffer.append(value + 128)

            return pygame.mixer.Sound(buffer=bytes(sound_buffer))

        except (pygame.error, ValueError):
            return None

    def reset_game(self):
        """Start a fresh game using the selected difficulty."""

        self.moves_per_second = self.difficulties[
            self.difficulty_names[self.selected_difficulty]
        ]

        self.snake = Snake(
            self.grid_width // 2,
            self.grid_height // 2,
            self.cell_size
        )

        self.food = Food(
            self.grid_width,
            self.grid_height,
            self.cell_size
        )

        self.score = 0
        self._frame_counter = 0

        self.game_over = False
        self.show_menu = False

    def handle_keydown(self, key):
        """Handle keyboard input."""

        # Game-over menu
        if self.game_over:
            if key in (pygame.K_r, pygame.K_RETURN):
                self.reset_game()
                return

            if key == pygame.K_1:
                self.selected_difficulty = 0
                self.reset_game()
                return

            if key == pygame.K_2:
                self.selected_difficulty = 1
                self.reset_game()
                return

            if key == pygame.K_3:
                self.selected_difficulty = 2
                self.reset_game()
                return

            return

        # Normal gameplay controls
        if key in (pygame.K_UP, pygame.K_w):
            self.snake.set_direction(0, -1)

        elif key in (pygame.K_DOWN, pygame.K_s):
            self.snake.set_direction(0, 1)

        elif key in (pygame.K_LEFT, pygame.K_a):
            self.snake.set_direction(-1, 0)

        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.snake.set_direction(1, 0)

    def handle_input(self):
        """
        Reserved for continuously-held-key input.

        Snake direction changes are handled by KEYDOWN events.
        """
        pass

    def update(self):
        """Update the game state."""

        if self.game_over:
            return

        self._frame_counter += 1

        frames_per_move = max(
            1,
            60 // self.moves_per_second
        )

        if self._frame_counter < frames_per_move:
            return

        self._frame_counter = 0

        # Move snake
        self.snake.move()

        # Wall collision
        if self.snake.collides_with_wall(
            self.grid_width,
            self.grid_height
        ):
            self._trigger_game_over()
            return

        # Self collision
        if self.snake.collides_with_self():
            self._trigger_game_over()
            return

        # Food collision
        if self.snake.head_rect().colliderect(
            self.food.rect()
        ):
            self.snake.grow()
            self.score += 1

            self.food.respawn(self.snake.body)

            self._play_sound(self.eat_sound)

    def _trigger_game_over(self):
        """Handle game-over state."""

        self.game_over = True

        self._play_sound(self.game_over_sound)

    def _play_sound(self, sound):
        """Play a sound safely."""

        if not self.sound_enabled:
            return

        if sound is None:
            return

        try:
            sound.play()
        except pygame.error:
            pass

    def render(self, screen):
        """Draw the game."""

        # Background
        screen.fill((0, 0, 0))

        # Food
        pygame.draw.rect(
            screen,
            RED,
            self.food.rect()
        )

        # Snake
        for index, rect in enumerate(
            self.snake.segment_rects()
        ):
            if index == 0:
                pygame.draw.rect(
                    screen,
                    DARK_GREEN,
                    rect
                )
            else:
                pygame.draw.rect(
                    screen,
                    GREEN,
                    rect
                )

        # Score
        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            WHITE
        )

        screen.blit(
            score_text,
            (10, 10)
        )

        # Difficulty
        difficulty_text = self.small_font.render(
            f"Difficulty: "
            f"{self.difficulty_names[self.selected_difficulty]}",
            True,
            WHITE
        )

        screen.blit(
            difficulty_text,
            (10, 45)
        )

        # Game-over screen
        if self.game_over:
            self._render_game_over(screen)

    def _render_game_over(self, screen):
        """Draw the game-over screen."""

        overlay = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))

        game_over_text = self.title_font.render(
            "GAME OVER",
            True,
            WHITE
        )

        final_score_text = self.font.render(
            f"Final Score: {self.score}",
            True,
            WHITE
        )

        restart_text = self.small_font.render(
            "Press R or ENTER to replay",
            True,
            WHITE
        )

        difficulty_text = self.small_font.render(
            "Press 1 = Easy   2 = Medium   3 = Hard",
            True,
            WHITE
        )

        exit_text = self.small_font.render(
            "Close the window to exit",
            True,
            WHITE
        )

        game_over_rect = game_over_text.get_rect(
            center=(self.width // 2, 200)
        )

        final_score_rect = final_score_text.get_rect(
            center=(self.width // 2, 270)
        )

        restart_rect = restart_text.get_rect(
            center=(self.width // 2, 340)
        )

        difficulty_rect = difficulty_text.get_rect(
            center=(self.width // 2, 390)
        )

        exit_rect = exit_text.get_rect(
            center=(self.width // 2, 440)
        )

        screen.blit(
            game_over_text,
            game_over_rect
        )

        screen.blit(
            final_score_text,
            final_score_rect
        )

        screen.blit(
            restart_text,
            restart_rect
        )

        screen.blit(
            difficulty_text,
            difficulty_rect
        )

        screen.blit(
            exit_text,
            exit_rect
        )