import math 
# from math import atan2, degrees, radians, sqrt


def get_x(p):
    return p[0]


def get_y(p):
    return p[1]


def z(p):
    return p[3]


def add_pt(p, q):
    return ((p[0] + q[0]),  (p[1] + q[1]))

def add_scalar(p, s):
    return ((p[0] + s),  (p[1] + s))


def mid_pt(q, p):
    return (((p[0] + q[0]) / 2),  ((p[1] + q[1]) / 2))

def mid_ln (ln):
    """ mid point in a coordinate list"""
    if len(ln)==2:
        return mid_pt(ln[0],ln[1])
    else:
        return ln[len(ln)/2]

def mid_a_ln (ln):
    """ mid point in a coordinate list"""
    if len(ln)==2:
        return mid_pt(ln[0],ln[1]) , txtangle(ln[0],ln[1])
    else:
        return ln[len(ln)/2] ,  txtangle(ln[len(ln)/2],ln[1+len(ln)/2])

def ptscale(p, scale):
    return ((p[0] * scale), (p[1] * scale))

def distance(p, q):
    return math.sqrt(((p[0] - q[0]) * (p[0] - q[0])) + ((p[1] - q[1]) * (p[1] - q[1])))

def ln_length(ln):
    p = ln[0]
    l = 0.0
    for q in ln:
        l = l + distance(p, q)
        p = q
    return l

def ll_length(ln):
    p = ln[0]
    l = 0.0
    ll = []
    for q in ln:
        l = l + distance(p, q)
        ll.append(l)
        p = q
    return ll


def equal(p, q, tollerance=0.5):
    return distance(p, q) < tollerance


def angle(p, q):
    y = p[1] - q[1]
    x = p[0] - q[0]
    return math.degrees(math.atan2(y, x))


def txtangle(p1, p2):
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]
    if (x1 > x2):
        return angle(p1, p2)
    elif (x2 > x1):
        return angle(p2, p1)
    elif (y1 > y2):
        return angle(p1, p2)
    elif (y2 > y1):
        return angle(p2, p1)
    else:
        return 0
