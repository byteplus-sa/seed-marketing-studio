# Product-Shot Presets

Focused reference for `seedream-product-shot`. Load only the preset you need.
Read [the entrypoint](../SKILL.md) first for routes, inputs and QA.

Placeholders in square brackets come from the approved product descriptor, the
brand kit or the brief. `[product descriptor]` is the approved descriptor copied
word for word. Every preset shares this References block and Constraints tail:

```text
References:
@Image 1: approved product reference — shape, proportions, materials, colors, label layout

Constraints (shared tail):
Use the exact shape, proportions, materials, colors and label layout of the product in @Image 1. One product only. No added text, letters, numbers or logos beyond the product's own label, no watermark, no duplicate products, no cropped product edges.
```

For a **plate** (plate + composite route), replace the Subject with the plate
Subject shown in the preset, drop `@Image 1` from the shape binding and keep it
only as a scale and light reference: "Use @Image 1 only for the product's size
and the light direction; do not draw the product."

- [studio-white](#studio-white)
- [color-pop](#color-pop)
- [editorial](#editorial)
- [macro-detail](#macro-detail)
- [in-use](#in-use)
- [faceless-hands](#faceless-hands)
- [flat-lay](#flat-lay)
- [lifestyle](#lifestyle)
- [hero-plinth](#hero-plinth)
- [marketplace-dark](#marketplace-dark)
- [marketplace-pastel](#marketplace-pastel)
- [marketplace-surreal-3d](#marketplace-surreal-3d)

## studio-white

Marketplace main image and catalog. Prefer the no-generation composite of an
authorized alpha packshot on `#FFFFFF`. Generate only when no clean packshot
exists, and then only when the label need not be read.

```text
Task: Image-to-Image (I2I)
Subject: [product descriptor], front three-quarter view, the whole product upright and centered.
Setting: Isolated on a pure white seamless background, one flat even field of pure white with no floor line, no gradient and no vignette.
Style: Photorealistic e-commerce packshot, true material texture, accurate color.
Lighting: Soft, even, shadowless high-key studio light, neutral white balance, controlled highlights on [gloss/metal/glass].
Composition: The product fills most of the frame with an even margin on every side, nothing touching the edges, deep focus across the product.
Constraints: shared tail; no props, no hands, no reflections of other objects, no contact shadow band.
```

QA extra: white-background check with the target marketplace's tolerance.
Shadows, reflections and fill share follow that marketplace's current rules.

## color-pop

Brand-color seamless with crisp light; reads at feed thumbnail size.

```text
Task: Image-to-Image (I2I)
Subject (plate): An empty smooth surface seamlessly continuous with the backdrop, the center left clear for one product about [size in frame] tall; a crisp contact shadow area falling to the [left/right].
Subject (generated): [product descriptor], standing upright, slightly turned toward the light.
Setting: A saturated [color name] seamless backdrop and floor, hex [#RRGGBB from the brand kit], one continuous color field.
Style: Bold commercial product photography, clean graphic shapes, [brand imagery sentence].
Lighting: One hard key light from [upper left], a defined shadow cast to the [right], gentle fill so the product's own colors stay true.
Composition: Product centered in the lower two thirds, [upper third left clear for copy], generous margin.
Constraints: shared tail; backdrop is one flat color with no texture or gradient.
```

QA extra: measure the backdrop with `--target '#RRGGBB'`; confirm product colors
did not shift toward the backdrop.

## editorial

Magazine still life; styled props support the product's story without
competing with it.

```text
Task: Image-to-Image (I2I)
Subject: [product descriptor], resting on [surface material], accompanied by [two or three plain, unbranded companion objects that fit the brief], the product clearly the focal point.
Setting: [neutral tabletop or shelf from the brief], muted [palette words], soft texture, nothing printed on any companion object.
Style: Editorial still-life photography, considered negative space, [brand imagery sentence].
Lighting: Directional soft window light from [side], long gentle shadows, natural falloff.
Composition: Product on the [left/right] third, companions secondary and partly out of focus, 50mm-equivalent perspective.
Constraints: shared tail; companion objects plain, no readable text or logos on them.
```

## macro-detail

A close-up of a material, texture, finish or mechanism. The label is usually
partial, so this preset never carries a legibility requirement.

```text
Task: Image-to-Image (I2I)
Subject: Extreme close-up of [the identity-critical detail: texture, seam, nozzle, clasp] of the product in @Image 1, the detail filling the frame.
Setting: Out-of-focus continuation of the product, no other objects.
Style: Macro product photography, true micro-texture, crisp focal plane.
Lighting: Gentle raking light from [side] to reveal texture, controlled specular highlight.
Composition: The detail sharp across a thin focal plane, soft falloff, [any partial label area out of focus].
Constraints: shared tail; partial label areas soft, not re-lettered.
```

## in-use

The product doing a **supported** job from the product facts. Name the action as
an observable operation, never as an unsupported result.

```text
Task: Image-to-Image (I2I)
Subject: [product descriptor] in use: [supported operation, e.g. the lid flipped open with one thumb], [who uses it, from the brief, partly in frame].
Setting: [real use context from the brief], tidy and plausible.
Style: Natural commercial photography, believable materials, [brand imagery sentence].
Lighting: [named practical or window source], soft and realistic.
Composition: The product and the operated part sharp and unobstructed, the person secondary, [ratio-appropriate framing].
Constraints: shared tail; anatomically correct hands with five fingers each, no exaggerated result effects.
```

## faceless-hands

Hands only, no face; neutral and brand-safe.

```text
Task: Image-to-Image (I2I)
Subject: [product descriptor] held by two hands [grip: cradled from below / thumb on the button], [skin tone, nails and sleeves from the brief], no face or body beyond the wrists.
Setting: [plain backdrop or soft context from the brief].
Style: Clean commercial photography, [brand imagery sentence].
Lighting: Soft frontal key with gentle fill, neutral white balance.
Composition: Hands and product centered, the product's front facing camera and unobstructed by fingers, [copy space if needed].
Constraints: shared tail; exactly two hands, five fingers each, natural grip, no rings or jewellery unless the brief asks.
```

## flat-lay

Top-down arrangement. Composite the product when the label must read; the
companions and surface come from the plate.

```text
Task: Image-to-Image (I2I)
Subject (plate): A top-down arrangement of [three to five plain, unbranded companion objects] around an empty central space sized for the product, [surface material].
Subject (generated): [product descriptor] lying flat at center, surrounded by [companions].
Setting: [surface from the brief or brand palette color, hex if used].
Style: Overhead flat-lay photography, orderly spacing, [brand imagery sentence].
Lighting: Soft, even overhead light, short soft shadows.
Composition: Straight-down camera, product at center, companions balanced with consistent spacing, nothing touching the frame edge.
Constraints: shared tail; companions plain, nothing printed on them.
```

## lifestyle

The product in the audience's own setting. The brief supplies the setting,
season, people and culture; the preset assumes none.

```text
Task: Image-to-Image (I2I)
Subject: [product descriptor] placed naturally on [surface] in [setting from the brief], [optional person from the brief at mid-distance, not looking at camera].
Setting: [setting details from the brief], lived-in but uncluttered, no visible brand names on anything else.
Style: Lifestyle photography, natural color, [brand imagery sentence].
Lighting: [time of day and named source from the brief].
Composition: Product in the foreground [third], sharp, setting softly out of focus, [copy space if needed].
Constraints: shared tail; no other products with logos, no readable signage.
```

## hero-plinth

Premium hero on a sculpted plinth. Plate + composite keeps the label exact.

```text
Task: Image-to-Image (I2I)
Subject (plate): An empty [cylindrical / stepped / arched] plinth of [material, color], its top surface clear and sized for one product about [size in frame] tall.
Subject (generated): [product descriptor] standing on a [plinth description].
Setting: [backdrop color from the brand kit, hex] with a soft gradient falloff behind the plinth.
Style: Premium product hero photography, sculpted forms, [brand imagery sentence].
Lighting: Soft key from [front left], a clean rim light outlining the product's edge, gentle falloff into the background.
Composition: Plinth centered low, product top-center, [copy area above or beside], generous margin.
Constraints: shared tail; plinth plain with nothing printed.
```

## marketplace-dark

Dark seamless secondary image. Marketplaces that require white main images
usually allow other backgrounds only for secondary images; verify first.

```text
Task: Image-to-Image (I2I)
Subject (plate): An empty dark seamless floor and backdrop, the center clear for one product.
Setting: A deep charcoal seamless background, hex [#1C1C1E or brand dark], one continuous field.
Style: Low-key product photography, rich blacks without crushed detail.
Lighting: Two soft rim lights from behind left and right, a low frontal fill so the label face stays readable.
Composition: Product centered with an even margin.
Constraints: shared tail; no fog, sparks or particles.
```

QA extra: `--target` set to the dark hex; check that the product's dark parts
still separate from the backdrop.

## marketplace-pastel

Soft pastel seamless secondary image.

```text
Task: Image-to-Image (I2I)
Subject (plate): An empty pastel seamless floor and backdrop, the center clear for one product.
Setting: A soft pastel [color name] seamless background, hex [#RRGGBB from the brand kit], one flat continuous field.
Style: Light, airy product photography, gentle saturation.
Lighting: Large soft frontal light, very soft shadow directly beneath the product.
Composition: Product centered with an even margin.
Constraints: shared tail; no gradient, texture or props.
```

## marketplace-surreal-3d

Stylized 3D scene of soft geometric forms around the product. Generated; the
label must not be a legibility requirement unless the product is composited
over a generated empty scene.

```text
Task: Image-to-Image (I2I)
Subject: [product descriptor] resting among [smooth spheres, arches and pill shapes] in [brand palette colors, hex], the product the largest and sharpest object.
Setting: A minimal surreal 3D set, matte clay-like surfaces, soft infinite backdrop in [palette color].
Style: Clean 3D render look, soft global illumination, [brand imagery sentence].
Lighting: Soft area light from above, gentle ambient occlusion in the contact areas.
Composition: Product centered or on the [left] third, shapes framing it without overlapping its front face.
Constraints: shared tail; shapes plain, no text or symbols on any surface.
```
