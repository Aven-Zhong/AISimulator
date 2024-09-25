from matplotlib import pyplot as plt
import numpy as np
import datetime
from statistics import mean


def loadtxtmethod(filename):
    data = np.loadtxt(filename, dtype=np.float32, delimiter=',')
    return data


def plot_rewards(filename, label):
    x = []
    y = []
    avg_y = []
    i = 1
    data = loadtxtmethod(filename)
    for row in data:
        x.append(i)
        i += 1
        y.append(row)
        if i > 20:
            avg = mean(y[i - 19:i])
            avg_y.append(avg)
        else:
            avg_y.append(row)

    plt.plot(x, avg_y, linewidth=1, label=label)
    plt.xlabel("Episode")
    plt.ylabel("Rewards")
    plt.legend()

def plot_rewards_combine(ax, filename, label):
    x = []
    y = []
    avg_y = []
    i = 1
    data = loadtxtmethod(filename)
    for row in data:
        x.append(i)
        i += 1
        y.append(row)
        if i > 20:
            avg = mean(y[i-19:i])
            avg_y.append(avg)
        else:
            avg_y.append(row)

    ax.plot(x, avg_y, linewidth=1, label=label)
    ax.set_xlabel("Episode")
    ax.set_ylabel("Rewards")
    ax.legend()


if __name__ == "__main__":
    # Plot total_reward_attack_angle, total_reward_distance, and total_reward_alt on one figure
    plt.figure(figsize=(10, 6))
    plot_rewards('./TXT/total_reward_attack_angle.txt', 'Total_reward_attack_angle')
    plot_rewards('./TXT/total_reward_distance.txt', 'Total_reward_distance')
    plot_rewards('./TXT/total_reward_alt.txt', 'Total_reward_alt')
    day = str(datetime.datetime.today().day)
    month = str(datetime.datetime.today().month)
    hour = str(datetime.datetime.today().hour)
    minute = str(datetime.datetime.today().minute)
    title = month + '-' + day + ' ' + hour + ':' + minute + '  Total Rewards'
    plt.title(title)
    plt.savefig("./PIC/total_reward_compare.png")
    plt.show()

    # Plot total_reward_alt on a separate figure
    plt.figure(figsize=(10, 6))
    plot_rewards('./TXT/total_reward.txt', 'Total_reward')
    title = month + '-' + day + ' ' + hour + ':' + minute + '  Total Reward Alt'
    plt.title(title)
    plt.savefig("./PIC/total_rewards.png")
    plt.show()

    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))

    # Plot total_reward_attack_angle, total_reward_distance, and total_reward_alt on the first subplot
    plot_rewards_combine(ax1, './TXT/total_reward_attack_angle.txt', 'Total_reward_attack_angle')
    plot_rewards_combine(ax1, './TXT/total_reward_distance.txt', 'Total_reward_distance')
    plot_rewards_combine(ax1, './TXT/total_reward_alt.txt', 'Total_reward_alt')
    day = str(datetime.datetime.today().day)
    month = str(datetime.datetime.today().month)
    hour = str(datetime.datetime.today().hour)
    minute = str(datetime.datetime.today().minute)
    title = month + '-' + day + ' ' + hour + ':' + minute + '  Total Rewards'
    ax1.set_title(title)

    # Plot total_reward_alt on the second subplot
    plot_rewards_combine(ax2, './TXT/total_reward.txt', 'Total_reward')
    title = month + '-' + day + ' ' + hour + ':' + minute + '  Total Reward Alt'
    ax2.set_title(title)

    # Adjust layout to prevent overlapping
    plt.tight_layout()

    # Save the combined plot
    plt.savefig("./PIC/combined_plots.png")

    # Show the combined plot
    plt.show()
