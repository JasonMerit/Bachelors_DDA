from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel
import numpy as np
import matplotlib.pyplot as plt




def prepare_data(data_path):
    data = np.load(f"{data_path}_means.npy")
    std_mat = np.load(f"{data_path}_std.npy")
    var = (std_mat**2).ravel()

    X_train = np.array([(i, j) for j in range(1, 11) for i in range(1, 11)])
    y_train = data.ravel()  # Unravels the 2D array into a 1D array
    return X_train, y_train, var

def get_gaussian_process(X_train, y_train, var):
    # Optimizing kernel hyperparameters on the training data
    kernel = ConstantKernel(constant_value=1.14e+03**2,constant_value_bounds =(1e-1,1e10)) \
            * RBF(length_scale=1.59, length_scale_bounds=(1e-1, 1e10))
    gaussian_process = GaussianProcessRegressor(kernel=kernel, 
                                                alpha=var, 
                                                n_restarts_optimizer=9)
    gaussian_process.fit(X_train, y_train)
    return gaussian_process

def save_gaussian_process(gaussian_process, path):
    import pickle
    with open(path, "wb") as f:
        pickle.dump(gaussian_process, f)

def load_gaussian_process(path):
    import pickle
    with open(path, "rb") as f:
        return pickle.load(f)

def plot(gaussian_process):
    # Define grid points for plotting
    x_min, x_max = 1, 10
    y_min, y_max = 1, 10
    x_grid = np.linspace(x_min, x_max, 100)
    y_grid = np.linspace(y_min, y_max, 100)
    X, Y = np.meshgrid(x_grid, y_grid)
    XY = np.column_stack([X.ravel(), Y.ravel()])

    # Predict mean and standard deviation of predictions
    y_pred = gaussian_process.predict(XY)
    Z = y_pred.reshape(X.shape)
    # Z_std = y_std.reshape(X.shape)

    # Plot the contour plot of the mean predictions
    plt.contourf(X, Y, Z)
    plt.colorbar(label='Predicted Output')


    plt.xlabel("p_death")
    plt.ylabel("\u0394gap")
    plt.title('2D Gaussian Process with Error Bars')
    # plt.legend()
    plt.show()

def subplot(gps):
    # Define grid points for plotting
    D = np.linspace(1, 10, 100)
    X, Y = np.meshgrid(D, D)
    XY = np.column_stack([X.ravel(), Y.ravel()])

    fig, axs = plt.subplots(1, len(gps), figsize=(15, 5))


    for i, ax in enumerate(axs):
        # Predict mean and standard deviation of predictions
        y_pred = gps[i].predict(XY)
        Z = y_pred.reshape(X.shape)  # Tranpose to agree with difficulty matrix

        # Make contour plot of the mean predictions
        # The image is squished, so make xaxis wider
        im = ax.contourf(X, Y, Z)

        # Add colorbar
        ax.figure.colorbar(im, ax=ax, orientation='vertical')

        ax.set_xlabel("p_death")
        ax.set_ylabel("\u0394gap")
        ax.set_title(abilities[i])
    plt.show()


def plot_all():
    path = "gps.pkl"
    gps = load_gaussian_process(path)

    D = np.linspace(1, 10, 100)
    X, Y = np.meshgrid(D, D)
    XY = np.column_stack([X.ravel(), Y.ravel()])

    fig, axs = plt.subplots(10, 10, figsize=(10, 10))
    axs = axs.ravel()
    for i, ax in enumerate(axs):
        # Predict mean and standard deviation of predictions
        y_pred = gps[i].predict(XY)
        Z = y_pred.reshape(X.shape)  # Tranpose to agree with difficulty matrix

        # Make contour plot of the mean predictions
        im = ax.contourf(X, Y, Z)

        # Add colorbar
        # ax.figure.colorbar(im, ax=ax, orientation='vertical')

        # ax.set_xlabel("p_death")
        # ax.set_ylabel("\u0394gap")
        # ax.set_title(abilities[i])
    plt.show()
    
def main():
    datas = [prepare_data(p) for p in players]
    gps = [get_gaussian_process(*d) for d in datas]
    subplot(gps)

if __name__ == "__main__":
    from model_config import players, abilities, all_players
    # main()
    plot_all()