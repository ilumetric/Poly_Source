## Poly Source — Blender Add-on

A compact toolkit for game-ready 3D modeling workflows in Blender: polycount feedback, boolean helpers, transform utilities, mesh cleanup, modifier presets, UE-texture material setup, topology diagnostics, unit grid overlay, and more.

**Version:** 5.0.5 · **Author:** Max Derksen · **Blender:** 4.2+ · **License:** GPL-3.0-or-later

Location: `3D View` (headers, context menus, sidebar panels, and popovers).

---

### Table of Contents
- [Features](#features)
  - [Viewport and UI](#viewport-and-ui)
  - [Selection and Mesh Tools](#selection-and-mesh-tools)
  - [Transform Utilities](#transform-utilities)
  - [Transform+ Panel](#transform-panel)
  - [Materials and Shading](#materials-and-shading)
  - [Modifiers Presets](#modifiers-presets)
  - [Booleans](#booleans)
  - [Object Utilities](#object-utilities)
  - [Cleanup](#cleanup)
- [Installation](#installation)
- [How to Use](#how-to-use)
- [Preferences](#preferences)
- [Compatibility](#compatibility)
- [License](#license)

---

### Features

#### Viewport and UI
- **Polycount header counters** with click-to-select by topology type (N-gons, Quads, Tris). Configurable placement: Top Bar, Viewport Header Left/Right, Tool Header.
- **Polycount overlay** — viewport widget showing scene triangle count vs. target budget with color-coded feedback (green / orange / red). Supports `_LOW` collection suffix filtering.
- **Tool Kit popover** for quick access to transform reset and display settings.
- **Check Objects panel** — real-time topology diagnostics: non-manifold edges, isolated vertices, boundary vertices, E-poles (5 edges), N-poles (3 edges), extraordinary poles (>5 edges), tris, N-gons, elongated triangles, and custom vertex count.
- **Unit Grid overlay** — configurable grid/box drawn in the viewport with padding, sub-grid, cell size, alignment, height, X-Ray mode, and custom colors. Settings in the sidebar `PS` tab.
- **Color Randomizer** — header buttons to add/remove incremental color prefix (`CR#_`) to object names for viewport random-color shading.
- **Boolean tool buttons** in the 3D Viewport header (Difference, Union, Intersect, Slice).
- **Camera Sync controls** — camera view toggle, lock camera to view, and lock camera transforms from the header.
- **RMB context menu** integration under "Poly Source" (Object Mode and Edit Mode).
- **Outliner header button** — quick "Set Random Name" for selected objects.
- **Snapping angle presets** — quick-access buttons (5°–90°) in the Snapping popover (3D View and Image Editor).
- **Wireframe for Selected** — automatically display wireframe overlay only on selected objects (toggle in Viewport Overlays).

#### Selection and Mesh Tools
- **Select Polygons** by number of sides — pick N-gons, Quads, or Tris and switch to Edit Mode.
- **Clear Dots** — delete single-vertex islands (vertices with no connected edges).
- **Remove Non Manifold Vertex** — delete vertices not connected to any face.
- **Reset Vertex Location** (Edit Mode) — move selected vertices to object origin, world origin, or 3D cursor, per-axis or all, with individual/grouped mode.
- **Fill From Points** — connect selected vertices into a mesh using a minimum spanning tree algorithm.
- **Fill Mesh** — generate faces from selected vertices by computing a convex hull.
- **Set Edge Data** — smart toggle for Seam, Sharp, Bevel Weight, and Crease on selected edges. Supports combined modes (e.g. Seam + Sharp).
- **Cylinder Optimizer** (Edit Mode) — reduce cylinder polygon count by dissolving selected edge loops with configurable skip/nth/offset pattern. Includes a "Rounding Up" mode to shape loops into perfect circles.

#### Transform Utilities
- **Reset transforms** for selected objects (Location, Rotation, Scale) per-axis or all; optionally relative to the 3D Cursor.
- **Reset All** — reset location, rotation, and scale in one click.
- **Transfer Transform Data** — copy location, rotation, and/or scale from the active object to all selected objects.
- **Distribute Objects** — evenly distribute selected objects along the X axis with spacing based on bounding box sizes (adjustable expose factor).

#### Transform+ Panel
Enhanced transform panel in the sidebar (`PS` tab) with:
- **Per-axis display** of Location, Rotation, and Scale with inline reset-to-default buttons.
- **Copy to clipboard** buttons for each transform type.
- **Rotation mode switcher** (Euler, Quaternion, Axis-Angle) with full W/X/Y/Z support.
- **Lock toggles** per axis.
- **Edit Mode section** — toggle Vertex/Edge Bevel Weight and Crease.

#### Materials and Shading
- **Add Material** — create and assign a default "PS Material" to all selected objects.
- **UE Material** — create an Unreal Engine-style PBR material from texture maps:
  - Base Color Texture
  - Mask Texture (R=Roughness, G=Metallic, B=AO — auto-mixed with Base Color)
  - Normal Texture (G channel inverted automatically for UE convention)
  - Emissive Texture (R channel with configurable color and intensity)
  - "Apply to Active Material" toggle to rebuild nodes in an existing material.
- **Tris & Weighted Normal** — apply smooth shading and add Triangulate + Weighted Normal modifiers with configurable mode, weight, threshold, keep sharp, and face influence.

#### Modifiers Presets
- **Triangulate** — add a triangulate modifier with optimized quad splitting (Fixed) and N-gon method (Beauty).
- **Add Subdivision And Bevel** — combined bevel + subdivision modifiers with presets: Default (weight-based), Wide (no clamp), Angle-Based.
- **Solidify** — non-manifold solidify modifier with flat boundary mode and even thickness.

#### Booleans
Fast boolean operations with modifier hotkeys:
- **Bool Difference** — subtract selected from active.
- **Bool Union** — merge selected into active.
- **Bool Intersect** — keep only overlapping volume.
- **Bool Slice** — cut active into two parts (difference + intersection copy).

Modifiers:
- `Shift+LMB` — keep the boolean operand object.
- `Ctrl+LMB` — non-destructive brush mode (keep modifier live).

#### Object Utilities
- **Set Random Name** — assign random 11-character names to selected objects (also in Outliner header).
- **Add Camera** — create a camera aligned to the current viewport view with camera lock enabled.
- **Lock Camera Transforms** — toggle location, rotation, and scale locks on the active camera.
- **Clear Data** — remove vertex groups, shape keys, color attributes, and custom attributes from selected objects.
- **Clear Materials** — remove all material slots from selected objects.

#### Cleanup
- **Delete Long Faces** (Edit Mode) — dissolve vertices where adjacent edges form angles exceeding a configurable threshold. Supports comparison operators (greater than, less than, equal to, not equal to), face split, boundary tear, and selected-faces-only mode.

---

### Installation

**Extension (Blender 4.2+):**
1. Download the add-on ZIP.
2. Blender → Edit → Preferences → Get Extensions → Install from Disk…
3. Select the ZIP file and enable "Poly Source".

**Legacy (from source):**
1. Copy the `Poly_Source` folder to Blender's addons directory.
2. Edit → Preferences → Add-ons → search "Poly Source" and enable it.

---

### How to Use
- **Viewport Header (Top Bar):**
  Polycount counters with popover to Tool Kit and Check panels. Optional Boolean buttons, Camera Sync controls, and Color Randomizer (enable in Preferences).
- **RMB Context Menu → "Poly Source":**
  Modifiers presets, utility operators, edge data toggles (Edit Mode), edge selection helpers.
- **Sidebar → PS tab:**
  - *Unit Grid* — grid/box overlay configuration.
  - *Transform+* — enhanced transform panel with per-axis reset and clipboard copy (enable in Preferences).
- **Snapping Popover:**
  Angle increment presets (5°, 10°, 15°, 30°, 45°, 60°, 90°).
- **Viewport Overlays:**
  "Display Wireframe for Selected" toggle (when enabled in Preferences).
- **Outliner Header:**
  "Set Random Name" button.

---

### Preferences
Find under Edit → Preferences → Add-ons → Poly Source.

**General tab:**
| Section | Options |
|---|---|
| Viewport Header | Color Randomizer, Bool Tool, Camera Sync buttons |
| Polycount | Placement (Header, Viewport Left/Right, Tool Header), `_LOW` suffix filter, performance limits (max vertices, max objects) |
| Panels & Tools | Transform+ panel, Wireframe for Selected, Snapping angle presets |
| Mesh Check | Point/edge sizes, highlight colors for each topology check |
| Unit Grid | Grid and box colors |
| Links | Blender Market, Gumroad, Artstation |

**Keymaps tab:**
- Open Tool Kit panel via `Space` (customizable; may conflict with other add-ons/keymaps).

---

### Compatibility
- **Blender:** 4.2+ including Blender 5.x (minimum version is defined in `blender_manifest.toml`).
- **Booleans:** boolean operators use Blender's `EXACT` solver path for stable, predictable results across Blender 4.2+ and 5.x.
- **Other add-ons:** some hotkeys or header insertions may overlap; adjust in Preferences as needed. Cylinder Optimizer's "Rounding Up" mode requires the LoopTools add-on.

---

### License
This add-on is licensed under [GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0.html).

---

Thanks for using Poly Source! If you encounter issues or have feature requests, please open an issue on the repository.
