from threading import Lock
import pygame

from models.fighter import Fighter

NOMINAL_FPS = 60.0

class Display:

    def init(self):
        pygame.init()
        self._clock = pygame.Clock()

        # Get current display resolution
        info = pygame.display.Info()
        screen_width, screen_height = info.current_w, info.current_h

        # Create a borderless window that fills the screen
        self._screen = pygame.display.set_mode(
            (screen_width, screen_height),
            pygame.NOFRAME  # removes window borders
        )

        pygame.display.set_caption(f"Battlestar NonGalactica: fps={self._clock.get_fps()}")

        self._fighter_lock = Lock()
        self._fighters = set[Fighter]()

        self._running = True
        print("(display) initialised")

    def stop(self):
        self._running = False
        pygame.quit()
        print("(display) stopped")

    def render(self):
        pygame.display.flip()
        self._clock.tick(NOMINAL_FPS)

    def draw(self):
        self._screen.fill((0, 0, 0))

        for fighter in self.fighters:
            self.draw_fighter(fighter)
    
    def add_fighter(self, fighter: Fighter):
        with self._fighter_lock:
            self._fighters.add(fighter)

    def remove_fighter(self, fighter: Fighter):
        with self._fighter_lock:
            self._fighters.remove(fighter)

    @property
    def fighters(self):
        with self._fighter_lock:
            return set(self._fighters)

    def draw_fighter(self, fighter: Fighter):
        pygame.draw.circle(
            surface = self._screen,
            color   = fighter.color,
            center  = fighter.coords,
            radius  = fighter.radius,
            width   = fighter.thiccness
        )

        x,y = fighter.coords
        arc_radius = fighter.radius + 10
        
        arc_rect = (
            int(x - arc_radius),
            int(y - arc_radius),
            int(arc_radius * 2),
            int(arc_radius * 2)
        )

        pygame.draw.arc(
            surface     = self._screen,
            color       = fighter.color,
            rect        = arc_rect,
            start_angle = fighter.angle - 10,
            stop_angle  = fighter.angle + 10,
            width       = fighter.thiccness
        )
    