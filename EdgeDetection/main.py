import sys
import numpy as np
import math
from skimage import io
from scipy import ndimage

def grad(im, sigma):
    im = im[:, :, 0]
    sigma = float(sigma)

    r = round(3 * sigma)      # радиус окна
    n = r * 2 + 1           # сторона окна

    x = np.arange(-r, r+1)
    y = np.reshape(x, (-1, 1))
    normal = 1 / (2 * np.pi * sigma**2)
    e = np.exp(-(x**2+y**2)/(2*sigma**2)) * normal

    im = im / im.max() * 255

    Gx = (-x/sigma**2) * e
    Gy = (-y/sigma**2) * e

    Ix = ndimage.convolve(im, Gx)
    Iy = ndimage.convolve(im, Gy)
    G = np.hypot(Ix, Iy)

    res = G / G.max() * 255
    theta = np.arctan2(Iy, Ix)

    return [res.astype(np.uint8), theta]

def nonmax(im, sigma):
    im, theta = grad(im, sigma)
    x0, x1 = im.shape
    res = np.zeros((x0, x1))
    angle = theta * 180 / np.pi
    angle[angle < 0] += 180

    for i in range(1, x0-1):
        for j in range(1, x1-1):
            if (0 <= angle[i, j] < 22.5) or (157.5 <= angle[i, j] <= 180):
                nmx = max(im[i, j-1], im[i, j+1])
            elif (22.5 <= angle[i, j] < 67.5):
                nmx = max(im[i-1, j-1], im[i+1, j+1])
            elif (67.5 <= angle[i, j] < 112.5):
                nmx = max(im[i-1, j], im[i+1, j])
            else:
                nmx = max(im[i+1, j-1], im[i-1, j+1])
            
            if im[i, j] >= nmx:
                res[i, j] = im[i, j]

    res = np.multiply(res, 255 / res.max())

    return res.astype(np.uint8)

def canny(im, sigma, thr_high, thr_low):
    im = nonmax(im, float(sigma))
    thr_high = float(thr_high) * im.max()
    thr_low = float(thr_low) * thr_high
    x0, x1 = im.shape
    res = np.zeros((x0, x1))

    low = 1
    high = 255

    low_i, low_j = np.where((thr_low <= im) & (im <= thr_high))
    high_i, high_j = np.where(im >= thr_high)

    res[low_i, low_j] = low
    res[high_i, high_j] = high

    for i in range(x0):
        for j in range(x1):
            if res[i, j] == low:
                try:
                    if (res[i-1, j-1] == high or res[i-1, j] == high
                      or res[i-1, j+1] == high or res[i, j-1] == high
                      or res[i, j+1] == high or res[i+1, j-1] == high
                      or res[i+1, j] == high or res[i+1, j+1] == high):
                        res[i, j] = 255
                    else:
                        res[i, j] = 0
                except IndexError:
                    pass

    return res.astype(np.uint8)

def vessels(im):
    im = im[:, :, 0]
    x0, x1 = im.shape
    res = np.zeros((x0, x1))
    im2 = ridge_detection(im, 2)
    im3 = ridge_detection(im, 3)
    im4 = ridge_detection(im, 4)
    for i in range(x0):
        for j in range(x1):
            res[i, j] = max(im2[i, j], im3[i, j], im4[i, j])
    return res.astype(np.uint8)

def ridge_detection(im, sigma):
    im = im / im.max() * 255
    x0, x1 = im.shape

    r = int(3 * sigma)
    n = 2 * r + 1

    x = np.arange(-r, r+1)
    y = np.reshape(x, (-1, 1))
    e = np.exp(-(x**2+y**2)/(2*sigma**2))

    g_xx = 1 / (2*np.pi*sigma**4) * (x**2/sigma**2-1) * e
    g_xy = 1 / (2*np.pi*sigma**6) * x * y * e
    g_yy = 1 / (2*np.pi*sigma**4) * (y**2/sigma**2-1) * e

    I_xx = ndimage.convolve(im, g_xx)
    I_xy = ndimage.convolve(im, g_xy)
    I_yy = ndimage.convolve(im, g_yy)

    eig_val = np.zeros((x0, x1))
    # eig_vec = np.zeros((x0, x1, 2))
    theta = np.zeros((x0, x1))
    res = np.zeros((x0, x1))

    for i in range(x0):
        for j in range(x1):
            xx = I_xx[i, j]
            xy = I_xy[i, j]
            yy = I_yy[i, j]
            H = np.array([[xx, xy], [xy, yy]])
            eval, evec = np.linalg.eig(H)
            m = np.argmax(abs(eval))
            theta[i, j] = np.arctan2(evec[m][1], evec[m][0])
            if eval[m] >= 0:
                eig_val[i, j] = eval[m]
                # eig_vec[i, j, :] = evec[m]

    im = eig_val
    angle = theta * 180 / np.pi
    angle[angle < 0] += 180

    for i in range(1, x0-1):
        for j in range(1, x1-1):
            if (0 <= angle[i, j] < 22.5) or (157.5 <= angle[i, j] <= 180):
                nmx = max(im[i+1, j-1], im[i-1, j+1])
            elif (22.5 <= angle[i, j] < 67.5):
                nmx = max(im[i-1, j], im[i+1, j])
            elif (67.5 <= angle[i, j] < 112.5):
                nmx = max(im[i-1, j-1], im[i+1, j+1])
            else:
                nmx = max(im[i, j-1], im[i, j+1])
                
            if im[i, j] >= nmx:
                res[i, j] = im[i, j]

    res = res / res.max() * 255

    return res.astype(np.uint8)

def main():

    if sys.argv[1] == 'grad':
        sigma = sys.argv[2]
        im = io.imread(sys.argv[3])
        io.imsave(sys.argv[4], grad(im, sigma)[0])

    if sys.argv[1] == 'nonmax':
        sigma = sys.argv[2]
        im = io.imread(sys.argv[3])
        io.imsave(sys.argv[4], nonmax(im, sigma))

    if sys.argv[1] == 'canny':
        sigma = sys.argv[2]
        thr_high = sys.argv[3]
        thr_low = sys.argv[4]
        im = io.imread(sys.argv[5])
        io.imsave(sys.argv[6], canny(im, sigma, thr_high, thr_low))

    if sys.argv[1] == 'vessels':
        im = io.imread(sys.argv[2])
        io.imsave(sys.argv[3], vessels(im))
    
    return 1

if __name__ == "__main__":
    main()