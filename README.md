## Poly Source — Blender Add-on

A compact toolkit for modeling workflows in Blender: quick polycount feedback, boolean helpers, transform utilities, mesh cleanup, modifiers presets, UE-texture material setup, custom add objects, unit grid overlay, and more.

Supports Blender 4.2+ (see `__init__.py`). Location: `3D View` (headers, context menus, and popovers).

---

### Table of Contents
- [Features](#features)
  - [Viewport and UI](#viewport-and-ui)
  - [Selection and Mesh Tools](#selection-and-mesh-tools)
  - [Transform Utilities](#transform-utilities)
  - [Materials and Shading](#materials-and-shading)
  - [Modifiers Presets](#modifiers-presets)
  - [Booleans](#booleans)
  - [Object Utilities](#object-utilities)
  - [Add Object (Tool Kit)](#add-object-tool-kit)
  - [Cleanup](#cleanup)
- [Installation](#installation)
- [How to Use](#how-to-use)
- [Preferences](#preferences)
- [Compatibility](#compatibility)
- [License](#license)

---

### Features

#### Viewport and UI
- Polycount overlay and header counters with click-to-select by topology type (N-gons, Quads, Tris).
- Tool Kit popover for quick access to tools and counters.
- Check Objects panel to analyze common topology issues (non-manifold, poles, elongated tris, custom counts, etc.).
- Unit Grid overlay: draw configurable unit grid/box with padding, sub-grid, alignment, and colors.
- Optional header buttons: boolean tools, camera view/lock, and quick actions in Outliner header.
- RMB (context) menu integration under “Poly Source”.

#### Selection and Mesh Tools
- Select Polygons by number of sides:
  - Select Polygons → pick NGONS, QUADS, or TRIS.
- Clear single-vertex islands (dots):
  - Clear Dots.
- Remove non-manifold vertices not connected to faces:
  - Remove Non Manifold Vertex.
- Reset vertex location in Edit Mode to object/world/3D cursor, per-axis or all:
  - Reset Vertex Location.
- Fill From Points (experimental generation from points/edges):
  - Fill From Points.
- Set Edge Data toggle for selected edges (smart on/off):
  - Set Edge Data (Seam, Sharp, Bevel Weight, Crease).
- Cylinder Optimizer (Edit Mode), with rounding option:
  - Cylinder Optimizer.

#### Transform Utilities
- Reset transforms for selected objects (Location, Rotation, Scale) per-axis or all; optionally relative to 3D Cursor:
  - Reset Location
  - Reset Rotation
  - Reset Scale
  - Special “Reset All” option for location+rotation+scale.
- Transfer transformation from active to selected (choose which: Loc/Rot/Scale):
  - Transfer Transform Data.
- Distribute objects horizontally with spacing derived from object bounds (EXPERIMENTAL):
  - Distribute Objects (TEST) — property: Expose Factor.

#### Materials and Shading
- Add simple material to all selected objects:
  - Add Material (creates/uses “PS Material”).
- UE-style Material from texture set with mask unpacking and normal-green inversion:
  - UE Material with properties:
    - Base Color Texture
    - Mask Texture (R=Roughness, G=Metallic, B=AO)
    - Normal Texture (G channel inverted automatically)
    - Emissive Texture (uses R channel with color/intensity)
    - Apply to Active Material toggle
- Quick smooth shading and weighted normal + triangulate combo:
  - Tris & Weighted Normal (configurable mode, weight, threshold, keep sharp, face influence).

#### Modifiers Presets
- Triangulate preset modifier:
  - Triangulate (fixed quad method, beauty n-gon).
- Add Subdivision and Bevel combined preset:
  - Add Subdivision And Bevel with presets: Default, Wide, Angle-Based.
- Solidify preset tuned for non-manifold boundary:
  - Solidify.

#### Booleans
- Fast boolean operations (Shift = keep cutter, Ctrl = Brush mode):
  - Bool Difference
  - Bool Union
  - Bool Intersect
  - Bool Slice (creates split copy intersection)

#### Object Utilities
- Randomize object names (11 letters) for all selected meshes:
  - Set Random Name (also available as an Outliner header button).
- Add and align camera to view; toggle camera transform locks from header:
  - Add Camera
  - Lock Camera Transforms
- Clear data on selected objects (vertex groups, shape keys, color attributes, face maps, attributes):
  - Clear Data.
- Clear all materials from selected objects:
  - Clear Materials.

#### Add Object (Tool Kit)
- Custom primitives exposed in Add > Mesh (when enabled in Preferences):
  - Create Cube
  - Create Cylinder
  - Create Tube

#### Cleanup
- Delete elongated triangles/long faces (Edit Mode):
  - Delete Long Faces.

---

### Installation
1. Download the add-on as a ZIP or keep the folder structure as is.
2. Blender → Edit → Preferences → Add-ons → Install…
3. Select the ZIP (or the `Poly_Source` folder if installing from source) and enable “Poly Source”.
4. Confirm Blender version is 4.2+.

---

### How to Use
- Viewport Header (Top):
  - Polycount quick counters with popover to Tool Kit and Check panels.
  - Optional Boolean buttons and Camera controls (enable in Preferences).
- RMB Context Menu → “Poly Source”:
  - Quick access to Modifiers, Test tools, and Edge Data toggles in Edit Mode.
- Add > Mesh menu:
  - Custom objects (Cube, Cylinder, Tube) when the option is enabled in Preferences.
- Panels:
  - Tool Kit: transform tools, display helpers, counters.
  - Check Objects: topology diagnostics and summary.
  - Unit Grid (sidebar `PS` tab): overlay configuration for grid/box.

---

### Preferences
Find under Edit → Preferences → Add-ons → Poly Source.

Options include (non-exhaustive):
- Show Polycount in various headers (Top, Viewport Left/Right, Tool Header).
- Enable Boolean tool buttons in headers.
- Enable Camera Sync controls in the 3D View header.
- Show Unit Grid settings and drawing.
- Presets for snapping increment angles.
- Optional “Wireframe for Selected” integration.
- Keymap: open Tool Kit panel via Space (note: may conflict with other add-ons/keymaps).

---

### Compatibility
- Blender: 4.2+ (as defined in `bl_info`). Some UI icons or header placements adapt based on Blender version.
- Other add-ons: some hotkeys or header insertions may overlap; adjust in Preferences as needed.

---

### License
Specify your license here (e.g., MIT). If omitted, users will assume default “all rights reserved”.

---

Thanks for using Poly Source! If you encounter issues or have feature requests, please open an issue on the repository.
