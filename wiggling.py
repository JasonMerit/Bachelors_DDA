import matplotlib.pyplot as plt
import numpy as np

from tqdm import tqdm
from scipy.optimize import minimize
from scipy.interpolate import interpn, interp1d

from model_config import checkpoint_folder, all_players, players
# all_players = all_players[60:70]  # TODO: remove this line

discrete = np.arange(1, 11)
continuous = np.linspace(1, 10, 100)


def interpolate(data, res=100):
    """Smoothe out the difficulty matrix using cubic interpolation."""
    smooth = np.linspace(1, 10, res)
    coords = np.array(np.meshgrid(smooth, smooth)).T.reshape(-1, 2)
    return interpn((discrete, discrete), data, coords, "cubic").reshape(res, -1)
    
# def _get_x(Y, target) -> np.ndarray:
#     """Returns distinct x values that intersect with target."""
#     f = interp1d(continuous, Y, kind='cubic')
#     objective = lambda x: (f(x) - target)**2
    
#     solutions = set()
#     for x0 in range(1, 11):
#         x = minimize(objective, x0, bounds=[(1, 10)]).x[0]
#         if np.isclose(f(x), target):
#             solutions.add(np.round(float(x), 2))

#     return np.array(sorted(list(solutions)))

def get_x(Y, target):
    crossings = np.where(np.diff(np.sign(Y - target)))[0]

    # Interpolate 
    x_intersections = []
    for c in crossings:
        x0, x1 = continuous[c : c + 2]
        y0, y1 = Y[c : c + 2]
        x_intersections.append(x0 + (target - y0) * (x1 - x0) / (y1 - y0))

    return np.array(x_intersections)

def get_intersection_spread(Ys, target) -> float:
    """Returns spread of x values intersecting with target.
    or 0 if no intersection is found.
    """
    intersections = [get_x(Y, target) for Y in Ys]
    # filter out empty arrays and take mean
    means = [a.mean() for a in intersections if a.size > 0]
    return np.std(means) if means else 0

def get_spreads(targets, performances):
    """Returns std of x values intersecting with target across all players.
    Only includes targets with non-zero spread.
    Zero when no intersection is found for any player or 
    very unlikely all players have the same intersection point."""
    
    spreads = [(target, get_intersection_spread(performances, target)) for target in targets]
    return [(m, s) for m, s in spreads if s > 0]

def eval_line(datas, line, targets):
    performances = [interpn((discrete, discrete), d, line, "cubic") for d in datas]
    spreads = get_spreads(targets, performances)  # (t, std) pairs
    if len(spreads) == 0:
        return 0, 0, performances
    best_target, max_std = max(spreads, key=lambda x: x[1])
    return max_std, best_target, performances

def wiggle(line, scale):
    start_point = line[0] + np.random.normal(0, scale, 2)
    start_point = np.clip(start_point, 1, 10)

    end_point = line[-1] + np.random.normal(0, scale, 2)
    end_point = np.clip(end_point, 1, 10)

    X = np.linspace(start_point[1], end_point[1], 100)
    Y = np.linspace(start_point[0], end_point[0], 100)
    return np.column_stack((Y, X))

def plot_performace(performances):
    plt.figure(figsize=(10, 5))
    for performance in performances:
        plt.plot(continuous, performance, color="r", alpha=0.1)

    plt.xlim(1, 10)
    plt.xlabel('Difficulty')
    plt.ylabel('Performance')
    plt.title('Performance vs. Difficulty')
    plt.legend()
    plt.show()



def plot_spreads(spreads, targets):
    plt.figure(figsize=(4, 1))
    plt.bar(*zip(*spreads))
    plt.xticks(targets)
    plt.xlabel('target performance')
    plt.ylabel('Spread')
    plt.title('Spread vs. target performance')
    plt.show()

