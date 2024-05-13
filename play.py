from game.controls import Controller
from game.display import Display

class EndlessRunnerApp():
    def __init__(self, difficulty):
        self.game = Display()
        self.game.set_difficulty((difficulty, 0))
        

        self.key_actions = {
            "quit": self.quit, 
            "jump": self.game.jump,
            "jump_release": self.game.jump_release,
            "pause": self.pause, 
            "reset": self.game.reset,
            "increase_speed": Controller.increase_speed,
            "decrease_speed": Controller.decrease_speed,
            "increase_difficulty": self.increase_difficulty,
            "decrease_difficulty": self.decrease_difficulty
        }

        self.controller = Controller(self.key_actions)
        
        self.playing = True
        self.paused = False
    
    def quit(self):
        self.playing = False

    def pause(self):
        self.paused = not self.paused

    def increase_difficulty(self):
        new_diff = (self.game.difficulty[0] + 1) % 11
        self.game.set_difficulty((new_diff, self.game.difficulty[1]))

    def decrease_difficulty(self):
        new_diff = (self.game.difficulty[0] - 1)
        if new_diff < 0:
            new_diff = 10
        self.game.set_difficulty((new_diff, self.game.difficulty[1]))
    
    def play(self):
        self.game.reset()  # Seed for reproducibility
        # self.game.reset(seed=2)  # Seed for reproducibility
        
        while self.playing:
            # Pausing the game
            while self.paused:
                self.controller.handle_events()

            self.controller.handle_events()

            if self.game.tick() is True:
                self.game.reset()
            
            
            self.game.render()
        
        # history = self.game.history
        # Display.play_recording(history)


if __name__ == "__main__":
    app = EndlessRunnerApp(6)
    app.play()