import time
from collections import deque
import pickle

from reinforcement_learning.environment import EndlessRunnerEnv
from reinforcement_learning.agent import CheaterAgent

def play():
    env = EndlessRunnerEnv(render=False, truncated=False)
    agent = CheaterAgent()
    obs, _ = env.reset(42)  # Seed for reproducibility
    history = deque(maxlen=10)

    _x1, _dx, _dy = 100, 100, 100
    x1_, dx_, dy_ = 0, 0, 0
    # with open('stats.pkl', 'wb') as f:
    # with open('deaths.csv', 'w') as f:
    with open('deaths.pkl', 'wb') as f:
    # with open('daemons.txt', 'w') as f:
        # run loop for 10 seconds
        timeout = 10#40 * 60
        t0 = time.time()
        while True:
        # for _ in range(100):
            actions, states = agent.predict([obs])
            # action = env.action_space.sample()
            obs, reward, terminal, truncated, _ = env.step(actions[0])
            x1, dx, dy = obs
            _x1 = min(_x1, x1)
            _dx = min(_dx, dx)
            _dy = min(_dy, dy)
            x1_ = max(x1_, x1)
            dx_ = max(dx_, dx)
            dy_ = max(dy_, dy)
            # print(type(r_state))
            # quit()
            r_state = env.get_random_state()[1]
            p_state = env.get_player_state()
            history.append((r_state, p_state))
            if terminal or truncated:
                # deaths.append(env.game.history.copy())
                obs, _ = env.reset()
                # pickle.dump(history.copy(), f)
                # write last element in history
                # f.write(f'{r_state}')
                pickle.dump(history[0], f)
                break
            env.render(obs)

            if time.time() - t0 > timeout:
                break

    # print(f'x0 in [{_x1}, {x1_}]\ndx in [{_dx}, {dx_}]\ndy in [{_dy}, {dy_}]')

# x0 in [0.0, 325.0]
# dx in [45.0, 209.0]
# dy in [-399.0, 205.0]
import pickle
if __name__ == "__main__":
    play()