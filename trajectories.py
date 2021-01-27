import transform
import numpy as np
from xml.dom import minidom
import json
import cv2


# settings parameters
saving = False

xml_path = r"Data/Video1/annotations.xml"
image_path = r'Data/Video1/images/frame_000000.PNG'
image_pts = np.array([[204, 94], [350, 90], [213, 355], [547, 330]])


# program...

warped, M, maxWidth, maxHeight = transform.four_point_transform(image_path, image_pts)
xtl = ytl = xbr = ybr = 0

frames = []
x_points = []
y_points = []

xml_doc = minidom.parse(xml_path)

track_list = xml_doc.getElementsByTagName('track')

trajectory_dict = {}    # format: [id][frame] = (x, y)

for t in track_list:
    trajectory_dict[t.attributes['id'].value] = {}
    points = t.getElementsByTagName('box')
    for p in points:
        if p.attributes['occluded'].value == "0":
            x = (float(p.attributes['xtl'].value) + float(p.attributes['xbr'].value)) / 2
            y = float(p.attributes['ybr'].value)

            pt = (M.dot(np.array([x, y, 1])))
            pt = pt * (1.0 / pt[2])
            pt = np.round(pt, 0)
            # print(pt[0:2])

            # print(round(x, 2), round(y, 2))
            trajectory_dict[t.attributes['id'].value][p.attributes['frame'].value] = (pt[0], pt[1])


if saving:
    with open(r'Data/Test Results/transformed_tracks_video01.json', 'w+') as fp:
        json.dump(trajectory_dict, fp)

cord_list = []

circle = warped
for frame in range(146):
    name = r'Data/Video1/images/frame_000' + str(frame).zfill(3) + '.PNG'
    warped, M, maxWidth, maxHeight = transform.four_point_transform(name, image_pts)
    for pnt in trajectory_dict.values():
        cord = pnt.get(str(frame))
        if cord is not None:
            cord_list.append(cord)
            for i in cord_list:
                circle = cv2.circle(warped, (int(i[0]), int(i[1])), 3, (0, 0, 255), -1)

    cv2.imshow("Tracking", circle)
    cv2.waitKey(0)
