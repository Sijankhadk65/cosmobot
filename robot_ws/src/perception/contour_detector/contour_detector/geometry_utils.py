import cv2
import numpy as np
import math

def get_distance(p1, p2):
    """Euclidean distance between two points."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def is_dot(contour, circularity_threshold=0.6, min_area=10):
    """Detects if a contour is a dot using circularity."""
    area = cv2.contourArea(contour)
    if area < min_area:
        return True # Tiny blobs are often dots
    
    perimeter = cv2.arcLength(contour, True)
    if perimeter == 0:
        return False
        
    circularity = (4 * math.pi * area) / (perimeter**2)
    return circularity > circularity_threshold

def is_line(contour, tolerance=0.90):
    """
    Detects if a contour is a line using the distance formula ratio.
    """
    if len(contour) < 2:
        return False
        
    # Get endpoints (farthest points for better accuracy in lines)
    # Using the first and last point is okay for simple lines
    p_start = contour[0][0]
    p_end = contour[-1][0]
    
    euclidean_dist = get_distance(p_start, p_end)
    arc_length = cv2.arcLength(contour, False)
    
    if arc_length == 0:
        return False
        
    ratio = euclidean_dist / arc_length
    return ratio > tolerance

def is_curve(contour, tangent_threshold=0.5):
    """
    Detects if a contour is a curve using the tangent formula approach.
    Increased threshold to avoid noisy lines being caught.
    """
    if len(contour) < 3:
        return False
        
    # Approximate the contour
    epsilon = 0.02 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    
    if len(approx) < 3:
        return False
        
    angles = []
    for i in range(1, len(approx) - 1):
        p1 = approx[i-1][0]
        p2 = approx[i][0]
        p3 = approx[i+1][0]
        
        v1 = (p2[0] - p1[0], p2[1] - p1[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        
        mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
        mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
        
        if mag1 == 0 or mag2 == 0: continue
        
        # Dot product for angle
        dot = (v1[0]*v2[0] + v1[1]*v2[1]) / (mag1 * mag2)
        dot = max(-1.0, min(1.0, dot))
        angle = math.acos(dot)
        angles.append(angle)
        
    if not angles:
        return False
        
    avg_change = sum(angles) / len(angles)
    return avg_change > tangent_threshold

def classify_contour(contour):
    """Classifies a contour as a dot, line, or curve in order of specificity."""
    if is_dot(contour):
        return "dot"
        
    if is_line(contour):
        return "line"
    
    if is_curve(contour):
        return "curve"
        
    return "unknown"
