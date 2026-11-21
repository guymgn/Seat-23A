"""
23A wing: the wing from the 23A plane window, as a real 3D object.

Same numbers as the wing drawn on the page (a 737-style planform, in metres).
Run inside Blender: Scripting tab > Open > Run Script. It adds a "23A Wing"
collection with the wing, three flap track fairings and a camera at the window seat.

Blender axes: +Y is the nose, +Z is up, the left wing extends toward -X.
"""
import math
import bpy
import bmesh
from mathutils import Vector

PURPLE = (0.486, 0.361, 1.0)

# ---- planform (metres). Prototype axes: x forward, y up, z out along the span ----
ZR, ZK, ZT = 1.88, 5.9, 17.0          # fuselage side, trailing-edge kink, tip


def xle(z): return -(z - ZR) * 0.52                                    # leading-edge sweep
def xte(z): return -6.19 if z < ZK else -6.19 - (z - ZK) * 0.2675      # trailing edge with kink
def ydi(z): return (z - ZR) * 0.105 + 0.55 * ((z - ZR) / (ZT - ZR)) ** 2   # dihedral plus in-flight flex


def yt(xc, tk):                        # NACA 4-digit half thickness, closed trailing edge
    return 5 * tk * (0.2969 * math.sqrt(xc) - 0.126 * xc - 0.3516 * xc ** 2 + 0.2843 * xc ** 3 - 0.1036 * xc ** 4)


def smoothstep(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def to_blender(x, y, z):
    return Vector((-z, x, y))


LOWER = 0.6                            # underside is flatter than the top
Z_BREAKS = [2.1, 5.75, 6.05, 6.3, 7.55, 8.8, 10.05, 11.3, 11.55, 11.85, 15.7]
C_BREAKS = [0.09, 0.58, 0.72, 0.73, 0.77]


def stations(lo, hi, n, breaks):
    vals = [lo + (hi - lo) * i / n for i in range(n + 1)] + [b for b in breaks if lo < b < hi]
    vals.sort()
    out = [vals[0]]
    for v in vals[1:]:
        if v - out[-1] > 0.02:
            out.append(v)
        elif v in breaks:              # keep the exact break so region edges stay crisp
            out[-1] = v
    out[-1] = hi
    return out


def chord_stations():
    n = 20
    vals = [(1 - math.cos(math.pi * j / n)) / 2 for j in range(n + 1)] + C_BREAKS
    vals.sort()
    out = [vals[0]]
    for v in vals[1:]:
        if v - out[-1] > 0.004:
            out.append(v)
        elif v in C_BREAKS:
            out[-1] = v
    out[-1] = 1.0
    return out


def region(z, xc, upper, winglet_t):
    """Material name for a face, matching the prototype's painted regions."""
    if winglet_t is not None:
        return "Livery" if winglet_t >= 0.38 else "Paint"
    if xc < 0.09:
        return "Leading edge"
    if xc > 0.73 and (2.1 <= z <= 5.75 or 6.05 <= z <= 11.55):
        return "Flap"
    if xc > 0.77 and 11.85 <= z <= 15.7:
        return "Aileron"
    if upper and 0.58 <= xc <= 0.72 and 6.3 <= z <= 11.3:
        return "Spoiler"
    return "Paint"


def material(name, color, metallic=0.0, roughness=0.4):
    mat = bpy.data.materials.get("23A " + name) or bpy.data.materials.new("23A " + name)
    mat.use_nodes = True
    bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1)
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
    mat.diffuse_color = (*color, 1)
    return mat


def grey(v): return (v, v, v)


def build_sections():
    """Wing stations from root to tip, then the blended winglet. Each: leading edge point,
    chord, surface normal (in the y,z plane), thickness ratio, span z and winglet parameter."""
    secs = []
    for z in stations(ZR, ZT, 48, Z_BREAKS):
        sp = (z - ZR) / (ZT - ZR)
        secs.append(dict(le=(xle(z), ydi(z), z), chord=xle(z) - xte(z), n=(1.0, 0.0), tk=0.13 - 0.035 * sp, z=z, t=None))
    ns, length = 26, 2.9
    dy = dz = 0.0
    for k in range(ns + 1):
        t = k / ns
        th = math.radians(80) * smoothstep(0, 0.34, t)
        if k > 0:
            secs.append(dict(le=(xle(ZT) - 2.05 * t ** 1.3, ydi(ZT) + dy, ZT + dz), chord=1.3 - 0.8 * t ** 0.9,
                             n=(math.cos(th), -math.sin(th)), tk=0.095 - 0.01 * t, z=ZT, t=t))
        dy += math.sin(th) * length / ns
        dz += math.cos(th) * length / ns
    return secs


