# coding: utf-8

import numpy as np

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

import title

sys.path.insert(0, os.path.join(sys.path[0], '..'))
from jhm.vector import Vector
from jhm.quaternion import Quaternion
import viewer.quaternion as qt
sys.path.pop()

SCALING, TRANSLATING, ROTATING = range(3)
camera = None
data = None

def is_pressed(flag):
  m = glutGetModifiers()
  return bool(m & flag)

def shift_pressed():
  return is_pressed(GLUT_ACTIVE_SHIFT)

def ctrl_pressed():
  return is_pressed(GLUT_ACTIVE_CTRL)

def alt_pressed():
  return is_pressed(GLUT_ACTIVE_ALT)

class Drag:
  def __init__(self):
    self.ing = False
  def begin(self, point):
    self.ing = True
    self.source = point
  def move(self, point):
    self.target = point
  def end(self):
    self.ing = False
drag = Drag()

def keyboard(ch, x, y):
  if alt_pressed():
    camera.keyboard(ch, x, y)

def mouse(button, state, x, y):
  if state == GLUT_DOWN:
    drag.alt = alt_pressed()
    if drag.alt:
      camera.mouse(button, state, x, y)
      return
    drag.begin(np.array([x, y]))
    pick_point()
  elif state == GLUT_UP:
    if drag.alt:
      camera.mouse(button, state, x, y)
      return
    drag.end()

def motion(x, y):
  if drag.alt:
    camera.motion(x, y)
    return
  if not drag.ing:
    return
  drag.move(np.array([x, y]))
  move_point()

def display():
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
  glMatrixMode(GL_MODELVIEW)

  for i in xrange(data.n):
    glPushMatrix()
    glTranslate(data.positions[i][0],
                data.positions[i][1],
                data.positions[i][2])
    glRotate(data.rotations[i][0] * 180.0 / np.pi,
             data.rotations[i][1],
             data.rotations[i][2],
             data.rotations[i][3])
    glScale(data.scales[i],
            1.0,
            data.scales[i])
    glColor(1.0, 1.0, 1.0)
    glBegin(GL_POLYGON)
    for p in data.points[i]:
      glVertex(p[0], 0.0, p[1])
    glEnd()
    if not drag.ing or i != drag.picked_i:
      glColor(0.5, 0.5, 1.0)
      glBegin(GL_POINTS)
      glVertex(0.0, 0.0, 0.0)
      glEnd()
    glPopMatrix()

def pick_point():
  if ctrl_pressed():
    drag.method = SCALING
  elif shift_pressed():
    drag.method = TRANSLATING
  else:
    drag.method = ROTATING

  drag.picked_i = None

  closest = np.inf
  n_point = camera._nearplane_point(drag.source, False)
  v = n_point - camera.pos
  v /= np.sqrt(v.dot(v))
  for i in xrange(len(data.positions)):
    l = np.array(data.positions[i]) - camera.pos
    ll = l.dot(l)
    t = l.dot(v)
    dd = ll - t * t
    if dd < closest:
      closest = dd
      drag.picked_i = i

  if drag.method == SCALING:
    drag.picked_scale = data.scales[drag.picked_i]
  elif drag.method == TRANSLATING:
    drag.picked_position = data.positions[drag.picked_i]
  else: # drag.method == ROTATING
    drag.picked_rotation = data.rotations[drag.picked_i]

def move_point():
  if drag.picked_i is None:
    return

  if drag.method == SCALING:
    diff = drag.target[1] - drag.source[1]
    mag = 10.0 ** diff
    data.scales[drag.picked_i] = drag.picked_scale * mag
  elif drag.method == TRANSLATING:
    v = drag.picked_position - camera.pos
    l = np.sqrt(v.dot(v))
    w = camera._nearplane_point(drag.target, False) - camera.pos
    w /= np.sqrt(w.dot(w))
    w *= l
    data.positions[drag.picked_i] = camera.pos + w
  else: # drag.method == ROTATING
    a = camera._nearplane_point(drag.target, False) - camera.pos
    b = camera._nearplane_point(drag.source, False) - camera.pos
    q = qt.from_two_vectors(a, b)
    o = Quaternion.pow(Vector.from_list(drag.picked_rotation[1:]), drag.picked_rotation[0])
    v = Quaternion.ln(q * o)
    data.rotations[drag.picked_i] = [v.length()] + v.normalize().to_list()

def refresh_title():
  title.change('Transforming')

def start():
  glDisable(GL_LIGHTING)
  glClearColor(0.0, 0.0, 0.0, 0.0)
  glPolygonMode(GL_FRONT, GL_FILL)
  glPolygonMode(GL_BACK, GL_LINE)

  camera.see()
  refresh_title()

