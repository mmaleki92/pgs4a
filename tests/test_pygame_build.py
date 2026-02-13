"""
Test pygame functionality - validates that pygame can initialize,
create a display, render shapes/text, and capture output.
This serves as a build validation test for the pygame integration.
"""

import os
import sys
import unittest

try:
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    os.environ['SDL_AUDIODRIVER'] = 'dummy'
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


@unittest.skipUnless(PYGAME_AVAILABLE, "pygame not installed")
class TestPygameInit(unittest.TestCase):
    """Test that pygame initializes correctly."""

    def setUp(self):
        pygame.init()

    def tearDown(self):
        pygame.quit()

    def test_pygame_init(self):
        """Test pygame initializes without errors."""
        num_passed, num_failed = pygame.init()
        self.assertGreater(num_passed, 0)

    def test_pygame_version(self):
        """Test pygame version is modern (2.x+)."""
        version = pygame.version.ver
        major = int(version.split('.')[0])
        self.assertGreaterEqual(major, 2, f"Expected pygame 2.x+, got {version}")

    def test_create_surface(self):
        """Test creating a pygame surface."""
        surface = pygame.Surface((100, 100))
        self.assertIsNotNone(surface)
        self.assertEqual(surface.get_size(), (100, 100))

    def test_surface_fill(self):
        """Test filling a surface with color."""
        surface = pygame.Surface((100, 100))
        surface.fill((255, 0, 0))
        color = surface.get_at((50, 50))
        self.assertEqual(color[:3], (255, 0, 0))

    def test_draw_rect(self):
        """Test drawing a rectangle on surface."""
        surface = pygame.Surface((200, 200))
        surface.fill((0, 0, 0))
        pygame.draw.rect(surface, (0, 255, 0), (10, 10, 50, 50))
        # Check pixel inside the rectangle
        color = surface.get_at((30, 30))
        self.assertEqual(color[:3], (0, 255, 0))
        # Check pixel outside the rectangle
        color = surface.get_at((100, 100))
        self.assertEqual(color[:3], (0, 0, 0))

    def test_draw_circle(self):
        """Test drawing a circle on surface."""
        surface = pygame.Surface((200, 200))
        surface.fill((0, 0, 0))
        pygame.draw.circle(surface, (0, 0, 255), (100, 100), 50)
        # Center should be blue
        color = surface.get_at((100, 100))
        self.assertEqual(color[:3], (0, 0, 255))

    def test_font_render(self):
        """Test rendering text with default font."""
        font = pygame.font.Font(None, 24)
        text_surface = font.render("Hello Pygame", True, (255, 255, 255))
        self.assertIsNotNone(text_surface)
        self.assertGreater(text_surface.get_width(), 0)
        self.assertGreater(text_surface.get_height(), 0)

    def test_surface_blit(self):
        """Test blitting one surface onto another."""
        dest = pygame.Surface((200, 200))
        dest.fill((0, 0, 0))
        src = pygame.Surface((50, 50))
        src.fill((255, 255, 0))
        dest.blit(src, (10, 10))
        # Check blitted area
        color = dest.get_at((30, 30))
        self.assertEqual(color[:3], (255, 255, 0))
        # Check non-blitted area
        color = dest.get_at((100, 100))
        self.assertEqual(color[:3], (0, 0, 0))

    def test_event_system(self):
        """Test that the event system works."""
        # Post a custom event and retrieve it
        custom_event = pygame.event.Event(pygame.USEREVENT, {"data": "test"})
        pygame.event.post(custom_event)
        events = pygame.event.get(pygame.USEREVENT)
        self.assertTrue(len(events) > 0)
        self.assertEqual(events[0].data, "test")

    def test_clock(self):
        """Test that Clock works."""
        clock = pygame.time.Clock()
        clock.tick(60)
        fps = clock.get_fps()
        # First tick won't have meaningful FPS, just ensure no error
        self.assertIsInstance(fps, float)

    def test_surface_convert(self):
        """Test surface format conversion."""
        screen = pygame.Surface((100, 100))
        surface = pygame.Surface((50, 50))
        converted = surface.convert(screen)
        self.assertEqual(converted.get_size(), (50, 50))

    def test_rect_operations(self):
        """Test pygame Rect operations."""
        rect1 = pygame.Rect(0, 0, 100, 100)
        rect2 = pygame.Rect(50, 50, 100, 100)
        self.assertTrue(rect1.colliderect(rect2))
        
        rect3 = pygame.Rect(200, 200, 50, 50)
        self.assertFalse(rect1.colliderect(rect3))

    def test_display_set_mode(self):
        """Test creating a display surface."""
        screen = pygame.display.set_mode((320, 240))
        self.assertIsNotNone(screen)
        self.assertEqual(screen.get_size(), (320, 240))

    def test_display_update(self):
        """Test display update doesn't crash."""
        screen = pygame.display.set_mode((320, 240))
        screen.fill((100, 100, 100))
        pygame.display.flip()


@unittest.skipUnless(PYGAME_AVAILABLE, "pygame not installed")
class TestPygameGameLoop(unittest.TestCase):
    """Test a minimal game loop similar to what pgs4a would build."""

    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((320, 240))

    def tearDown(self):
        pygame.quit()

    def test_simple_game_loop(self):
        """Test running a simple game loop for a few frames."""
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 24)

        for frame in range(10):
            # Handle events
            for event in pygame.event.get():
                pass

            # Update
            clock.tick(60)

            # Render
            self.screen.fill((0, 0, 50))
            text = font.render(f"Frame {frame}", True, (255, 255, 0))
            self.screen.blit(text, (10, 10))
            pygame.draw.rect(self.screen, (255, 0, 0), (50, 50, 100, 100), 2)
            pygame.display.flip()

        # If we get here without crashing, the test passes

    def test_sprite_creation(self):
        """Test creating and using a simple sprite."""
        class SimpleSprite(pygame.sprite.Sprite):
            def __init__(self):
                super().__init__()
                self.image = pygame.Surface((32, 32))
                self.image.fill((255, 0, 0))
                self.rect = self.image.get_rect()
                self.rect.x = 100
                self.rect.y = 100

            def update(self):
                self.rect.x += 1

        sprite = SimpleSprite()
        group = pygame.sprite.Group(sprite)

        for _ in range(5):
            group.update()
            group.draw(self.screen)

        self.assertEqual(sprite.rect.x, 105)


if __name__ == "__main__":
    unittest.main()
