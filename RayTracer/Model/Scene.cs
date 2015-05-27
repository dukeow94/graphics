﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Media.Media3D;

namespace Gyumin.Graphics.RayTracer.Model
{
    using Material;
    using MathUtil;

    public class Scene
    {
        private Color backgroundColor = Colors.Black;

        private List<Light> lights = new List<Light>();

        private List<Renderable> objects = new List<Renderable>();

        private Camera camera = new Camera();

        public Scene()
        {
        }

        private Renderable FirstMeet(Ray ray, out Point3D at)
        {
            at = new Point3D();
            var found = this.objects.Select(renderable =>
            {
                var intersection = new Point3D();
                var intersects = renderable.Intersects(ray, out intersection);
                return new { Renderable = renderable, Intersects = intersects, Intersection = intersection };
            })
            .Where(result => result.Intersects)
            .OrderBy(result => (result.Intersection - ray.Position).Length)
            .FirstOrDefault();
            if (found == null)
                return null;
            at = found.Intersection;
            return found.Renderable;
        }

        private Color Trace(Ray ray)
        {
            var at = new Point3D();
            var renderable = this.FirstMeet(ray, out at);
            if (renderable == null)
                return this.backgroundColor;

            var color = Colors.Black;

            var k_a = renderable.Material.Ambient;
            var k_d = renderable.Material.Diffuse;
            var k_s = renderable.Material.Specular;
            var n = renderable.Material.Shininess;

            var normal = renderable.NormalAt(at);

            foreach (var light in this.lights)
            {
                color = Color.Add(color,
                    ColorUtil.ElementWiseMultiply(k_a, light.Ambient));

                var to_light = light.RayFrom(at);
                var cos_t = Vector3D.DotProduct(normal, to_light.Direction);
                if (cos_t > Geometry.Epsilon)
                {
                    var unused = new Point3D();
                    if (this.FirstMeet(to_light, out unused) == null)
                    {
                        color = Color.Add(color,
                            Color.Multiply(
                                ColorUtil.ElementWiseMultiply(k_d, light.IntensityAt(at)),
                                (float)cos_t));

                        var reflected = Vector3D.DotProduct(2 * to_light.Direction, normal) * normal - to_light.Direction;
                        color = Color.Add(color,
                            Color.Multiply(
                                ColorUtil.ElementWiseMultiply(k_s, light.IntensityAt(at)),
                                (float)Math.Pow(Vector3D.DotProduct(reflected, -ray.Direction), n)));
                    }
                }
            }

            return color;
        }

        public Color Trace(double x, double y)
        {
            var ray = this.camera.GetRayToScreen(x, y);
            return this.Trace(ray);
        }

        public void AddLight(Light light)
        {
            this.lights.Add(light);
        }

        public void AddObject(Renderable renderable)
        {
            this.objects.Add(renderable);
        }
    }
}
