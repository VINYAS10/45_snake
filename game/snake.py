import pygame


class Snake:
    def __init__(self, x, y, cell_size):
        self.cell_size = cell_size

        # body[0] is always the head.
        self.body = [
            (x, y),
            (x - 1, y),
            (x - 2, y)
        ]

        # Start by moving right.
        self.direction = (1, 0)

        # Used when food is eaten.
        self.grow_pending = False

    def set_direction(self, dx, dy):
        """
        Change the snake's direction.

        A snake cannot immediately reverse direction because
        that would cause the head to move directly into the
        segment behind it.
        """
        current_dx, current_dy = self.direction

        # Ignore a direct reversal.
        if (dx, dy) == (-current_dx, -current_dy):
            return

        self.direction = (dx, dy)

    def move(self):
        """Move the snake one grid cell."""
        head_x, head_y = self.body[0]
        dx, dy = self.direction

        new_head = (head_x + dx, head_y + dy)

        self.body.insert(0, new_head)

        if self.grow_pending:
            self.grow_pending = False
        else:
            self.body.pop()

    def grow(self):
        """Make the snake grow by one segment on its next move."""
        self.grow_pending = True

    def head_rect(self):
        """Return a pygame rectangle representing the head."""
        x, y = self.body[0]

        return pygame.Rect(
            x * self.cell_size,
            y * self.cell_size,
            self.cell_size,
            self.cell_size
        )

    def segment_rects(self):
        """Return rectangles for all snake segments."""
        return [
            pygame.Rect(
                x * self.cell_size,
                y * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            for (x, y) in self.body
        ]

    def collides_with_self(self):
        """Check whether the head overlaps another body segment."""
        head = self.body[0]
        return head in self.body[1:]

    def collides_with_wall(self, grid_width, grid_height):
        """Check whether the head has left the game grid."""
        x, y = self.body[0]

        return (
            x < 0
            or y < 0
            or x >= grid_width
            or y >= grid_height
        )