def build_wing(collection):
    xs = chord_stations()
    m = len(xs) - 1
    bm = bmesh.new()
    rings = []
    for s in build_sections():
        lx, ly, lz = s["le"]
        c, (ny, nz) = s["chord"], s["n"]
        upper = [bm.verts.new(to_blender(lx - xc * c, ly + ny * yt(xc, s["tk"]) * c, lz + nz * yt(xc, s["tk"]) * c)) for xc in xs]
        lower = [bm.verts.new(to_blender(lx - xc * c, ly - ny * yt(xc, s["tk"]) * c * LOWER, lz - nz * yt(xc, s["tk"]) * c * LOWER))
                 for xc in xs[1:-1]]
        rings.append((s, upper, [upper[0]] + lower + [upper[-1]]))

    names = ["Paint", "Flap", "Aileron", "Spoiler", "Leading edge", "Livery"]
    for (sa, ua, la), (sb, ub, lb) in zip(rings, rings[1:]):
        zmid = (sa["z"] + sb["z"]) / 2
        t = None if sb["t"] is None else ((sa["t"] or 0) + sb["t"]) / 2
        for j in range(m):
            xc = (xs[j] + xs[j + 1]) / 2
            f = bm.faces.new((ua[j], ub[j], ub[j + 1], ua[j + 1]))
            f.material_index = names.index(region(zmid, xc, True, t))
            f = bm.faces.new((la[j + 1], lb[j + 1], lb[j], la[j]))
            f.material_index = names.index(region(zmid, xc, False, t))
    for _, up, lo in (rings[0], rings[-1]):       # root rib and winglet cap
        bm.faces.new(up + lo[-2:0:-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    for e in bm.edges:                            # keep the trailing edge and caps crisp
        if len(e.link_faces) == 2 and e.calc_face_angle(0) > math.radians(50):
            e.smooth = False

    mesh = bpy.data.meshes.new("23A Wing")
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(material("Paint", grey(0.885), roughness=0.38))
    mesh.materials.append(material("Flap", grey(0.80), roughness=0.42))
    mesh.materials.append(material("Aileron", grey(0.82), roughness=0.42))
    mesh.materials.append(material("Spoiler", grey(0.74), roughness=0.45))
    mesh.materials.append(material("Leading edge", grey(0.78), metallic=1.0, roughness=0.28))
    mesh.materials.append(material("Livery", PURPLE, roughness=0.35))
    obj = bpy.data.objects.new("Wing", mesh)
    collection.objects.link(obj)
    return obj


def build_fairing(collection, zf, index, parent):
    """Flap track fairing: a spindle slung under the wing, its tail behind the trailing edge."""
    a = Vector((xte(zf) + 1.6, ydi(zf) - 0.06, zf))
    b = Vector((xte(zf) - 0.78, ydi(zf) - 0.27, zf))
    axis = (b - a).normalized()
    side = Vector((0, 0, 1))
    up = axis.cross(side).normalized()
    rings_n, seg = 18, 14
    bm = bmesh.new()
    rings = []
    for k in range(rings_n + 1):
        t = k / rings_n
        r = max(0.17 * math.sin(math.pi * t) ** 0.6 * (1 - 0.4 * t), 0.004)
        c = a + (b - a) * t
        rings.append([bm.verts.new(to_blender(*(c + (up * math.cos(2 * math.pi * i / seg) + side * math.sin(2 * math.pi * i / seg)) * r)))
                      for i in range(seg)])
    for ra, rb in zip(rings, rings[1:]):
        for i in range(seg):
            bm.faces.new((ra[i], ra[(i + 1) % seg], rb[(i + 1) % seg], rb[i]))
    bm.faces.new(rings[0])
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    mesh = bpy.data.meshes.new(f"23A Fairing {index}")
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(material("Fairing", grey(0.80), roughness=0.4))
    obj = bpy.data.objects.new(f"Fairing {index}", mesh)
    collection.objects.link(obj)
    obj.parent = parent
    return obj


def build_camera(collection):
    """The window seat from the page: a little behind the trailing edge, looking out and 6 degrees forward."""
    cam = bpy.data.cameras.new("Seat camera")
    cam.sensor_fit = "VERTICAL"
    cam.sensor_height = 24
    cam.lens = 0.75 * 24               # the page's focal length of 0.75 screen heights
    cam.shift_y = -0.03                # the page puts the horizon at 53 percent, not the centre
    cam.clip_start, cam.clip_end = 0.05, 500
    obj = bpy.data.objects.new("Seat camera", cam)
    obj.location = to_blender(-7.35, 1.28, 1.8)
    yaw = math.radians(6)
    look = to_blender(math.sin(yaw), 0, math.cos(yaw))
    obj.rotation_euler = look.to_track_quat("-Z", "Y").to_euler()
    collection.objects.link(obj)
    return obj


def build():
    collection = bpy.data.collections.new("23A Wing")
    bpy.context.scene.collection.children.link(collection)
    wing = build_wing(collection)
    for i, zf in enumerate((3.7, 7.3, 10.7), start=1):
        build_fairing(collection, zf, i, wing)
    camera = build_camera(collection)
    return wing, camera


if __name__ == "__main__":
    build()
