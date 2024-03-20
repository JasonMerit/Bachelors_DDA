from datetime import datetime
now = datetime.now()
name = now.strftime("%m_%d/PPO_%H_%M")
save_path = f"Bachelors_DDA/models/{name}"
print("Save path:", save_path)

from ai.environment import EndlessRunnerEnv
from stable_baselines3 import PPO
env = EndlessRunnerEnv()
import torch as th


# # Custom nn
policy_kwargs = dict(activation_fn=th.nn.ReLU, net_arch=[4, 4])
model = PPO("MlpPolicy", env, policy_kwargs=policy_kwargs)

# # from stable_baselines3.common.env_util import make_vec_env

# # Instantiate the env
# # vec_env = EndlessRunnerEnv



# # # TRAINING
# model = PPO("MlpPolicy", env)
from stable_baselines3.common.callbacks import CheckpointCallback
checkpoint_callback = CheckpointCallback(save_freq=1e5, save_path=save_path, name_prefix="")
model.learn(total_timesteps=1e6, callback=[checkpoint_callback])
model.save(path=save_path)

# # LOADING and PLAYING
model = PPO.load("Bachelors_DDA/models/03_19/PPO_18_04.zip", env=env)
print("Loaded model")

# env.set_render(True)
# # Test the trained agent
# # using the vecenv
# obs, _ = env.reset()
# n_steps = 20000
# for step in range(n_steps):
#     action, _ = model.predict(obs, deterministic=True)
#     # print(f"Step {step + 1}")
#     # print("Action: ", action)
#     obs, reward, terminated, truncated, info = env.step(action)
#     done = terminated or truncated
#     # print("obs=", obs, "reward=", reward, "done=", done)
#     env.render()
#     if done:
#         # Note that the VecEnv resets automatically
#         # when a done signal is encountered
#         # print("Goal reached!", "reward=", reward)
#         obs, _ = env.reset()
        
