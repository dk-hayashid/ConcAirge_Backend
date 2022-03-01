import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from PIL import Image
plt.rcParams["font.size"] = 18


def return_close_value_idxes(measured_data, target, n=5):
    diffs = [abs(measured_value - target) for measured_value in measured_data]
    diffs_bottom_idxes = np.argsort(diffs)[:n]
    return diffs_bottom_idxes

def generate_cmap(colors):
    """自分で定義したカラーマップを返す"""
    values = range(len(colors))
    vmax = np.ceil(np.max(values))
    color_list = []
    for v, c in zip(values, colors):
        color_list.append( ( v/ vmax, c) )
    return LinearSegmentedColormap.from_list('custom_cmap', color_list)

def save_temperature_map(data: np.ndarray, target: float):

    close_value_idxes = return_close_value_idxes(data, target)

    # 図の生成
    fig = plt.figure(figsize=(5, 5))
    ax = plt.gca()

    # 目盛りの調整
    ax.grid(color='black', linestyle='-.', linewidth=1)
    ax.set_xticks(np.arange(0, 6, 1))
    ax.set_yticks(np.arange(0, 11, 1))

    # 温度マッピング
    im = Image.open("room_layout.png")
    cm = generate_cmap(['#B5D2EC','#FFFFFF','#FC5B4A'])
    plt.pcolormesh(data.reshape(11, 5)[::-1,:], cmap=cm, edgecolors='k', linewidth=2, alpha=0.7)
    ax.imshow(im, extent=[*ax.get_xlim(), *ax.get_ylim()], aspect='auto', alpha=1)

    # 誘導場所のピン打ち
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    width = abs((xmax - xmin) / 5)
    height = abs((ymax - ymin) / 11)
    list_coordinate = []
    for y_coordinate in np.arange(ymin + height / 2, ymax, height):
        for x_coordinate in np.arange(xmin + width / 2, xmax, width):
            list_coordinate.append([x_coordinate, y_coordinate])
    list_coordinate_target = [list_coordinate[idx] for idx in close_value_idxes]

    image = plt.imread('./locater.png')
    for coordinate_target in list_coordinate_target:
        ax.add_artist( 
            AnnotationBbox(
                OffsetImage(image, zoom=0.06), (coordinate_target[0], coordinate_target[1]+height/2), frameon=False
            )
        )

    # 全体のレイアウト調整
    spines = 5
    ax.spines["top"].set_linewidth(spines)
    ax.spines["left"].set_linewidth(spines)
    ax.spines["bottom"].set_linewidth(spines)
    ax.spines["right"].set_linewidth(spines)
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
    plt.colorbar()
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
    fig.savefig('./map.png', transparent=True)