def subplot_line(line, std, performances):
    # Replicate plot_line, but gather the plots in a subplot
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))

    ax = axs[0]
    # ax.matshow(datas[-1], extent=(1, 10, 1, 10), origin='lower')
    # ax.colorbar = plt.colorbar(ax.images[0], ax=ax, orientation='vertical')
    ax.plot(line[:, 1], line[:, 0], color='r')
    # write the coords of the line
    ax.text(line[0, 1], line[0, 0], f"({line[0, 1]:.2f}, {line[0, 0]:.2f})", fontsize=8)
    ax.text(line[-1, 1], line[-1, 0], f"({line[-1, 1]:.2f}, {line[-1, 0]:.2f})", fontsize=8)
    ax.scatter(line[0, 1], line[0, 0], color='r')
    ax.scatter(line[-1, 1], line[-1, 0], color='r')

    ax.set_xlim(1, 10)
    ax.set_ylim(1, 10)
    ax.set_xlabel("P(death)")
    ax.set_ylabel("\u0394gap")
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xticks(range(1, 11))
    ax.set_yticks(range(1, 11))
    ax.set_title(f'{std = :.2f}')

    ax = axs[1]
    for p in performances:
        ax.plot(continuous, p, color="r", alpha=0.1)
    ax.set_xlim(1, 10)
    ax.set_xlabel('Difficulty')
    ax.set_ylabel('Performance')
    ax.set_title('Performance vs. Difficulty')

    plt.show()

def axis_setup(ax1, ax2):
    ax1.clear()
    ax2.clear()

    ax1.set_xlim(1, 10)
    ax1.set_ylim(1, 10)
    ax1.set_xlabel("P(death)")
    ax1.set_ylabel("\u0394gap")
    ax1.xaxis.set_ticks_position('bottom')
    ax1.set_xticks(range(1, 11))
    ax1.set_yticks(range(1, 11))

    ax2.set_xlim(1, 10)
    ax2.set_xlabel('Difficulty')
    ax2.set_ylabel('Performance')
    ax2.set_title('Performance vs. Difficulty')

def plot_update(line, std, Z, target, performances, fig, ax1, ax2):
    """Called to update the plot with new data."""
    # Clear and setup axes
    axis_setup(ax1, ax2)

    # Axis 1 line plot
    ax1.matshow(Z, extent=(1, 10, 1, 10), origin='lower')
    ax1.plot(line[:, 1], line[:, 0], color='r')
    ax1.text(line[0, 1], line[0, 0], f"({line[0, 1]:.2f}, {line[0, 0]:.2f})", fontsize=8)
    ax1.text(line[-1, 1], line[-1, 0], f"({line[-1, 1]:.2f}, {line[-1, 0]:.2f})", fontsize=8)
    ax1.scatter(line[0, 1], line[0, 0], color='r')
    ax1.scatter(line[-1, 1], line[-1, 0], color='r')
    ax1.set_title(f'{std = :.2f}')

    # Axis 2 performance plot
    for p in performances:
        ax2.plot(continuous, p, color="r", alpha=0.1)
    ax2.axhline(target, color='b', linestyle='--', label=f"target: {target:.2f}")

    # Draw and flush
    fig.canvas.draw()
    fig.canvas.flush_events()

    plt.pause(0.01)
    
def main():
    datas = [np.load(f"{p}_means.npy") for p in all_players][3:]  # Remove worst 2 players
    Zs = np.array([interpolate(d) for d in datas])
    Z = Zs.mean(axis=0)
    # line = np.column_stack((np.full_like(continuous, 3), continuous)) 
    line = np.column_stack((continuous, continuous))  # Slope 1 line
    # line = np.load("line.npy")
    line_history = np.array(np.hstack([line[0], line[-1]]))
    targets = np.arange(10, 45, 5)  # target performances

    plt.ion()  # Enable interactive mode

    # Initial data
    std, target, performances = eval_line(datas, line, targets)

    # Plot initial data
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    plot_update(line, std, Z, target, performances, fig, ax1, ax2)

    def on_key(event):
        if event.key == 'q':
            quit()
    fig.canvas.mpl_connect('key_press_event', on_key)
    
    scale0 = 0.1
    scale = scale0
    fails = 0
    while True:
        _line = wiggle(line, scale)
        _std, target, performances = eval_line(datas, _line, targets)

        if _std > std:
            line = _line
            std = _std
            # np.save("line.npy", line)
            line_history = np.vstack((line_history, np.hstack([line[0], line[-1]])))
            # np.save("line_history.npy", line_history)
            plot_update(_line, _std, Z, target, performances, fig, ax1, ax2)

            fails = 0
            scale = scale0
        else:
            fails += 1
            if fails > 5:
                scale += scale0
                if scale > 1:
                    scale = scale0
                    continue
    
    
