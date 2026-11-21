# 23A

The view from the window seat, live.

![The 23A window at golden hour](preview.png)

23A is the view from a window seat just behind the wing, rendered live in the browser. The sky follows the real position of the sun for where you are, so it is day when your day is and the light turns orange when your own sun goes down. At night you get stars, city lights through the gaps in the cloud, the moon in its actual phase and the odd flash of distant lightning.

Nothing in it is a photo or a video. The clouds are a volume the camera flies over, the wing is built from real geometry and lit by the same sun as the sky, and every so often the plane passes through a bank of cloud. Swipe down on the window to close the blind.

I made it for the onboarding of [Teara](https://teara.io), my travel app.

## What is here

| File | What it is |
| --- | --- |
| `index.html` | The whole thing. One self-contained page, no build step and no dependencies. Open it in any browser with WebGL |
| `wing.blend` | The wing as a Blender scene, with a camera at the window seat |
| `wing.glb` | The same wing as glTF |
| `wing.py` | The Blender script that builds the wing from the same numbers the page uses |

## How it works

- **Sky and clouds.** One fragment shader. The clouds are a raymarched slab with self-shadowing, and the sky colours are keyed to the sun's elevation.
- **Day and night.** The sun's position is computed from your clock and a location estimated from your time zone. "Use precise" asks the browser for your actual location. The moon's phase is computed from the date.
- **Wing.** A 737-style planform defined in metres (sweep, trailing-edge kink, dihedral, an airfoil section and a blended winglet), projected through the scene camera and lit in the shader.
- **Blind.** A spring that keeps the speed of your swipe.

The controls under the window let you scrub the time of day, play a full 24 hours, change the cloud cover and fly through a cloud on demand.

## Credit

Created by [Guy Magen](https://www.guymagen.com). Built with Claude.

## License

MIT. See `LICENSE`.
