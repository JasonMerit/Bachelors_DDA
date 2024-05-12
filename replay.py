import pickle

from game.display import Display

# with open('deaths.pkl', 'rb') as f:
#     deaths = pickle.load(f)

# for d in deaths:
# Display.play_recordings(deaths)



from reinforcement_learning.agent import CheaterAgent
from reinforcement_learning.environment import EndlessRunnerEnv

def main():
    env = EndlessRunnerEnv(render=True, truncated=False)
    agent = CheaterAgent()
    game_master = env.game.game_master

    with open('deaths.pkl', 'rb') as f:
        death_states = pickle.load(f)

    random_state, player_state = death_states
    game_master.set_state(random_state)
    obs, _ = env.reset()  # Seed for reproducibility
    player = env.game.player
    player.y, player.speed = player_state
    if player.speed != 0:
        player.is_falling = True

    
    while True:
        # Pausing the game
        actions, states = agent.predict([obs])
        # action = env.action_space.sample()
        obs, reward, terminal, truncated, _ = env.step(actions[0])
        if terminal or truncated:
            break
        env.render(obs)
    # print(random_states)
    # for state in random_states:
        # game.game_master.set_state(state)
        # clock.tick(fps)


if __name__ == "__main__":
    main()