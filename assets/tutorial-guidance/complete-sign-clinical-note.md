Complete, sign, and lock the clinical note for patient Gandalf Greyhame Wiz (displayed as Gandalf Greyhame Wz inside the note editor) in my drchrono workspace to document an evaluation for suspected appendicitis—recording gastrointestinal review of systems, abdominal physical exam findings, clinical assessment notes, a laboratory order, and treatment/consultation plan notes—so that the compiled note status becomes `Locked by Rendering Provider`.

### Target Patient and Note Context
- **Application and Initial Context**: drchrono web interface, starting from the appointments Schedule view (displaying `Exam 1` through `Exam 4` on `April 10, 2013`).
- **Patient Record**: Shown as `Gandalf Greyhame Wiz` in the `SOAP Notes Clinical Report` table and as `Gandalf Greyhame Wz` in the `Edit Clinical Note` header and `Allergy List` page.
- **Target Clinical Note**: The existing `H&P` clinical note associated with the `Edit (29)` link in the `SOAP Notes Clinical Report` table, which opens with `Chief Complaint` and `History of Present Illness` already populated and initial lock state `Status: Not Locked`.

### Required Clinical Note Updates
Within the patient's clinical note (under the `H&P` template sections), record the following structured selections and text entries:
- **Review of Systems**:
  - **`GI`**: Select `abdominal pain` from the dropdown options so it is added as a tag.
- **Physical Exam**:
  - **`Abdomen Abnormal`**: Select `tenderness RLQ` from the dropdown menu.
  - **`Abdomen Comments`**: Enter `possible appendicitis`.
- **Assessment**:
  - **`Notes`**: Enter `Gandalf presented with abdominal pain. Possible appendicitis.` in the lined text area.
- **Plan**:
  - **`Labs`**: Select `CBC with diff` from the dropdown menu so it is added as a tag.
  - **`Notes`**: Enter `Possible appendicitis. Consult Dr. Mayfield to determine if appendectomy is appropriate course of action.` in the lined text area in the lower portion of the Plan form.

*(Scope note on free-text fields: The strings above reflect the exact demonstrated wording in `Abdomen Comments`, `Assessment` `Notes`, and `Plan` `Notes`. Whether the underlying task requires exact verbatim text or equivalent clinical prose conveying the same symptoms, suspected appendicitis diagnosis, and Dr. Mayfield appendectomy consultation cannot be uniquely determined from the trajectory alone; preserving the exact demonstrated strings satisfies both.)*

### Finalization and Expected Outcome
- Compile/view the complete clinical note and execute `Sign & lock`.
- **Expected Final State**:
  - All `Review of Systems`, `Physical Exam`, `Assessment`, and `Plan` entries above are saved in the compiled clinical note document for `Gandalf Greyhame Wiz` (`Gandalf Greyhame Wz`).
  - The note status updates from `Status: Not Locked` to `Status: Locked by Rendering Provider` (with the `Sign & lock` button replaced by `Unlock`), and the complete locked clinical note document is rendered.

### Demonstrated Workflow, Intermediate States, and Execution Notes
1. **Opening the Clinical Note (Steps 0–3)**: From the `April 10, 2013` Schedule page, the demonstrator opened the top `Clinical` dropdown menu, clicked `Clinical Notes` (under `CLINICAL`) to load the `SOAP Notes Clinical Report`, and clicked `Edit (29)` in the `Clinical Note` column for `Gandalf Greyhame Wiz`, opening `Edit Clinical Note` in a new browser tab with `CC / History of Present Illness` selected under `H&P`. Note that `(29)` is an existing UI label/count on the report link rather than a parameter to configure, and reaching the same clinical note via another valid drchrono navigation path is equivalent.
2. **Read-Only Inspection of Vitals and Allergies (Steps 4–11)**: Prior to entering any findings, the demonstrator clicked `Vitals` to expand the `Patient Vitals` section (displaying Temperature, Pulse, Blood pressure, Respiratory rate, Oxygen saturation, Height, Weight, BMI, Pain, Head Circ., and Smoking status), selected `Medications & Allergies` in the left navigation sidebar, clicked `View Allergies` to open the `drchrono | Allergy List` tab (showing `Current Allergy List` and `Enter Allergy`), and switched back to the `drchrono | Edit Clinical Notes` tab without recording changes (after which the `View Allergies` row disappeared from the `Medications & Allergies` view on sidebar hover). These actions appear to be exploratory or contextual chart checks rather than required modifications, though it remains slightly uncertain whether reviewing vitals and allergies prior to completing the note was independently requested.
3. **Populating Sections and Locking (Steps 12–33)**: The demonstrator selected `Review of Systems`, `Physical Exam`, `Assessment`, and `Plan` sequentially in the left sidebar to enter the values listed above, scrolled to the top of the note to click `View Complete Note` in the sidebar (displaying the compiled document at `Status: Not Locked`), and scrolled down to click `Sign & lock`, transitioning the note to `Status: Locked by Rendering Provider`. The four clinical sections can be filled in any order, provided all documentation updates are completed before clicking `Sign & lock`.