def wiggle_demo():
    # plt.ion()  # Enable interactive mode

    # from matplotlib.widgets import Slider
    # slider = Slider(ax_slider, 'Phase', 0, 2*np.pi, valinit=0)
    fig, ax = plt.subplots()
    # Create initial data
    line = np.column_stack((continuous, np.full_like(continuous, 3)))

    def _clear():
        ax.clear()
        ax.set_xlim(1, 10)
        ax.set_ylim(1, 10)
        ax.set_xlabel("P(death)")
        ax.set_ylabel("\u0394gap")
        ax.xaxis.set_ticks_position('bottom')
        ax.set_xticks(range(1, 11))
        ax.set_yticks(range(1, 11))

    def _plot(line):
        ax.plot(line[:, 1], line[:, 0], color='r')
        ax.scatter(line[0, 1], line[0, 0], color='r')
        ax.scatter(line[-1, 1], line[-1, 0], color='r')
    
    _clear()
    _plot(line)

    for i in range(1000):
        _clear()
        line = wiggle(line, scale=0.1)
        _plot(line)
        plt.pause(0.01)

def play_history():
    # plt.ion()  # Enable interactive mode
    datas = [np.load(f"{p}_means.npy") for p in all_players][3:]  # Remove worst 2 players
    lines = np.load("line_history.npy") # starty, startx, endy, endx

    fig, ax = plt.subplots()
    ax.set_xlim(1, 10)
    ax.set_ylim(1, 10)
    ax.set_xlabel("P(death)")
    ax.set_ylabel("\u0394gap")
    ax.set_xticks(range(1, 11))
    Zs = np.array([interpolate(d) for d in datas])
    Z = Zs.mean(axis=0)
    # matshow the Z matrix
    ax.matshow(Z, extent=(1, 10, 1, 10), origin='lower')
    ax.xaxis.set_ticks_position('bottom')
    curve, = ax.plot([lines[0, 1], lines[0, 3]], [lines[0, 0], lines[0, 2]], color='r')
    start, = ax.plot(lines[0, 1], lines[0, 0], 'ro')
    end, = ax.plot(lines[0, 3], lines[0, 2], 'ro')
    print(lines.shape)
    for i, (a_y, a_x, b_y, b_x) in enumerate(lines):
        # set yvalues
        curve.set_ydata([a_y, b_y])
        curve.set_xdata([a_x, b_x])
        start.set_ydata([a_y])
        start.set_xdata([a_x])
        end.set_ydata([b_y])
        end.set_xdata([b_x])
        # plot line

        # ax.clear()
        # ax.plot([a_x, b_x], [a_y, b_y], color='r')
        # ax.scatter(a_x, a_y, color='r')
        # ax.scatter(b_x, b_y, color='r')
        ax.set_title(f"Step {i+1}/{len(lines)}")
        plt.pause(0.1)
    print(np.round(lines[-1], 2))
    

def test():
    line = np.column_stack((continuous, continuous))
    datas = [np.load(f"{p}_means.npy") for p in all_players][3:]  # Remove worst 2 players
    targets = np.arange(10, 45, 5)  # target performances
    eval_line(datas, line, targets)

if __name__ == "__main__":
    main()
    # wiggle_demo()
    # play_history()
    
    # from line_profiler import LineProfiler
    # profiler = LineProfiler()

    # # Add the function to the profiler
    # profiler.add_function(get_x)

    # # Run the wrapper function
    # profiler.run('test()')

    # # Print the profiling results
    # profiler.print_stats()