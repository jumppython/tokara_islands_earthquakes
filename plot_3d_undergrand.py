import os
import operator
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

plt.rcParams['font.family'] = "MS Gothic"

def ops(o: str):
    odict = {"<": operator.lt,
             "<=": operator.le,
             "==": operator.eq,
             ">=": operator.ge,
             ">": operator.gt}
    return odict[o]


def circle_size(mag: float) -> float:
    base_size = 5
    if mag < 2:
        return base_size * 1
    elif 2 <= mag < 3:
        return base_size * 10
    elif 3 <= mag < 4:
        return base_size * 20
    elif 4 <= mag < 5:
        return base_size * 30
    elif 5 <= mag:
        return base_size * 40
    else:
        return base_size * 50


def circle_clr(v: float) -> float:
    return v


def filter_data(fp: str, dt_cond: datetime=None, times: str=">= 100") -> pd.DataFrame:
    df = pd.read_csv(fp, parse_dates=["happened_time"])

    oper_, num_ = times.split(' ')
    df = df[ops(o=oper_)(df["times"], int(num_))].reset_index(drop=True)
    
    if dt_cond is not None:
        use_df = df[df["happened_time"] >= dt_cond].reset_index(drop=True)
        return use_df
    else:
        return df


def plot_4_images(df: pd.DataFrame, plot_item: str,
                  circle_size_item: str, circle_size_func: callable,
                  circle_clr_item: str, circle_clr_func: callable,
                  **kwargs):
    x = df.lon.tolist()
    y = df.lat.tolist()
    z = df[plot_item].tolist()

    circle_size_coll = df[circle_size_item].map(lambda item_val: circle_size_func(item_val))
    circle_color_coll = df[circle_clr_item].map(lambda item_val: circle_clr_func(item_val))

    fig, axs = plt.subplots(2, 2, figsize=(9.5, 8.5), subplot_kw={"projection": "3d"})
    fig.suptitle("吐噶喇列島　震源分布3D")

    title_list = ["上-下　断面", "東-西　断面",
                  "南-北　断面", "45° 俯瞰"]
    # view plane	elev	azim
    # XY		    90	    -90
    # XZ		    0	    -90
    # YZ		    0	    0
    # -XY		    -90	    90
    # -XZ		    0	    90
    # -YZ		    0	    180
    view_init_list = [{"elev": 90, "azim": -90}, {"elev": 0, "azim": 0},
                      {"elev": 0, "azim": -90}, {}]
    proj_type_list = ['ortho', 'ortho',
                      'ortho', 'persp']
    tick_param_list = [{'axis': 'x', 'rotation': 30}, {'axis': 'y', 'rotation': 30},
                       {'axis': 'x', 'rotation': 30}, {}]

    images = []
    for ax, title, view_init, proj_type, tick_param in zip(axs.flat, title_list, view_init_list,
                                                           proj_type_list, tick_param_list):
        img = ax.scatter(x, y, z, s=circle_size_coll, c=circle_color_coll, cmap="binary")
        ax.set_xlabel("Longitude", labelpad=20)
        ax.set_ylabel("Latitude", labelpad=20)
        ax.set_zlabel("Depth (km)")
        ax.set_title(title)
        ax.view_init(**view_init)
        ax.set_proj_type(proj_type)
        ax.tick_params(**tick_param)
        images.append(img)
        fig.colorbar(img, ax=ax, shrink=.45, orientation="horizontal", fraction=.05)

    fig.subplots_adjust(left=0.05, right=0.95, bottom=0.1, top=0.95,
                        wspace=0.01, hspace=0.02)

    plt.tight_layout()
    #plt.show()
    plt.savefig(os.path.join("graph", kwargs["save_as"]), dpi=400)


