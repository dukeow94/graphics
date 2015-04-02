# coding: utf-8

import numpy as np

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

X, Y, Z = 0, 1, 2
IN, OUT = False, True

def is_pressed(flag):
  m = glutGetModifiers()
  return bool(m & flag)

def shift_pressed():
  return is_pressed(GLUT_ACTIVE_SHIFT)

def ctrl_pressed():
  return is_pressed(GLUT_ACTIVE_CTRL)

def rotation_matrix(axis, sin, cos):
    x, y, z = axis[X], axis[Y], axis[Z]
    ncos = 1.0 - cos
    return np.array([
      [x * x * ncos + cos,     x * y * ncos - z * sin, z * x * ncos + y * sin],
      [x * y * ncos + z * sin, y * y * ncos + cos,     y * z * ncos - x * sin],
      [z * x * ncos - y * sin, y * z * ncos + x * sin, z * z * ncos + cos    ],
    ])

class Camera:

  def __init__(self):
    self.pos = np.array([0.0, 0.0, 3.0])
    self.ref = np.array([0.0, 0.0, 0.0])
    self.up = np.array([0.0, 1.0, 0.0])
    self.theta = 90.0
    self.aspect = 1.0
    self.near = 1.0
    self.far = 30.0

  def _look_at(self):
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(
      self.pos[X], self.pos[Y], self.pos[Z],
      self.ref[X], self.ref[Y], self.ref[Z],
      self.up[X], self.up[Y], self.up[Z]
    )

  def _perspective(self):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(
      self.theta, self.aspect,
      self.near, self.far
    )

  def init(self):
    self._look_at()
    self._perspective()

  def doly(self, out):
    speed = -0.1
    if out:
      speed = -speed
    v = self.pos - self.ref
    distance = np.sqrt(v.dot(v))
    if speed < 0 and distance + speed <= self.near \
      or speed > 0 and distance + speed >= self.far:
      return
    v *= speed / distance
    self.pos += v
    self._look_at()
    glutPostRedisplay()

  def zoom(self, out):
    speed = -1.0
    if out:
      speed = -speed
    if speed < 0 and self.theta + speed < 1.0 \
      or speed > 0 and self.theta + speed >= 180.0:
      return
    self.theta += speed
    self._perspective()
    glutPostRedisplay()

  def _get_nuv(self):
    n = self.prev_pos - self.prev_ref
    n /= np.sqrt(n.dot(n))
    u = np.cross(self.up, n) / np.sqrt(self.up.dot(self.up))
    v = np.cross(n, u)
    return n, u, v

  def _get_nearplane_half_size(self):
    height = np.arctan(self.theta / 2.0) * self.near
    width = height * self.aspect
    return np.array([width, height])

  def _nearplane_point(self, point):
    size = self._get_nearplane_half_size()
    point *= size
    n, u, v = self._get_nuv()
    o = self.prev_pos - self.near * n
    du = point[X] * u
    dv = point[Y] * v
    return o + du + dv

  def translate_start(self, source):
    self.prev_pos = self.pos
    self.prev_ref = self.ref
    self.n_source = self._nearplane_point(source)

  def translate(self, target):
    n_target = self._nearplane_point(target)
    displacement = n_target - self.n_source

    self.pos = self.prev_pos - displacement
    self.ref = self.prev_ref - displacement

    self._look_at()
    glutPostRedisplay()

  def _trackball_point(self, point):
    n_point = self._nearplane_point(point)

    v = n_point - self.prev_pos
    v /= np.sqrt(v.dot(v))

    l = self.prev_ref - self.prev_pos
    t = l.dot(v)
    dd = l.dot(l) - t * t

    r = np.sqrt(l.dot(l)) - self.near
    rr = r * r

    if dd > rr:
      q = self.prev_pos + t * v
      d = np.sqrt(dd)
      p = ((d - r) * self.prev_ref + r * q) / d
    else: # intersects
      dt = np.sqrt(rr - dd)
      t -= dt
      p = self.prev_pos + t * v

    return p

  def rotate_start(self, source):
    self.prev_pos = self.pos
    self.prev_ref = self.ref
    self.t_source = self._trackball_point(source)

  def rotate(self, target):
    s = self.t_source - self.prev_ref
    e = self._trackball_point(target) - self.prev_ref

    axis = np.cross(s, e)
    se_cos = s.dot(e)
    se_sin = np.sqrt(axis.dot(axis))

    axis /= se_sin

    se = np.sqrt(s.dot(s)) * np.sqrt(e.dot(e))
    cos = se_cos / se
    sin = se_sin / se

    rot = rotation_matrix(axis, sin, cos)
    rot = np.linalg.inv(rot)

    self.pos = rot.dot(self.prev_pos - self.prev_ref) + self.prev_ref

    self._look_at()
    glutPostRedisplay()

  def keyboard(self, ch, x, y):
    if ch == 'w':
      self.doly(IN)
    elif ch == 's':
      self.doly(OUT)
    elif ch == 'd':
      self.zoom(IN)
    elif ch == 'a':
      self.zoom(OUT)
    else:
      pass

  def mouse(self, button, state, x, y):
    if state == GLUT_DOWN:
      source = np.array([x, y])
      if ctrl_pressed():
        pass
      elif shift_pressed():
        self.method = 'translate'
        self.translate_start(source)
      else:
        self.method = 'rotate'
        self.rotate_start(source)
    elif state == GLUT_UP:
      self.method = None
    else:
      pass

  def motion(self, x, y):
    target = np.array([x, y])
    if self.method == 'translate':
      self.translate(target)
    elif self.method == 'rotate':
      self.rotate(target)
    else:
      pass

