# Composite Page — AI Art Brief
## How to replace the SVG figure with a proper illustration

---

## The goal
Replace the hand-coded SVG figure with a high-quality illustration while keeping
all the interactive click zones, WCS filter, and data panels exactly as they are.
The illustration becomes the background; the zones are invisible overlays on top.

---

## AI image prompt

### Midjourney (best result)
```
forensic police composite sketch of a bipedal wolf creature, full body, 
front-facing, standing upright, arms slightly away from body, 
German Shepherd head with large upright pointed ears, elongated wolf snout, 
forward-set predator eyes with visible iris, two large canine teeth visible 
below upper lip, massive muscular shoulders, long arms proportionally longer 
than human, raccoon-like hands with elongated fingers and curved claws, 
digitigrade leg stance with raised heel, dark dense fur, 
pencil on cream paper, no shading, clean line art only, 
forensic anatomical diagram style, white background, 
no color, no texture fill, cross-hatching only for shadow, 
full body visible head to feet, neutral threatening stance, 
--ar 1:2 --style raw --v 6
```

### DALL-E 3
```
A forensic composite sketch in the style of a police artist's pencil drawing. 
Subject: a bipedal wolf-headed creature standing upright facing forward, 
full body from head to feet. Features: large German Shepherd-type upright 
pointed ears, elongated wolf muzzle with two visible canine teeth, 
forward-facing predator eyes, massively broad shoulders, 
long arms hanging slightly forward, elongated raccoon-like hands with claws, 
digitigrade lower legs. Style: pencil line art on white paper, 
no fills, no shading, clean contour lines only, 
clinical forensic illustration, anatomical diagram aesthetic.
```

### Stable Diffusion (img2img from current SVG screenshot)
Use the current screenshot as init image at strength 0.65 with prompt:
```
forensic pencil sketch, police composite drawing, bipedal wolf creature, 
front view, full body, clean line art, white paper background, 
no shading, anatomical diagram style
```

---

## What to ask for specifically

**Tell the AI explicitly:**
- Full body, head to feet, nothing cropped
- Front-facing / straight on (not 3/4, not profile)
- White or very light cream background (no environment, no scene)
- No shading fills — pencil line art only, or sparse cross-hatching
- Proportions: head is ~1/7 of total height (not 1/4)
- Arms noticeably longer than human proportion
- Digitigrade legs (heel raised, weight on ball of foot)
- Two large canine teeth visible below upper lip — not a full snarl

**Key things to avoid:**
- Dramatic lighting / dark background
- Artistic flourishes (claw marks, blood, etc.)
- A snarling open-mouth expression (closed or slightly parted only)
- Quadrupedal pose
- Humanoid proportions (too skinny, too human-shaped)

---

## How to embed in composite.html

Once you have the image (PNG or SVG export):

### Step 1 — Add the image to the repo
Save it as `docs/composite-figure.png` (or `.svg`)

### Step 2 — Replace the pencil-sketch SVG group

Inside `composite.html`, find:
```html
<g transform="translate(50,0)">
```

Replace the entire pencil figure group contents with:
```html
<g transform="translate(50,0)">
  <!-- AI illustration as base layer -->
  <image 
    href="composite-figure.png" 
    x="-10" y="-10" 
    width="290" height="510"
    preserveAspectRatio="xMidYMid meet"
    opacity="0.92"
  />
```

Then keep all the zone overlays exactly as they are — they sit on top of the image.

### Step 3 — Calibrate the zone positions

After embedding, open the page and click each zone button to check the
highlight lands in the right place. Adjust the zone overlay coordinates
(the `cx/cy/rx/ry` or `x/y/width/height` attributes) to match
where the body parts actually are in the illustration.

The zone overlays are all inside the same `translate(50,0)` group,
so you only need to adjust their individual positions, not the overall offset.

### Step 4 — Remove the now-redundant pencil filter

You can remove the `<filter id="pencil">` definition from the SVG `<defs>`
since the image handles its own texture.

---

## Coordinate reference (current zone positions, pre-translate)

These are the zone overlay positions in the SVG coordinate system
*before* the translate(50,0) is applied. When calibrating after the art swap,
use these as your starting reference and nudge from there.

| Zone | Shape | Position |
|------|-------|----------|
| HEAD | ellipse | cx=140 cy=84 rx=52 ry=58 |
| EYES | ellipse | cx=140 cy=67 rx=36 ry=16 |
| TEETH | rect | x=116 y=98 w=68 h=52 |
| LEFT EAR | ellipse | cx=108 cy=22 rx=18 ry=30 |
| RIGHT EAR | ellipse | cx=172 cy=20 rx=18 ry=30 |
| TORSO | rect | x=62 y=134 w=156 h=168 |
| LEFT ARM | rect (rotated) | x=10 y=144 w=52 h=180 rotate(-7) |
| RIGHT ARM | rect (rotated) | x=218 y=144 w=52 h=180 rotate(7) |
| LEFT HAND | rect | x=4 y=306 w=46 h=62 |
| RIGHT HAND | rect | x=230 y=306 w=46 h=62 |
| LEGS | rect | x=60 y=332 w=160 h=162 |

---

## If you want a sketch feel without full AI generation

Ask an illustrator on Fiverr or ArtStation for:
> "Forensic composite sketch of a bipedal wolf creature. 
> Pencil on paper, clean line art, front-facing, full body.  
> Police sketch style — clinical, not artistic. No background.
> Deliver as SVG or high-res PNG with transparent background."

Budget: $50–150 depending on detail level.
Search: "forensic illustration" or "creature concept art" on ArtStation.

---

*Brief prepared by Jonek — Kryptovox project*
