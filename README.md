# Poly Source — Blender Add-on

A compact toolkit for game-ready modeling in Blender: polycount feedback, topology checks, boolean helpers, transform utilities, mesh cleanup, modifier presets, and a UE-style material builder.

**Blender:** 4.2+ (including 5.x) · **License:** GPL-3.0-or-later · **Location:** 3D View

---

## Installation

Poly Source ships as a **Blender Extension** (a `.zip` file with `blender_manifest.toml` inside).

1. Download the latest `poly_source-*.zip` (do **not** unpack it).
2. In Blender open `Edit → Preferences → Get Extensions`.
3. Click the **dropdown arrow (˅) in the top-right corner** of the Preferences window and choose **Install from Disk…**
4. Select the downloaded ZIP — the add-on is installed and enabled automatically.

> Tip: you can also simply **drag & drop the ZIP** into the Blender window and confirm the dialog.

Requires Blender **4.2 or newer** — older versions do not support the Extensions system.

---

## Features

### Viewport & UI
- **Polycount counters** in the header (Top Bar / Viewport / Tool Header) — N-gons, Quads, Tris; click a counter to select faces of that type. Performance limits are configurable.
- **Polycount overlay** — scene triangle count vs. target budget with color-coded feedback; supports `_LOW` collection filtering.
- **Check Objects popover** — live topology diagnostics drawn in the viewport: non-manifold edges, isolated / boundary / inline (2-edge) vertices, N/E/>5 poles, tris, N-gons, elongated tris, custom vertex count. Statistics per check.
- **Facet Ratio** — estimates how Unreal Engine sees the mesh after triangulation and hard-edge vertex splitting: V/T ratio and vertex split factor with good/warn/error indicators.
- **Unit Grid** — configurable grid/box overlay (size, padding, sub-grid, X-Ray, colors) in the sidebar `PS` tab.
- **Wireframe for Selected** — auto-show wire only on selected objects (toggle in Viewport Overlays).
- **Color Randomizer**, **Camera Sync** controls, and **snapping angle presets** (5°–90°) in headers/popovers.

### Booleans
Header buttons: **Difference / Union / Intersect / Slice**.
- Only the boolean modifier created by the operator is applied — the rest of the object's modifier stack stays untouched.
- `Shift+LMB` — keep the cutter object after the operation.
- `Ctrl+LMB` — brush mode: the modifier stays live, the cutter is displayed as wireframe.

### Mesh Tools (Edit Mode)
- **Edge Decal** — generate a separate decal strip mesh from selected edges or quad strips, with trim-sheet UV mapping (orientation, trim index/count, scale, random shift, conform to face).
- **Set Edge Data** — smart toggle for Seam / Sharp / Bevel Weight / Crease on selected edges.
- **Cylinder Optimizer** — dissolve every N-th edge loop (skip/nth/offset); "Rounding Up" mode shapes loops into circles (requires LoopTools).
- **Cleanup:** Clear Dots (isolated vertices), Remove Non-Manifold Vertices, Delete Long Faces (angle-based dissolve).
- **Fill From Points** (minimum spanning tree) and **Fill Mesh** (convex hull).
- **Reset Vertex Location** — snap selected vertices to object origin / world / 3D cursor, per axis.

### Transform
- **Transform+ panel** (sidebar `PS` tab) — per-axis Location/Rotation/Scale with inline reset buttons, axis locks, copy-to-clipboard, rotation mode switcher; vertex/edge Bevel & Crease toggles in Edit Mode.
- **Reset transforms** per axis or all, optionally relative to the 3D cursor.
- **Transfer Transform** from active to selected; **Distribute Objects** along X by bounding box.

### Materials & Modifiers
- **UE Material** — build an Unreal-style PBR node tree from textures: Base Color, Mask (R=Roughness, G=Metallic, B=AO), Normal (G-channel auto-inverted), Emissive.
- **Modifier presets:** Triangulate, Tris & Weighted Normal, Crease Bevel + Subdivision, Non-manifold Solidify.
- **Object utilities:** Add Material, Clear Materials, Clear Data (vertex groups / shape keys / attributes), Set Random Name, Add Camera from view.

---

## Where to Find It
- **Headers** — polycount, mesh check toggle, booleans, color randomizer, camera sync (placement configurable in Preferences).
- **RMB context menu → Poly Source** — modifier presets, utilities, edge data toggles, selection helpers, Edge Decal.
- **Sidebar → `PS` tab** — Unit Grid and Transform+ panels.
- **Viewport Overlays** — Wireframe for Selected; **Snapping popover** — angle presets.

## Preferences
`Edit → Preferences → Add-ons → Poly Source` (or the Extensions list): header button visibility, polycount placement and performance limits, mesh check colors and sizes, unit grid colors.

## License
[GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0.html)
