In Adobe Premiere Pro, set up a new video editing project named "Justin Edit", assemble and edit a YouTube talking-head sequence named "YouTube" with B-roll overlays, a lower-third title graphic, visual effects, balanced background music, Essential Sound audio tags, and Lumetri Color grading, and configure 4K YouTube export settings.

### 1. Project Setup and Media Import
- Create a new project named **"Justin Edit"** (`Justin Edit.prproj`; observed in the default project directory `/Users/justin/Documents/Adobe/Premiere Pro/23.0` with `Project template: None`) and open the editing workspace without pre-selecting media on the initial Import screen.
- Import all five video files from the **`Video Assets`** folder on my **`Desktop`** (`File > Import...` in the demonstration, though any equivalent import method is valid):
  - `Camera-Recording.mp4`
  - `Screen-Recording.mp4`
  - `IMG_0133.MOV`
  - `IMG_0261.MOV`
  - `Test 1.mov`
  *(Note: Only `Camera-Recording.mp4`, `IMG_0133.MOV`, and `IMG_0261.MOV` are placed on the timeline in the observed workflow, while `Screen-Recording.mp4` and `Test 1.mov` remain in the Project bin.)*

### 2. Sequence Creation, Display Options, and Primary Footage Editing
- Create a new sequence from **`Camera-Recording.mp4`** (populating tracks `Video 1` / `V1` and `Audio 1` / `A1` with an initial duration of `00:05:16:15`), and rename the sequence from `Camera-Recording` to **"YouTube"** so both the Project panel item and Timeline tab reflect the name `YouTube`.
- Enable **Continuous Video Thumbnails** from the Timeline panel menu.
- *Source Monitor marking (demonstrated without timeline insertion)*: In the demonstration, `Camera-Recording.mp4` is also opened in the Source Monitor with an **In point** set at `00:01:23:18` and an **Out point** set at `00:02:03:06` (marked duration `00:00:39:19`), though this subclip is not inserted onto the timeline; whether preserving these Source Monitor markers on the master clip is required is uncertain.
- Trim and cut the primary talking-head clip **`Camera-Recording.mp4`** on `Video 1` and `Audio 1`. In the demonstrated sequence of edits:
  1. With the timeline playhead at `00:00:06:18`, ripple-trim the start (in-point) of `Camera-Recording.mp4` (holding `Ctrl/Cmd`), shortening total sequence duration from `00:05:16:15` to `00:04:44:25`.
  2. Trim the clip's end (out-point) leftward from `00:04:44:25` to `00:04:26:25`.
  3. Split `Camera-Recording.mp4` at `00:04:20:05` and `00:04:18:15` (demonstrated with `Ctrl/Cmd + K`) and ripple-delete (`Alt/Option + Delete`) the segment between `00:04:18:15` and `00:04:20:05`, reducing sequence duration to `00:04:25:05`.
  4. Split the clip using the Razor Tool (`C`) and Selection Tool (`V`)—with cuts observed near `00:04:12:00`, `00:03:50:08`, and `00:03:43:26`—and ripple-delete the `00:00:06:13` segment spanning **`00:03:43:26` to `00:03:50:08`**, reducing sequence duration to `00:04:18:22`.
  5. *Rough-cut discontinuity*: Between Steps 42 and 43, an unrecorded set of additional cuts further condenses `Camera-Recording.mp4` on `Video 1` / `Audio 1` from `00:04:18:22` to a multi-segment rough cut totaling **`00:01:26:26`** (including a first clip ending at `00:00:12:19`, a second clip from `00:00:12:19` to `00:00:16:09` of duration `00:00:03:21`, and subsequent segments ending at `00:01:26:26`).

### 3. B-Roll Overlay Placement on Video 2
- Place two video-only B-roll overlay clips onto track **`Video 2`** (`V2`) without adding audio to `Audio 2`:
  - **`IMG_0133.MOV`** (waterfall clip): Open in the Source Monitor, set an **In point at `00:00:29:09`**, mark an **Out point** yielding a selection duration of **`00:00:05:01`**, and drag the **video-only** stream (`Drag Video Only`) onto `Video 2`. *(Although the timeline playhead rests at `00:01:11:14` during the drag in Steps 47–48, the drag preview shows `00:00:11:09` and subsequent transition editing in Steps 82–88 shows `IMG_0133.MOV` positioned on `Video 2` starting near **`00:00:15:00`**.)*
  - **`IMG_0261.MOV`** (ocean surf/raft footage): Open in the Source Monitor, position the playhead at **`00:00:02:09`** (with a `00:00:20:17` source duration shown during placement), and place its video stream onto `Video 2` starting at approximately **`00:00:36:00`** (confirmed under the playhead at `00:00:36:19`).

### 4. Lower-Third Text Graphic ("JUSTIN BROWN")
- Using the **Type Tool (`T`)** in the Program Monitor at timecode **`00:00:00:16`**, create a Graphic text clip on track **`Video 2`** containing the uppercase text **`JUSTIN BROWN`**.
- Configure the **`JUSTIN BROWN`** text layer in the **Essential Graphics** panel (`Edit` tab):
  - **Font**: **`Oswald`** with style **`Bold`** (`Oswald Bold`, changed from `Myriad Pro`).
  - **Appearance > Background**: Enable **`Background`** (checked), set the background color swatch to **solid blue**, set **Background Opacity** to **`100%`** (from `75%`), and set **Background Size** to **`17.9`** (from `0.0`).
  - **Align and Transform**: Change vertical position (**Position Y**) from `614` to **`834`** (with horizontal position X observed at `664.2`) to place the title in the lower-third area.
