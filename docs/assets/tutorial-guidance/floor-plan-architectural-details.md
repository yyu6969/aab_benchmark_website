# Architectural Floor Plan Construction, Dynamic Block Authoring, Multi-Scale Layouts, and Publication

## Overall Objective
In Autodesk AutoCAD 2019, working within `floor plan exercise.dwg`, construct a complete multi-unit architectural floor plan from initial perimeter drafting to final multi-scale presentation layouts and PDF publication. The workflow encompasses configuring decimal meter units and precision drafting grid settings; drawing double-line exterior walls and interior partition layouts; drafting elevator shaft geometry; defining static and dynamic architectural blocks (single swing doors with dynamic flip, symmetrical double doors, restroom fixtures with dual-axis flips, and stretchable windows); structuring project layers with standardized colors; drafting detailed staircase flights; placing room designation labels with custom Candara typography; setting up paper space layouts with scaled viewports (1:200, 1:16, 1:10) and an annotative title block; applying viewport layer overrides; adding linear and continuous exterior and detail dimensions; and publishing borderless PDF sheets.

---

## 1. Project Setup, Units, Grid Spacing, and Wall Linework

### Drawing Units and Drafting Environment
- Open the Drawing Units dialog using the `UNITS` command and configure:
  - **Length Type:** Decimal
  - **Insertion Scale (Units to scale inserted content):** Meters
  - **Precision:** `0.0000` (or `0.00`)
- On the AutoCAD status bar, enable **Grid Mode** (`<Grid on>`) and **Snap Mode** (`<Snap on>`).
- Open the Drafting Settings dialog (`DSETTINGS`) under the **Snap and Grid** tab and set:
  - **Snap X spacing:** `0.01`
  - **Snap Y spacing:** `0.01`
  - **Grid X spacing:** `0.01`
  - **Grid Y spacing:** `0.01`

### Exterior Wall Contour
- Activate the polyline command (`PLINE`) and draw the closed exterior building perimeter, beginning with a `3.30` m horizontal segment along the 0° polar tracking axis, continuing around the perimeter profile, and closing the polyline back to its origin vertex (`Close` / `c`).
- Execute the `OFFSET` command with an offset distance of `0.30` m and offset the closed perimeter polyline inward to establish a continuous 0.30 m double-line exterior wall thickness.

### Interior Partitions, Angled Junctions, and Mirrored Corridors
- **Upper Horizontal Dividing Wall:** Activate `LINE`, acquire an Object Snap Tracking reference from the upper-right interior wall corner, track downward along the inner vertical wall by `3.45` m to establish the start point, and extend horizontally along 180° across the plan to intersect the opposite wall boundary.
- **Upper Vertical Partition:** Activate `LINE`, track horizontally to the left from the upper-right interior corner along the upper inner wall by `3.75` m, draw vertically downward at 90°, and snap to the horizontal interior dividing wall. Offset this line by `0.10` m to the left to establish wall thickness, and erase any accidental extra offset line segment.
- **Central Vertical Wall & Angled Corner Junction:** Snap to the horizontal interior wall (near coordinates `1866.25, 1100.55`) and draw a `2.80` m vertical line upward at 90°. Offset this segment `0.30` m to the left. At the junction, draw a diagonal line segment at approximately 133° (~0.40 m length), offset it `0.30` m toward the lower right, and stretch its top endpoint grip along the extension line until it intersects the vertical wall line.
- **Junction Cleanup:** Select and delete the two obsolete intersecting line segments inside the upper corner junction.
- **Symmetrical Corridor Generation:** Execute the `MIRROR` command, select the 4 corner wall objects, define the mirror line using the Midpoint snap of the adjacent horizontal wall tracked vertically along 90°, and retain source objects (`No` to erase source objects).
- **Corridor Doorway Opening:** Execute `TRIM` to trim away the horizontal wall segment between the two vertical wall extensions.

