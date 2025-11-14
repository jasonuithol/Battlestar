from threading import Lock
import pygame

from models.fighter import Fighter

NOMINAL_FPS = 60.0

class Display:

    def __init__(self):
        self._fighter_lock = Lock()
        self._fighters = set[Fighter]()

    def init(self):
        pygame.init()
        self._clock = pygame.Clock()

        # Create a borderless window that fills the screen
        info = pygame.display.Info()
        self._screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME)

        self.update_window_title()

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

        self.update_window_title()

        self._screen.fill((0, 0, 0))

        for fighter in self.fighters:
            self.draw_fighter(fighter)
    
    def add_fighter(self, fighter: Fighter):
        with self._fighter_lock:
            self._fighters.add(fighter)
            num_fighters = len(self._fighters)

        print(f"(display) added fighter {num_fighters}")

    def remove_fighter(self, fighter: Fighter):
        with self._fighter_lock:
            self._fighters.remove(fighter)

    def num_fighters(self) -> int:
        with self._fighter_lock:
            return len(self._fighters)

    @property
    def fighters(self):
        with self._fighter_lock:
            return set(self._fighters)

    def draw_fighter(self, fighter: Fighter):

        fighter.calculate()

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
            start_angle = fighter.angle - 0.1,
            stop_angle  = fighter.angle + 0.1,
            width       = fighter.thiccness
        )

    def update_window_title(self):
        pygame.display.set_caption(f"Battlestar NonGalactica: players={self.num_fighters()} fps={self._clock.get_fps()}")

    