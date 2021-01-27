import cv2
import numpy as np
import matplotlib.pyplot as plt


img = cv2.imread(r'Data/Video1/images/frame_000000.PNG')
rows, cols, ch = img.shape

pts1 = np.float32([[204, 94], [350, 90], [213, 355], [547, 330]])
pts2 = np.float32([[0, 0], [160, 0], [0, 200], [160, 200]])

M = cv2.getPerspectiveTransform(pts1, pts2)

dst = cv2.warpPerspective(img, M, (170, 200))

"""
plt.subplot(121), plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)), plt.title('Input')
plt.subplot(122), plt.imshow(cv2.cvtColor(dst, cv2.COLOR_BGR2RGB)), plt.title('Output')
plt.show()"""

plt.imshow(cv2.cvtColor(dst, cv2.COLOR_BGR2RGB))
plt.show()

print(M.dot(np.array([204, 94, 1])))

print(M.dot(np.array([213, 355, 1])))
