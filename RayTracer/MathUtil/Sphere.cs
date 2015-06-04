﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Media.Media3D;

namespace Gyumin.Graphics.RayTracer.MathUtil
{
    public class Sphere
    {
        public Point3D Center { get; private set; }

        public double Radius { get; private set; }

        public double Radius2 { get; private set; }

        public Sphere(Point3D center, double radius)
        {
            this.Center = center;
            this.Radius = radius;
            this.Radius2 = radius * radius;
        }

        public Vector3D NormalAt(Point3D point)
        {
            var normal = point - this.Center;
            normal.Normalize();
            return normal;
        }

        private int count = 0;

        public void Move()
        {
            var center = this.Center;
            center.X -= 0.03 / (++this.count);
            this.Center = center;
        }
    }
}
