import matplotlib.pyplot as plt
import numpy as np
plt.rcParams["font.size"] = 18

def return_close_value(array, target):
    mindiff = np.inf
    minvalue = None
    for value in array:
        diff = abs(value - target)
        if diff < mindiff:
            mindiff = diff
            minvalue = value
    return minvalue

def save_temperature_map(data: np.ndarray, target: float):

    close_value = return_close_value(data, target)

    # 図の生成
    fig = plt.figure(figsize=(10,4))
    ax = plt.gca()

    # 目盛りの調整
    ax.grid(color='black', linestyle='-.', linewidth=1)
    ax.set_xticks(np.arange(0,7, 1))
    ax.set_yticks(np.arange(0,4, 1))

    # 温度マッピング
    plt.pcolormesh(data.reshape(3,6), cmap="Reds", edgecolors='k', linewidth=2)
    
    # 誘導場所のピン打ち
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    width = abs((xmax - xmin) / 6)
    height = abs((ymax - ymin) / 3)
    list_coordinate = []
    for y_coordinate in np.arange(ymin + height / 2, ymax, height):
        for x_coordinate in np.arange(xmin + width / 2, xmax, width):
            list_coordinate.append([x_coordinate, y_coordinate])
    dict_coordinate = {key:value for key, value in zip(data, list_coordinate)}
    x_coordinate_target, y_coordinate_target = [v for k, v in dict_coordinate.items() if k == close_value][0]
    ax.scatter(x_coordinate_target, y_coordinate_target, s=600, c="yellow", marker="*", alpha=0.9,
                linewidths=2, edgecolors="orange")

    # 全体のレイアウト調整
    spines=5
    ax.spines["top"].set_linewidth(spines)
    ax.spines["left"].set_linewidth(spines)
    ax.spines["bottom"].set_linewidth(spines)
    ax.spines["right"].set_linewidth(spines)
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
    plt.colorbar()
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
    ax.set_title('Temperature Map')
    # plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
    fig.savefig('./map.png', transparent=True)
