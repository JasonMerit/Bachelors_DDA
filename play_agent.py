from game.controls import Controller
from reinforcement_learning.environment import EndlessRunnerEnv
from reinforcement_learning.agent import CheaterAgent

class PlayAgent():
    def __init__(self):
        self.env = EndlessRunnerEnv(render=True)

        self.key_actions = {
            "quit": self.quit,
            "pause": self.pause, 
            "reset": self.env.reset,
            "increase_speed": Controller.increase_speed,
            "decrease_speed": Controller.decrease_speed
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
 
    def play(self):
        agent = CheaterAgent()
        state, _ = self.env.reset(42)  # Seed for reproducibility


        while self.playing:
            # Pausing the game
            while self.paused:
                self.controller.handle_events()
            
            self.controller.handle_events()

            action = agent.predict(state)
            # action = env.action_space.sample()
            state, reward, terminal, truncated, _ = self.env.step(action)
            if terminal or truncated:
                # self.env.render()
                # self.pause()
                # while self.paused:
                #     self.controller.handle_events()
                state, _ = self.env.reset()
            self.env.render(state)


if __name__ == "__main__":
    play_agent = PlayAgent()
    play_agent.play()