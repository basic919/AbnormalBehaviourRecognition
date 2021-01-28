import json
import numpy as np
import matplotlib.pyplot as plt
import math


# helper function, not a predicate
# returns the shortest distance from a pont to a line
def shortest_distance(points, line_f, line_l):
    a = line_f[1] - line_l[1]
    b = line_l[0] - line_f[0]
    c = (line_f[0] - line_l[0]) * line_f[1] + (line_l[1] - line_f[1]) * line_f[0]

    if a == 0 and b == 0:
        res = 0
    else:
        res = (a * points[0] + b * points[1] + c) / (math.sqrt(a * a + b * b))
    return res


# individual predicates
def inline(track, m, scale=1):
    # scale => length of one pixel
    j = m  # current frame
    dist_list = []

    for i in range(len(track) - m):
        # predicate value for one frame
        first_frame = j - m + 1 + i
        last_frame = j + i

        dist = 0

        for f in range(first_frame, last_frame + 1):
            dist += abs(shortest_distance(track[f], np.array(track[first_frame]), np.array(track[last_frame])))

        dist_list.append(dist * scale)
    return dist_list


def turn_left(track, m, scale=1):
    # scale => length of one pixel
    j = m  # current frame
    dist_list = []

    for i in range(len(track) - m):
        # predicate value for one frame
        first_frame = j - m + 1 + i
        last_frame = j + i
        dist = 0

        for f in range(first_frame, last_frame + 1):
            dist += max(0, shortest_distance(track[f],  np.array(track[first_frame]), np.array(track[last_frame])))

        dist_list.append(dist * scale)
    return dist_list


def turn_right(track, m, scale=1):
    # scale => length of one pixel
    j = m  # current frame
    dist_list = []

    for i in range(len(track) - m):
        # predicate value for one frame
        first_frame = j - m + 1 + i
        last_frame = j + i
        dist = 0

        for f in range(first_frame, last_frame + 1):
            dist += max(0, -shortest_distance(track[f],  np.array(track[first_frame]), np.array(track[last_frame])))

        dist_list.append(dist * scale)
    return dist_list


def turn_back(track, m):
    j = m  # current frame
    dist_list = []

    for i in range(len(track) - m):
        # predicate value for one frame
        first_frame = j - m + 1 + i
        last_frame = j + i

        fp = np.array(track[first_frame])
        lp = np.array(track[last_frame])

        if (fp == lp).all():  # random pomak za jedan piksel ako su isti (zbog dijeljenja s nulom)
            if np.random.randint(2) == 0:
                fp[np.random.randint(2)] += 1
            else:
                fp[np.random.randint(2)] += 1

        dist_max = 0

        for f in range(first_frame, last_frame + 1):
            dist_max = max(dist_max, abs(shortest_distance(track[f], fp, lp)))

        dist_list.append(dist_max / np.linalg.norm(fp - lp))
    return dist_list


def circle(track, m):
    j = m  # current frame
    variance_list = []

    for i in range(len(track) - m):
        # predicate value for one frame
        first_frame = j - m + 1 + i
        last_frame = j + i

        centroid = np.mean(track[first_frame:last_frame + 1], axis=0)
        dist_list = []

        for f in range(first_frame, last_frame + 1):
            dist_list.append(np.linalg.norm(centroid - track[f]))

        variance_list.append(np.var(dist_list))
    return variance_list


def direction(track, m):
    j = m  # current frame
    direction_list = []

    for i in range(len(track) - m):
        # predicate value for one frame
        first_frame = j - m + 1 + i
        last_frame = j + i

        fp = np.array(track[first_frame])
        lp = np.array(track[last_frame])

        difference = lp - fp
        sine = abs(difference / np.linalg.norm(lp - fp))
        direction_str = ''

        if sine[0] < 0.383:
            if difference[1] < 0:
                direction_str += 'N'
            else:
                direction_str += 'S'
        elif sine[1] < 0.383:
            if difference[0] < 0:
                direction_str += 'W'
            else:
                direction_str += 'E'
        elif 0.383 <= sine[1] <= 0.924:
            if difference[1] < 0:
                direction_str += 'N'
                if difference[0] < 0:
                    direction_str += 'W'
                else:
                    direction_str += 'E'
            else:
                direction_str += 'S'
                if difference[0] < 0:
                    direction_str += 'W'
                else:
                    direction_str += 'E'
        else:
            direction_str += 'X'

        direction_list.append(direction_str)

    return direction_list