### Interior Room Bays and Boundary Partitions
- **Partition Offsets:** Offset vertical wall lines to the right at distances of `2.50` m and `3.10` m to define interior room bays.
- **Extend Partitions:** Execute `EXTEND` using the bottom inner boundary polyline as the boundary edge, and extend the two pairs of vertical lines downward to terminate precisely at the lower boundary.
- **Lower Room Corner:** Activate `LINE`, track downward `2.55` m from the upper wall, draw vertically downward `2.50` m, and then horizontally to the right `2.55` m along 0°. Convert these two perpendicular segments into a single polyline using `JOIN` (`2 objects converted to 1 polyline`). Offset the joined polyline `0.10` m for wall thickness, and trim intersecting wall lines at the corner junction.

### Layout Repositioning and Lift Shaft Geometry
- Select all floor plan objects (56 objects) using a crossing window and execute `MOVE`, picking the upper-left corner vertex as the base point to reposition the layout comfortably on the drafting grid.
- Ensure 2D Object Snap (`<Osnap on>`) is active, navigate to the designated lift area, and construct the lift geometry using `RECTANG`:
  - Outer shaft enclosure: `1.80` m width by `-1.80` m height.
  - Corner offset guide: `0.20` m by `0.20` m rectangle at the upper-left corner.
  - Internal cab rectangle with crossed diagonal lines (`X`) connecting opposing vertices to complete the architectural elevator shaft symbol.

---

## 2. Reusable Block Library Authoring and Dynamic Parameters

### Standard Single Door (`door standard`)
- **Geometry Construction:** In the door drafting workspace, create a `0.05` m wide by `0.10` m high rectangle for the left jamb (`RECTANG`). Copy the jamb horizontally to the right with a displacement distance of `0.95` m to create the right jamb (`COPY`). Draw a `0.90` m vertical line upward from the top-right corner of the left jamb for the door leaf (`LINE`). Construct a 90° door swing arc using the Start, Center, End method (`ARC`) connecting the door leaf endpoint to the inner corner of the right jamb.
- **Block Creation:** Open the Block Definition dialog (`BLOCK`), name the block `door standard`, select the 4 door objects, and specify the insertion base point at the lower-left corner of the left jamb.
- **Dynamic Flip Parameter:** Open `door standard` in the Block Editor (`BEDIT`). Add a Flip parameter (`Flip state1`) with its reflection line starting at the midpoint of the bottom threshold line and tracking vertically along 90°. Assign a Flip action (`BACTION`) associated with `Flip state1`, selecting all door geometry entities. Save block changes (`_BSAVE`) and close the Block Editor (`_BCLOSE`). Test the triangular flip grip in model space.
- **Door Population:** Insert `door standard` into wall openings. Use `MIRROR` vertically and horizontally to generate 4 swing orientations, rotate a copy by 270° using `ROTATE` (Copy option) to generate vertical door symbols, and mirror door symbols across the central corridor into opposing doorways.
- **Angled Corridor Fitting:** At the angled corridor opening, remove any existing door, delete the obsolete horizontal wall segment, stretch the top grip of the diagonal wall line northwest along 135° (~0.08 m) to accommodate the standard opening width, and insert `door standard` on the `doors` layer.

### Symmetrical Double Door (`double door`)
- Reset the UCS to World (`WCS`). In the double door drafting area, construct one door leaf: jamb rectangle (`0.05` m by `0.10` m), vertical leaf line, and a 90° arc of radius `0.70` m. Mirror the 3 leaf objects vertically across the swing arc endpoint (retaining source objects) to create the complete 6-object double-door assembly.
- Create a block definition named `double door` containing the 6 objects, setting its insertion base point at the bottom corner of the right jamb.

### Dynamic Window Block (`windows`)
- Draw a `0.90` m by `0.08` m rectangle on layer `windows` (`RECTANG`). Switch the active layer to `0` and define block `windows` from the 6 window geometry entities, specifying the lower-left corner as the insertion base point.
- Open `windows` in the Block Editor. Add a horizontal Linear parameter (`Distance1`) across the bottom width. Assign a Stretch action associated with the right parameter point, defining a stretch frame enclosing the right side and selecting the 4 rightward objects. Save and close the Block Editor.
- Test dynamic behavior on the canvas by stretching instances horizontally to `1.20` m and `1.36` m using the dynamic grip.

