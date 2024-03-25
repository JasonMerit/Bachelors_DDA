
import numpy as np
path = "models/03_25/PPO_08_27/evaluations.npz"
data = np.load(path)
print(data.files)
print(data["timesteps"])
print(data["results"])
print(data["ep_lengths"])
print(data["timesteps"].shape)
print(data["results"].shape)
print(data["ep_lengths"].shape)

print(data)
