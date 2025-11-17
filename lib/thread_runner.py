from abc import ABC, abstractmethod

import threading
import time

class ThreadRunner(ABC):

    def __init__(self, name: str, daemon: bool, sleep: float, **kwargs):
        self._alive: bool = None
        self.name = name
        self.daemon = daemon
        self.sleep = sleep

        self.handle = threading.Thread(
            target = self._run_loop,
            name   = name,
            daemon = daemon
        )

        # For chaining MRO
        super().__init__(**kwargs)

    def start(self):
        self.handle.start()

    def _run_loop(self):

        print(f"{self.name}: Started thread '{self.name}'")

        self._alive = True

        while self._alive == True:
            self.loop()
            time.sleep(self.sleep)

        print(f"{self.name}: Finished thread '{self.name}'")

    def stop(self, blocking: bool):
        self._alive = False
        if self.daemon:
            return
        if blocking:
            self.handle.join()
        
    @abstractmethod
    def loop(self): ...

    def is_alive(self) -> bool:
        return self._alive