### Restroom Compartment and Fixture Block (`toilet`)
- **Enclosure Construction:** Using `PLINE`, draw perpendicular walls measuring `1.00` m vertical and `1.40` m horizontal. Apply `CHAMFER` with a distance of `0.25` m on both segments. Join the 3 segments into a single polyline (`JOIN`) and offset it by `0.10` m for double-line thickness.
- **Fixture Insertion:** Using DesignCenter (`bath furnitures.dwg`), insert `toilet 3` and `sink 8` (scale 1). Move the sink into the inner chamfered corner. Rotate `toilet 3` by 270° and position it adjacent to the sink. Insert a `door standard` block at the entrance corner snap.
- **Block Definition (`toilet`):** Create block `toilet` from the 7 fixture and enclosure objects, setting its insertion base point at the bottom-left endpoint snap.
- **Dual-Axis Dynamic Flips:** In the Block Editor for `toilet`, add:
  - `Flip state1`: vertical reflection line along the bottom boundary.
  - `Flip state2`: horizontal reflection line near the fixture base.
  - Assign a Flip action to `Flip state2` selecting the fixture geometry. Save and close.
- **Restroom Deployment:** Insert `toilet` blocks into private restrooms along the corridor. Relocate partition enclosures around lower fixtures with added door swing arcs. Insert private toilet dynamic blocks, flip horizontally as needed, snap base grips to horizontal/vertical partition intersections, and rotate stall toilet fixtures by 90°.

---

## 3. Layer Management, Color Properties, and Staircase Detailing

### Layer Configuration
In the Layer Properties Manager (`LAYER`), configure the following drawing layers:
- `walls`: Color White / Index 7 (assign existing floor plan wall linework to this layer).
- `doors`: Color Index 140 (cyan), subsequently updated to Color Index 51 (yellow). Assign all door blocks to this layer.
- `staircase`: Color Index 191 (purple); set as active layer.
- `windows`: Standard drafting layer for window components.
- `text labels`: Dedicated layer for all room designation typography.
- `dimensions`: Color Index 81 (green); set default dimension layer (`DIMLAYER`) to `dimensions`.
- `viewport`: Color Index 7 (white); set the Plot property to **No Plot** (disabled printer icon).

### Staircase Construction and Duplication
- Set line color to `ByLayer`.
- Draw a `1.10` m horizontal tread line positioned `1.30` m from the upper-left wall corner.
- Use `OFFSET` with an offset distance of `0.25` m upward repeatedly to generate 8 parallel staircase treads.
- Mirror the 8 treads across a vertical axis defined from the bottom tread midpoint (retaining source treads).
- Draw an angled flight line across the right section and trim the 2 vertical bounding lines (`TRIM`).
- Copy the 21 staircase elements into the corridor area using the bottom edge midpoint as the base point (`COPY`).
- Mirror the right flight of the central staircase across its bottom midpoint and select `Yes` to erase source objects, properly orienting the landing flight.

---

## 4. Typography, Text Formatting, and Annotative Dimensioning

### Room Designation Labels
- In the Text Style dialog (`STYLE`), set the font for the `Standard` text style to **Candara** and click Apply.
- On layer `text labels`, create a single-line text label reading `common area` (`TEXT`) and copy it into each room across the floor plan.
- Use `TEXTEDIT` to update the room designations:
  - Public areas: `dinning area` (demonstrated spelling), `kitchen`, `office`, `stairs`
  - Rental units: `unit 1`, `unit 2`, `unit 3`, `unit 4`, `unit 5`, `unit 6`, `unit 7`
- Isolate layer `text labels` (`LAYISO`). Open the Quick Properties palette, select all 13 text objects, and set:
  - **Height:** `0.80`
  - **Justify:** `Right`
- Unisolate layers (`LAYUNISO`).
- Create a multiline text label (`MTEXT`) reading `disable bathroom` in the room adjacent to unit 5.

