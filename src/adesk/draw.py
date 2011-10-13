# -*- coding: utf-8 -*-

import cairo
import math

def to_cr(cr, fill=False):
    if fill:
        cr.fill()
    else:
        cr.stroke()
    cr.restore()

def simple_rect(cr, rect, fill=False):
    cr.save()
    cr.rectangle(rect[0], rect[1], rect[2], rect[3])
    to_cr(cr, fill)

def rounded_rect(cr, rect, radius, position, fill=False):

    if radius == 0:
        simple_rect(cr, rect, fill=fill)
        return

    x, y, width, height = rect[0], rect[1], rect[2], rect[3]

    rotate_cr(cr, x, y, width, height, position)
    radius = radius/100.0 * min(width//2, height//2)

    if position == "left" or position == "right":
         width, height = height, width

    cr.move_to  (0, radius)
    cr.arc (radius, radius, radius, 3.14, 1.5 * 3.14)
    cr.line_to (width - radius, 0)
    cr.arc (width - radius, 0 + radius, radius, 1.5 * 3.14, 0.0)
    cr.line_to (width , height - radius)
    cr.arc (width - radius, height - radius, radius, 0.0, 0.5 * 3.14)
    cr.line_to (radius, height)
    cr.arc (radius, height - radius, radius, 0.5 * 3.14, 3.14)
    cr.close_path ()

    to_cr(cr, fill)

def rounded_rect2(cr, rect, radius, position, fill=False):

    if radius == 0:
        simple_rect(cr, rect, fill=fill)
        return

    x, y, width, height = rect[0], rect[1], rect[2], rect[3]

    rotate_cr(cr, x, y, width, height, position)
    radius = radius/100.0 * min(width//2, height//2)

    if position == "left" or position == "right":
         width, height = height, width

    cr.move_to  (0, radius)
    cr.arc (radius, radius, radius, math.pi, 1.5 * 3.14)
    cr.line_to (width - radius, 0)
    cr.arc (width - radius, 0 + radius, radius, 1.5 * math.pi, 0.0)
    cr.line_to (width , height)
    cr.line_to (0, height)
    cr.close_path ()

    to_cr(cr, fill)

def trapeze(cr, rect, angle, position, fill=False):
    x, y, width, height = rect[0], rect[1], rect[2], rect[3]
    
    ## max angle
    angle = 80 * angle//100

    rotate_cr(cr, x, y, width, height, position)
    if position == "left" or position == "right":
         width, height = height, width
    ba = height//math.tan(math.radians(90 - angle))

    cr.move_to(ba,0)
    cr.line_to(width-ba,0)
    cr.line_to(width,height)
    cr.line_to(0,height)
    cr.line_to(ba,0)

    to_cr(cr, fill)

def line(cr, rect, position, cfg, fill=False):
    x, y, width, height = rect[0], rect[1], rect[2], rect[3]

    rotate_cr(cr, x, y, width, height, position)
    if position == "left" or position == "right":
         width, height = height, width

    pos = cfg['offset_side']
    size = cfg['icon_size']
    space = cfg['icon_space']
    offset = space // 2

    cr.move_to(0, height - 2)
    cr.line_to(pos - space, height - 2)

    pos -= space

    for ind in range(len(cfg['Launcher'])):
        cr.line_to(pos + offset -1, height - 2)
        cr.line_to(pos + offset -1, 0)
        cr.line_to(pos + offset +1, 0)
        cr.line_to(pos + offset +1, height - 2)
        cr.line_to(pos + size , height - 2)
        cr.line_to(pos + size + space , height - 2)
        pos += size + space

    cr.line_to(width, height - 2)
    cr.line_to(width, height)
    cr.line_to(0, height)
    cr.line_to(0, height - 2)

    to_cr(cr, fill)

def rotate_cr(cr, x, y, width, height, position):
    cr.save()
    if position == "bottom":
        cr.translate(x, y)
    elif position == "top":
        cr.translate(x+width, y+height)
        cr.rotate(math.pi)
    elif position == "left":
        cr.translate(x+width, y)
        cr.rotate(math.pi/2.0)
    elif position == "right":
        cr.translate(x, y+height)
        cr.rotate(-math.pi/2.0)

def create_gradient(r, g, b, rect, opacity, position):
    x, y, width, height = rect[0], rect[1], rect[2], rect[3]

    if position=='bottom':
        lg = cairo.LinearGradient(0, y, 0, y+height)
    elif position=='top':
        lg = cairo.LinearGradient(0, 0, 0, height)
    elif position=='left':
        lg = cairo.LinearGradient(0, 0, width, 0)
    elif position=='right':
        lg = cairo.LinearGradient(x, 0, x+width, 0)

    i = 0.3
    while i >= 0:

        lg.add_color_stop_rgba(1-i, r-(i*r), g-(i*g), b-(i*b), opacity)
        i -= 0.05
    i = 0.7
    while i <= 1.0:
        lg.add_color_stop_rgba(1-i, r-(1-i)*r, g-(1-i)*g, b-(1-i)*b, opacity)
        i += 0.05
    return lg

def gradient_color2trans(r, g, b, rect, opacity, position, invert=False):
    x, y, width, height = rect[0], rect[1], rect[2], rect[3]

    if invert:
        if position=='bottom':
            lg = cairo.LinearGradient(0, y, 0, y+height)
        elif position=='top':
            lg = cairo.LinearGradient(0, y+height, 0, y)
        elif position=='left':
            lg = cairo.LinearGradient(x+width, 0, x, 0)
        elif position=='right':
            lg = cairo.LinearGradient(x, 0, x+width, 0)
    else:
        if position=='bottom':
            lg = cairo.LinearGradient(0, y+height, 0, y)
        elif position=='top':
            lg = cairo.LinearGradient(0, y, 0, y+height)
        elif position=='left':
            lg = cairo.LinearGradient(x, 0, x+width, 0)
        elif position=='right':
            lg = cairo.LinearGradient(width, 0, 0, 0)


    i = 1
    while i >= 0.2:

        lg.add_color_stop_rgba(i, r, g, b, opacity*i)
        i -= 0.02
           
    return lg
