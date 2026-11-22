# Seat 23A

The view from the window seat, live.

**Try it live: [guymagen.com/23a](https://www.guymagen.com/23a)**

[![The Seat 23A window in four skies: day, sunset, night and northern lights](four-skies.png)](https://www.guymagen.com/23a)

## Four skies

- **Day.** Sun on the wing, a white cloud deck below.
- **Sunset.** A thin orange band on the horizon and the wing going dark against it.
- **Night.** Stars, the moon in its real phase, city lights through the gaps in the cloud.
- **Northern lights.** Green curtains over Finland, Iceland and Norway, after dark.

One of my favorite moments on a flight is looking out of the window at the wing above the clouds. It is the moment the trip starts to feel real.

I'm working on a new onboarding for [Teara](https://teara.io), my travel app, and I wanted the first screen to do more than explain what the app does. I wanted it to bring back exactly that feeling. Seat 23A is that screen, on its own page.

## What you are looking at

The view from a window seat just behind the wing, rendered live in the browser. The sky follows the real position of the sun for where you are, so it is day when your day is and the light turns orange when your own sun goes down. At night you get stars, city lights through the gaps in the cloud, the moon in its actual phase and the odd flash of distant lightning.

Nothing in it is a photo or a video. The clouds are a volume the camera flies over, the wing is lit by the same sun as the sky, and every so often the plane passes through a bank of cloud. Swipe down on the window to close the blind.

When you choose a home airport, the sun in the window moves to match your place in the world, so the view feels like your flight.

## How it works

- **Sky and clouds.** One fragment shader. The clouds are a raymarched slab with self-shadowing, and the sky colours are keyed to the sun's elevation.
- **Day and night.** The sun's position is computed from the clock and a location. It starts from an estimate based on your time zone, and you can pick any of 126 cities or use your actual location. Picking a place shows the sky there right now, in its local time, and the view crossfades to it. The moon's phase is computed from the date.
- **Northern lights.** Choose somewhere in Finland, Iceland or Norway and wait for dark.
- **Wing.** A 737-style wing with real proportions (sweep, trailing-edge kink, dihedral, an airfoil section and a blended winglet), lit in the shader. It is also here as a 3D model: `wing.blend` and `wing.glb`.
- **Blind.** A spring that keeps the speed of your swipe.
- **Power.** The scene draws at 30 frames a second and stops when it is off screen or the blind is closed. The tab you are watching keeps running. It pauses 15 seconds after you switch to another window or app, and after 5 minutes without input, until you move or tap. With cabin sound on it keeps going.
- **Cabin sound.** Off until you turn it on. The live page plays a recorded cabin ambience, [Airplane atmos](https://pixabay.com/sound-effects/technology-airplane-atmos-22955/) from Pixabay, looped with the seam blended away. That recording is under the Pixabay Content License, not MIT, so it is not in this repo. Without it the page generates its own cabin rumble, and you can drop any `cabin.mp3` next to `index.html` to use a recording instead. The chimes are generated either way.

The controls under the window let you change location, scrub the time of day, play a full 24 hours, change the cloud cover, fly through a cloud on demand and turn on the cabin sound.

## Credit

Created by [Guy Magen](https://www.guymagen.com). Built with Claude.

## License

MIT. See `LICENSE`.