### Annotative Dimension Style (`Annotative meters`)
- Set default dimension layer (`DIMLAYER`) to `dimensions`.
- In the Dimension Style Manager (`DIMSTYLE`), modify style `Annotative meters`:
  - **Symbols and Arrows tab:** Center marks size `0.0025`, Break size `0.0038`.
  - **Text tab:** Text height `0.0015`, Offset from dim line `0.0005`.

### Exterior Wall Dimensions
- Place a `1.44` m linear dimension (`DIMLINEAR`) above the top-right exterior wall of unit 4.
- Use `DIMCONTINUE` to place continuous dimensions across units 3 and 2 (consecutive segments: `2.49`, `1.36`, `1.55`, `1.20`, `0.90`, `0.50`, `0.90`, `1.20`, and `2.20` m).
- Select the continuous dimension string grips and shift the entire dimension line upward to clear the exterior wall perimeter.

---

## 5. Sheet Layouts, Multi-Scale Viewports, Layer Overrides, and PDF Plotting

### Layout1 Page Setup and Main Viewport
- Navigate to the `Layout1` tab. In the Page Setup Manager, modify `Layout1` to set the plot scale to `1000 mm = 1 unit`.
- In paper space, draw a rectangular sheet border inside the printable margin (`RECTANG`).
- In the Text Style dialog, create annotative styles:
  - `Legend big`: Arial font, Annotative enabled, Paper Text Height `0.004`.
  - `legend small`: Arial font, Annotative enabled, Paper Text Height `0.002`.
- In the lower-right title block table, insert text:
  - Upper cells (using `Legend big`): `Project:`, `Location:`, `Drawing name:`
  - Metadata cell (using `Standard` style with 1.5x line spacing): `Drawn:`, `Scale:`, `Date:`
- Create a rectangular layout viewport displaying the model space floor plan.
- Activate floating model space (`_.MSPACE`). Add a custom drawing scale `1:200` (1 paper unit = 200 drawing units) via `_SCALELISTEDIT` and set the viewport scale to `1:200`.

### Viewport Frame Hiding and PDF Output
- Test-plot `Layout1` to `example.pdf` using plotter configuration `DWG To PDF.pc3`.
- Assign the layout viewport entity to the frozen `viewport` layer (with Plot disabled) to hide the visible rectangular border frame, and dismiss the layer warning dialog.
- Plot the borderless `Layout1` sheet to `example 2.pdf`.

### Viewport Layer Overrides (Layout1)
- Activate model space in the `Layout1` viewport. In the Layer Properties Manager, apply viewport overrides:
  - Layer `Furnitures`: set **VP Freeze** to frozen (snowflake icon) and **VP Color** override to `164`.
  - Layer `staircase`: set **VP Color** override to `194`.

### Architectural Details Layout Tab (`details`)
- Right-click `Layout1`, select **Move or Copy...**, check **Create a copy**, position the copy after `Layout1`, and rename the tab to `details`.
- **Left Viewport (Door Detail):** Activate model space inside the existing viewport, zoom in closely on the door detail, and set the viewport scale to `1:16`. Return to paper space (`_.PSPACE`), assign the viewport to layer `viewport`, and use its bottom-right grip to resize its width narrower horizontally.
- **Right Viewport (Architectural Detail):** Draw a second rectangular layout viewport on the right half of the sheet. Activate floating model space, zoom into the architectural detail, and set its scale to `1:10`.
- **Detail Dimensions in Model Space:** Switch to Model space and set the annotation scale (`CANNOSCALE`) to `1:16`. Add linear dimensions to the door swing geometry: `0.90` m vertical, `0.90` m horizontal, `0.10` m frame, and `0.05` m frame. Update the Model space annotation scale to `1:10`.
- **Viewport Color Overrides (`details` layout):** On the `details` layout tab, activate floating model space in the left viewport (`1:16`) and set the **VP Color** override for layer `dimensions` to `86`. Activate the right viewport (`1:10`) and set its **VP Color** override for layer `dimensions` to `86`. Return to paper space to finalize the dual-detail presentation sheet.