def individual_velocity(track, m, scale=1):
    # scale => length of one pixel
    j = m  # current frame
    dist_list = []

    for i in range(len(track) - m):
        # predicate value for one frame
        first_frame = j - m + 1 + i
        last_frame = j + i

        dist = 0

        for f in range(first_frame, last_frame):
            dist += np.linalg.norm(np.array(track[f]) - np.array(track[f + 1]))

        dist_list.append((dist / (m - 1)) * scale)
    return dist_list


# group predicates
def group_velocity(tracks, m, scale=1):
    # scale => length of one pixel
    j = m  # current frame
    dist_list = []

    # predicate value for one frame
    for i in range(len(tracks[0]) - m):
        dist = 0

        first_frame = j - m + 1 + i
        last_frame = j + i

        for track in tracks:
            for f in range(first_frame, last_frame):
                dist += np.linalg.norm(np.array(track[f]) - np.array(track[f + 1]))

        dist_list.append((dist / ((m - 1) * len(tracks))) * scale)
    return dist_list


def group_distance(tracks, m, scale=1):
    # scale => length of one pixel
    j = m  # current frame
    dist_list = []

    # predicate value for one frame
    for i in range(len(tracks[0]) - m):
        dist = 0

        first_frame = j - m + 1 + i
        last_frame = j + i

        for t1 in range(len(tracks) - 1):
            for t2 in range(t1 + 1, len(tracks)):
                for f in range(first_frame, last_frame + 1):
                    dist += np.linalg.norm(np.array(tracks[t1][f]) - np.array(tracks[t2][f]))

        dist_list.append((dist / ((m - 1) * (len(tracks) * (len(tracks) - 1) / 2)) * scale))
    return dist_list


def group_dynamic(tracks, m, scale=1):
    # scale => length of one pixel
    j = m  # current frame
    dist_list = []

    # predicate value for one frame
    for i in range(len(tracks[0]) - m):
        dist1 = 0
        dist2 = 0

        first_frame = j - m + 1 + i
        last_frame = j + i

        for t1 in range(len(tracks) - 1):
            for t2 in range(t1 + 1, len(tracks)):
                for f in range(first_frame, last_frame + 1):
                    dist1 += np.linalg.norm(np.array(tracks[t1][first_frame]) - np.array(tracks[t2][first_frame]))
                    dist2 += np.linalg.norm(np.array(tracks[t1][last_frame]) - np.array(tracks[t2][last_frame]))

        dist_list.append(((dist2 - dist1) / ((m - 1) * (len(tracks) * (len(tracks) - 1) / 2)) * scale))
    return dist_list


if __name__ == '__main__':

    # path = r'Data/Test Results/transformed_tracks_video01.json'
    path = r'Simulation/simulated_tracks.json'

    tracked_individuals = ["0", "1", "2"]
    m_frames = 20  # number of past frames used

    # in video no.0, 1 pixel represents the distance of 5.12 centimeter
    px_to_cm = 5.12

    # inline
    trajectories = []
    for tracked_individual in tracked_individuals:
        trajectory = []

        with open(path) as json_file:
            data = json.load(json_file)
            for ind in data[tracked_individual]:
                trajectory.append(data[tracked_individual][ind])
            trajectories.append(trajectory)

    # individual plot
    for trajectory in trajectories:

        inline_result = inline(trajectory, m_frames, scale=px_to_cm)
        # print(direction(track, m_frames))

        plt.plot(list(range(len(trajectory) - m_frames)), inline_result)
    plt.title("Individual Predicate")
    plt.legend(tracked_individuals)
    plt.xticks(range(0, len(data[tracked_individuals[0]]) - m_frames, 5),
               list(data[tracked_individuals[0]])[m_frames::5], rotation=90)
    plt.show()

    # group plot
    '''inline_result = group_dynamic(trajectories, m_frames)
    plt.plot(list(range(len(trajectories[0]) - m_frames)), inline_result)
    plt.title("Group Predicate")
    plt.legend(tracked_individuals)
    plt.xticks(range(0, len(data[tracked_individuals[0]]) - m_frames, 5),
               list(data[tracked_individuals[0]])[m_frames::5], rotation=90)
    plt.show()'''
