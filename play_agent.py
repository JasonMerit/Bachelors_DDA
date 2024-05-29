from game.controls import Controller
from reinforcement_learning.environment import EndlessRunnerEnv
from reinforcement_learning.agent import CheaterAgent

class PlayAgent():
    def __init__(self, d):
        self.env = EndlessRunnerEnv((d, 0), render=True, truncated=False)

        self.key_actions = {
            "quit": self.quit,
            "pause": self.pause, 
            "reset": self.env.reset,
            "increase_speed": Controller.increase_speed,
            "decrease_speed": Controller.decrease_speed,
            "increase_difficulty": self.increase_difficulty,
            "decrease_difficulty": self.decrease_difficulty,           
            "render": self.toggle_render
        }

        self.controller = Controller(self.key_actions)
        
        self.playing = True 
        self.paused = False
        
        
    
    def quit(self):
        self.playing = False
    
    def pause(self):
        self.paused = not self.paused
    
    def reset(self):
        self.env.reset()
    
    def toggle_render(self):
        self.env._render = not self.env._render

    def increase_difficulty(self):
        new_diff = (self.env.difficulty[0] + 1) % 11
        self.env.difficulty = new_diff, self.env.difficulty[1]
        self.env.game.set_difficulty((new_diff, self.env.difficulty[1]))

    def decrease_difficulty(self):
        new_diff = self.env.difficulty[0] - 1
        if new_diff < 0:
            new_diff = 10
        self.env.difficulty = new_diff, self.env.difficulty[1]
        self.env.game.set_difficulty((new_diff, self.env.difficulty[1]))
    
    def play(self):
        agent = CheaterAgent()
        obs, _ = self.env.reset(2)  # Seed for reproducibility
        
        while self.playing:
            # Pausing the game
            while self.paused:
                self.controller.handle_events()
            
            self.controller.handle_events()

            actions, states = agent.predict([obs])
            obs, reward, terminal, truncated, _ = self.env.step(actions[0])
            if terminal or truncated:
                print(f"You died! With a score of {self.env.game.player.cleared_platforms}")
                break
                # obs, _ = self.env.reset()
            if self.env.game.player.cleared_platforms > 1000:
                print("You win!")
                break
            if self.env.game.player.cleared_platforms == STOP:
                self.env._render = True

STOP = 119
if __name__ == "__main__":
    play_agent = PlayAgent(10)
    if STOP:
        play_agent.toggle_render()
    play_agent.play()

# 4