- Trim the right edge (out-point) of the `JUSTIN BROWN` graphic clip on `Video 2` outward **past `00:00:05:00`** (observed remaining visible at `00:00:05:17`–`00:00:05:19`).
- *(Demonstration detail: Afterward, the user briefly views the `Browse` tab in Essential Graphics and selects `Window > Workspaces > Reset to Saved Layout` to restore the default panel layout before applying effects.)*

### 5. Video Transitions, Motion Framing, Blur, and Stabilization
- **Transition on `IMG_0133.MOV` (`Video 2`)**: Apply the **`Dip to White`** transition (`Effects > Video Transitions > Dissolve`) to the **in-point (head)** of `IMG_0133.MOV` on `Video 2` and drag its right edge leftward to shorten its duration. *(In the demonstration, `Cube Spin` from `Obsolete` was first applied and extended to `00:00:01:29` before being overwritten by `Dip to White`; an exploratory `Dip to Black` transition placed between two `Camera-Recording.mp4` clips on `Video 1` was also immediately deleted.)*
- **Motion Zoom on `Camera-Recording.mp4` (`Video 1`)**: Select the second `Camera-Recording.mp4` segment on `Video 1` (`00:00:12:19` to `00:00:16:09`, duration `00:00:03:21`) and, in **Effect Controls** under **`Motion`**, set **Scale** to **`117.0`** (from `100.0`; **Position** is also observed adjusted from `960.0, 540.0` to `960.0, 608.0` and `978.0, 608.0`).
- **Gaussian Blur on `Camera-Recording.mp4` (`Video 1`)**: Apply **`Gaussian Blur`** (`Video Effects > Blur & Sharpen`) to that same `00:00:12:19`–`00:00:16:09` `Camera-Recording.mp4` segment on `Video 1` and configure **Blurriness** to **`25.0`** (adjusted via `26.0`) with **Repeat Edge Pixels** **checked** (`Blur Dimensions: Horizontal and Vertical`). *(Whether leaving Gaussian Blur on this single talking-head segment is an intended final creative choice or a feature demonstration is somewhat ambiguous, though it remains applied in the observed project state.)*
- **Video Stabilization on `IMG_0261.MOV` (`Video 2`)**: Apply **`Warp Stabilizer`** (`Video Effects > Distort > Warp Stabilizer`) to the **`IMG_0261.MOV`** clip on `Video 2`.

### 6. Background Music, Level Balancing, and Essential Sound Tagging
- Import **`ES_San Pedro - Sugoi.mp3`** from my **`Downloads`** folder into the `Project: Justin Edit` panel.
- Place **`ES_San Pedro - Sugoi.mp3`** on track **`Audio 2`** (`A2`), align its start with the beginning of the sequence (**`00:00:00:00`**), and trim its out-point to **`00:01:26:26`** so it ends flush with the video clips on `Video 1` (keeping total sequence duration at `00:01:26:26`).
- Balance audio levels:
  - Keep track `Audio 1` track volume at **`0.0 dB`** and keep track `Audio 2` **unmuted** *(during mixing, track `A2` was temporarily muted and unmuted, `Window > Audio Track Mixer` was opened, and the `Audio 1` fader was briefly tested at `-6.3 dB` before resetting to `0.0 dB`)*. 
  - Adjust the clip volume rubberband of **`ES_San Pedro - Sugoi.mp3`** on track `Audio 2` to **`-31.48 dB`** (after intermediate adjustments at `-31.4 dB` and `-2.3 dB`).
- Open the **Essential Sound** panel (`Window > Essential Sound`) and assign audio types:
  - Select all audio clips on track **`Audio 1`** and tag them as **`Dialogue`**.
  - Select **`ES_San Pedro - Sugoi.mp3`** on track **`Audio 2`** and tag it as **`Music`**. *(At the transition into color grading in Step 157, the `Loudness` checkbox in Essential Sound for the `Music` clip is also observed enabled.)*

### 7. Lumetri Color Grading and Paste Attributes
- Select the **first clip** (`Camera-Recording.mp4` starting at `00:00:00:00`) on **`Video 1`** and open the **Lumetri Color** panel (`Window > Lumetri Color`).
- Under **Basic Correction** *(after briefly testing `Auto` at `Intensity: 77.3` and clicking `Reset` to return all sliders to neutral defaults)*, set:
  - **Exposure**: **`0.5`**
  - **Contrast**: **`31.5`** (adjusted via `6.1`)
  - **Temperature**: **`17.1`**
  - **Saturation**: **`119.3`**
  - *(Leave **Tint** at `0.0`.)*
- Copy the graded first clip (`Edit > Copy`), select the remaining primary clips on **`Video 1` and `Audio 1`** from approximately `00:00:15:00` to the end of the timeline (`00:01:26:26`), open the **Paste Attributes** dialog *(in the demonstration, `Edit > Remove Attributes...` was briefly clicked/dismissed before opening `Paste Attributes`)*, **uncheck `Motion`** under `Video Attributes` while keeping **`Scale Attribute Times`** **checked**, and click **`OK`** so the Lumetri Color grade is applied across the remaining talking-head clips without overwriting per-clip Motion framing.

### 8. Export Settings Configuration
- Switch to the **Export** workspace (`Export` tab in the top header).
- Under **Settings: Media File** (where **File Name** defaults to **`YouTube.mp4`** and **Format** is **`H.264`**), change **Preset** from `High Quality 1080p HD` to **`YouTube 2160p 4K Ultra HD`**.
- *Scope boundary note*: The demonstrated workflow scrolls down and hovers over the blue **`Export`** button (`Export immediately with the current settings`) without clicking it to render an output file; whether final task completion requires leaving the export settings configured in the Export workspace or executing the render to produce `YouTube.mp4` is not uniquely established by the final frame.