def plot_animation(df: pd.DataFrame, plot_item: str,
                   circle_size_item: str, circle_size_func: callable,
                   circle_clr_item: str, circle_clr_func: callable,
                   **kwargs):

    date_list = df["happened_time"].dt.date.unique().tolist()
    daily_df = {date_: df[df["happened_time"].dt.date == date_] for date_ in date_list}

    init_df = df
    x = init_df.lon.tolist()
    y = init_df.lat.tolist()
    z = init_df[plot_item].tolist()

    circle_size_coll = init_df[circle_size_item].map(lambda item_val: circle_size_func(item_val))
    circle_color_coll = init_df[circle_clr_item].map(lambda item_val: circle_clr_func(item_val))

    fig, axs = plt.subplots(2, 2, figsize=(9.5, 8.5), subplot_kw={"projection": "3d"})
    fig.suptitle("吐噶喇列島　震源分布3D")

    title_list = ["上-下　断面　{date_i}", "東-西　断面　{date_i}",
                  "南-北　断面　{date_i}", "45° 俯瞰　{date_i}"]
    view_init_list = [{"elev": 90, "azim": -90}, {"elev": 0, "azim": 0},
                      {"elev": 0, "azim": -90}, {}]
    proj_type_list = ['ortho', 'ortho',
                      'ortho', 'persp']
    tick_param_list = [{'axis': 'x', 'rotation': 30}, {'axis': 'y', 'rotation': 30},
                       {'axis': 'x', 'rotation': 30}, {}]

    scatters = []
    ax_coll = []
    for ax, title, view_init, proj_type, tick_param in zip(axs.flat, title_list, view_init_list,
                                                           proj_type_list, tick_param_list):
        scatter = ax.scatter(x, y, z, c=circle_color_coll, s=circle_size_coll, cmap="brg")
        ax.set_xlim(128.9, 130.1)
        ax.set_ylim(28.8, 29.9)
        ax.set_zlim(-60, 0)
        ax.set_xlabel("Longitude", labelpad=20)
        ax.set_ylabel("Latitude", labelpad=20)
        ax.set_zlabel("Depth (km)")
        ax.set_title(title.format(date_i=""))
        ax.view_init(**view_init)
        ax.set_proj_type(proj_type)
        ax.tick_params(**tick_param)
        fig.colorbar(scatter, ax=ax, shrink=.45, orientation="horizontal", fraction=.05)
        scatters.append(scatter)
        ax_coll.append(ax)

    fig.subplots_adjust(left=0.05, right=0.95, bottom=0.1, top=0.95,
                        wspace=0.01, hspace=0.02)

    def animate(frame_date: datetime, frame_scatters, title_fmt, frame_ax):
        frame_df = daily_df[frame_date].reset_index(drop=True)
        f_x = frame_df["lon"].tolist()
        f_y = frame_df["lat"].tolist()
        f_z = frame_df[plot_item].tolist()

        f_circle_size_coll = frame_df[circle_size_item].map(lambda item_val: circle_size_func(item_val))
        f_circle_color_coll = frame_df[circle_clr_item].map(lambda item_val: circle_clr_func(item_val))

        for i, frame_scatter in enumerate(frame_scatters):
            frame_scatter._offsets3d = (f_x, f_y, f_z)
            frame_scatter.set_sizes(f_circle_size_coll)
            frame_scatter.set_array(f_circle_color_coll)
            frame_ax[i].set_title(title_fmt[i].format(date_i=frame_date))
            frame_scatter.set_cmap("brg")

    ani = FuncAnimation(fig, animate,
                        frames=date_list,
                        fargs=(scatters, title_list, ax_coll, ),
                        interval=1200)

    plt.tight_layout()

    #plt.show()
    ani.save(os.path.join("graph", kwargs["save_as"]), writer="pillow", dpi=72)


if __name__ == "__main__":

    used_data = filter_data("data/data_2025_formatted.csv",
                            dt_cond=datetime(2025, 1, 1, 0, 0),
                            times="> 0")

    #plot_4_images(df=used_data, plot_item="depth_km",
    #              circle_size_item="magnitude_scale", circle_size_func=circle_size,
    #              circle_clr_item="diff_bands", circle_clr_func=circle_clr,
    #              save_as="depth_magnitude_diff_bands.png")

    plot_animation(used_data, plot_item="depth_km",
                   circle_size_item="magnitude_scale", circle_size_func=circle_size,
                   circle_clr_item="diff_bands", circle_clr_func=circle_clr,
                   save_as="depth_magnitude_diff_bands.gif")

