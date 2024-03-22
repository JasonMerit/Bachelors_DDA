import torch as th
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback, ProgressBarCallback, EvalCallback
from stable_baselines3.common.evaluation import evaluate_policy
# monitor wrapper
from stable_baselines3.common.monitor import Monitor

import wandb
from wandb.integration.sb3 import WandbCallback
# https://docs.wandb.ai/guides/integrations/stable-baselines-3

from reinforcement_learning.environment import EndlessRunnerEnv, DumbEnv
from game.util import get_steps

def train(save_path: str, Env, total_timesteps, checkpoints: bool = True):
    total_timesteps = int(total_timesteps)
    print(f"Saving to [{save_path}] after [{total_timesteps}] timesteps")
    policy_kwargs = dict(activation_fn=th.nn.ReLU, net_arch=[4, 4])

    eval_callback = EvalCallback(
        Monitor(Env()), 
        eval_freq=total_timesteps//10, 
        verbose=1, 
        n_eval_episodes=1)
    
    checkpoint_callback = CheckpointCallback(
        save_freq=total_timesteps//10,
        save_path=save_path,
        name_prefix="",
        verbose=2
        )
    
    callbacks = [
        eval_callback, 
    ]
    
    if checkpoints:
        callbacks.append(checkpoint_callback)

    # Wandb 
    # config = dict(policy="MlpPolicy", 
    #                    total_timesteps=total_timesteps, 
    #                    seed=42, 
    #                    env="EndlessRunner")
    


    # run = wandb.init(project="dda", config=config)
    # wandb_callback = WandbCallback(
    #     gradient_save_freq=config["total_timesteps"]//10,  # Save every 10% of the total timesteps 
    #     model_save_path=save_path,
    #     verbose=2)

    # model = PPO(config["policy"], EndlessRunnerEnv(),
    #             policy_kwargs=policy_kwargs, seed=42)  # Seed for reproducibility
    # model.learn(total_timesteps=config["total_timesteps"], 
    #             callback=[wandb_callback, ProgressBarCallback()])

    model = PPO("MlpPolicy", Env(),
                policy_kwargs=policy_kwargs, seed=42)  # Seed for reproducibility
    print("Learning")
    model.learn(total_timesteps=total_timesteps, 
            callback=callbacks,
            progress_bar=True)
    print("Saving to", save_path)
    model.save(path=save_path)

    # Final eval
    mean, std = evaluate_policy( model, model.get_env(), n_eval_episodes=10)
    with open("logs.csv", "a") as f:
        f.write(f"{save_path}, d=1.0, {get_steps(total_timesteps)}, {mean}, {std}\n")
    # run.finish()
        

def get_save_path():
    from datetime import datetime
    name = datetime.now().strftime("%m_%d/PPO_%H_%M")
    return f"models/{name}"
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("timesteps", help="Order of magnitude of timesteps. default=4" , type=int, default=4)
    t = parser.parse_args().timesteps
    train(get_save_path(), EndlessRunnerEnv, 
          total_timesteps=10**t, checkpoints= t > 5)
    