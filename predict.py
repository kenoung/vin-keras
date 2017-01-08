from __future__ import print_function
import argparse
import numpy as np
import cv2
from vin import vin_model, get_layer_output
from utils import process_map_data

def get_action(a):
    if a == 0: return -1, -1
    if a == 1: return  0, -1
    if a == 2: return  1, -1
    if a == 3: return -1,  0
    if a == 4: return  1,  0
    if a == 5: return -1,  1
    if a == 6: return  0,  1
    if a == 7: return  1,  1
    return None

def find_goal(m):
    return np.argwhere(m.max() == m)[0][::-1]

def predict(im, pos, model, k):
    res = model.predict([np.array([im]), np.array([pos])])

    action = np.argmax(res)
    reward = get_layer_output(model, 'reward', np.array([im]))
    value = get_layer_output(model, 'value{}'.format(k), np.array([im]))
    reward = np.reshape(reward, reward.shape[2:])
    value = np.reshape(value, value.shape[2:])

    return action, reward, value

def main():
    parser = argparse.ArgumentParser(description='VIN')
    parser.add_argument('--data', '-d', type=str, default='./map_data.pkl',
                        help='Path to map data generated with script_make_data.py')
    parser.add_argument('--model', '-m', type=str, default='',
                        help='Model from given file')
    args = parser.parse_args()

    k = 20
    model = vin_model(k=k)
    model.load_weights(args.model)
    train, test = process_map_data(args.data)

    for d in zip(*test):
        im = d[0]
        pos = d[1]
        action, reward, value = predict(im, pos, model, k)

        path = [tuple(pos)]
        for _ in range(30):
            if im[1][pos[1], pos[0]] == 1:
                break
            action, _, _ = predict(im, pos, model, k)
            dx, dy = get_action(action)
            pos[0] = pos[0] + dx
            pos[1] = pos[1] + dy
            path.append(tuple(pos))

        test_img = cv2.cvtColor(im[0], cv2.COLOR_GRAY2BGR)
        goal = find_goal(im[1])

        for s in path:
            cv2.rectangle(test_img, (s[0], s[1]), (s[0], s[1]), (1, 0, 0), -1)
        cv2.rectangle(test_img, (path[0][0], path[0][1]), (path[0][0], path[0][1]), (0, 1, 1), -1)
        cv2.rectangle(test_img, (goal[0], goal[1]), (goal[0], goal[1]), (0, 0, 1), -1)
        cv2.imshow("image", cv2.resize(255 - test_img * 255, (300, 300), interpolation=cv2.INTER_NEAREST))
        cv2.imshow("reward", cv2.resize(reward, (300, 300), interpolation=cv2.INTER_NEAREST))
        cv2.imshow("value", cv2.resize(value / 80, (300, 300), interpolation=cv2.INTER_NEAREST))
        cv2.waitKey(0)

if __name__ == "__main__":
    main()