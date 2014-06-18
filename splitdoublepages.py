#!/usr/bin/python
# This is a standalone program. Pass an image name as a first parameter of the program.

import sys
from math import sin, cos, sqrt, pi
import cv2.cv as cv
import cv2
import urllib2
import os
import math
from os.path import isfile, join
from sets import Set
# toggle between CV_HOUGH_STANDARD and CV_HOUGH_PROBILISTIC
USE_STANDARD = False

threshold = 50

def verticalEnough(l):
    #print(l)
    x1,y1 = l[0]
    x2,y2 = l[1]
    angle = 90
    if x1 != x2:
        angle = int(math.atan((y1-y2)/(x2-x1))*180/math.pi)
   # print(angle)
    return abs(90 - angle) <= 5

def normalise(line,width):
    x1,y1 = line[0]
    x2,y2 = line[1]
    if x1 < 0:
        x1 = 0
    if x2 < 0:
        x2 = 0
    if x1 > width:
        x1 = width
    if x2 > width:
        x2 = width
    return ((x1,y1),(x2,y2))

def project(line,height,width):
    x1,y1 = line[0]
    x2,y2 = line[1]
    if x1 == x2:
        return ((x1,0),(x1,height))
    else:
        slope = (y2-y1)/(x2-x1)
        projto0      = (x1+slope*y1,0)
        projtoheight = (x2-slope*(height-y2),height)
        ret = normalise((projto0,projtoheight),width)
        print(ret)
        return ret

def nearenough(line1,line2):
    x11,y11 = line1[0]
    x12,y12 = line1[1]
    x21,y21 = line2[0]
    x22,y22 = line2[1]
    return abs(x11-x21) <= threshold and abs(x12-x22) <= threshold
    
    
def merge(projectedlines,width):
    # new algorithm ... go left to right swalloging near enough
    #sort projectedlines 
    projectedlines = sorted([l for l in projectedlines
                             if verticalEnough(l)],
                            key=lambda line: line[0][0])
    #go throu left to right start collecting clusters
    clusters = [[projectedlines[0]]]
    for line in projectedlines[1:]:
        # compare it with first element of current cluster
        tocompare = clusters[-1][0]
        if nearenough(line,tocompare):
            clusters[-1].append(line) # add to existing cluster
        else:
            clusters.append([line]) # start new cluster
    return clusters
        
def cluster2middle(cluster,height):
    return ((sum([line[0][0] for line in cluster]),0),
           (sum([line[1][0] for line in cluster]),height))

def mergeLines(lines,height,width):
    #look at two lines
    #project endpoints of line to top and bottom of image
    #calculate distance
    #if < treshold, merge them and take a "middle" line as merged result
    #Do so until no lines can be merged farther
    #(may be possible to do in one pass .... ?!?)
    print("lines")
    print(lines)
    projectedlines = [project(l,height,width) for l in lines]
    print("projectedlines")
    print(projectedlines)
    cluster = merge(projectedlines,width)
    print("cluster")
    print(cluster)
    return map(lambda cluster: cluster2middle(cluster,height),cluster)

if __name__ == "__main__":
    filename = ""
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    

    for file in [f for f in os.listdir(filename) if isfile(join(filename,f))]:
        print(file)
        src = cv.LoadImage(join(filename,file), cv.CV_LOAD_IMAGE_GRAYSCALE)
        print("vor while")
        print("height")
        i = True
        while i == True:
            print("in while")
            i = False
            dst = cv.CreateImage(cv.GetSize(src), 8, 1)
            color_dst = cv.CreateImage(cv.GetSize(src), 8, 3)
            storage = cv.CreateMemStorage(0)
            lines = 0
            cv.Canny(src, dst, 50, 200, 3)
            cv.CvtColor(dst, color_dst, cv.CV_GRAY2BGR)
            print("vor test")
            if USE_STANDARD:
                print("use standard")
                lines = cv.HoughLines2(dst, storage, cv.CV_HOUGH_STANDARD, 1, pi / 180, 100, 0, 0)
                for (rho, theta) in lines[:100]:
                    a = cos(theta)
                    b = sin(theta)
                    x0 = a * rho
                    y0 = b * rho
                    pt1 = (cv.Round(x0 + 1000*(-b)), cv.Round(y0 + 1000*(a)))
                    pt2 = (cv.Round(x0 - 1000*(-b)), cv.Round(y0 - 1000*(a)))
                    cv.Line(color_dst, pt1, pt2, cv.RGB(255, 0, 0), 3, 8)
            else:
                print("not standard")
                lines = cv.HoughLines2(dst, storage, cv.CV_HOUGH_PROBABILISTIC, 1, pi / 180, 50, 50, 10)
                for line in mergeLines([l for l in  lines if verticalEnough(l)],src.height,src.width):
               # for line in [l for l in  lines if verticalEnough(l)]:
                    print("line")
                    print(line)
                    cv.Line(color_dst, line[0], line[1], cv.CV_RGB(255, 0, 0), 3, 8)
                print("hi")
                cv.SaveImage(join("/home/kima/output/",file), color_dst)

      
