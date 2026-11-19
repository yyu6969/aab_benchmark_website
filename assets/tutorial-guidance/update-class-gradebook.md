As the instructor managing my 'Organize and Educate' class in Google Classroom, the objective of this workflow is to mark a pending classwork question/assignment as reviewed, grade and provide private feedback on student work for the 'Week 1: Writing' assignment, return selected student submissions, export all class grades to Google Sheets, and annotate a specific cell in the exported gradebook spreadsheet with a comment.

### 1. Mark Pending Classwork as Reviewed
- **Required outcome:** Mark the assignment `'How do you feel about online learning?'` in my `'Organize and Educate'` class as reviewed so that it is removed from the `'To review'` list and placed under `'Reviewed'`.
- **Demonstrated operations and states:** Starting from my `'Organize and Educate'` class `'Stream'` page, click `'View all'` in the `'Upcoming'` card to open the `'To review'` page (where `'How do you feel about online learning?'` is listed under `'No due date'` with `0 Turned in` and `3 Assigned`), open its three-dots more options menu, and click `'Mark as reviewed'`. The demonstrator then selects the `'Reviewed'` tab to confirm `'How do you feel about online learning?'` appears under `'No due date'`. Navigating via the `'Upcoming'` card and checking the `'Reviewed'` tab afterward are demonstrated navigation/verification mechanics rather than mandatory UI paths.

### 2. Grade, Comment on, and Return 'Week 1: Writing' Submissions
- **Initial assignment state:** In `'Organize and Educate'`, the `'Week 1: Writing'` assignment is worth `8` points total and initially has `4` student roster entries: `1 Turned in` (`Casey Boehm`) and `3 Assigned` (a second `Casey Boehm` entry, `Caitie Instone`, and `Hannah Koenig`). Prior to grading, the demonstration includes an exploratory navigation detour from `'Week 1: Writing'` `'Student work'` back to `'Stream'`, `'Grades'`, and `'Week 1: Reading'` `'Student work'` before returning to `'Week 1: Writing'` `'Student work'`, without modifying `'Week 1: Reading'`.
- **Grade and comment on `Casey Boehm`'s `'Turned in'` submission:**
  - Open `Casey Boehm`'s `'Turned in'` submission (`'Casey Boehm - Sentence Writing'`) in the grading workspace (closing the `'Open in a new window'` modal prompt if shown).
  - Assign rubric scores across all four criteria to establish a draft score of `7/8` (`'7/8 Draft'`, status `'Not returned'`):
    - `Sentence Writing`: `2/2`
    - `Organization`: `2/2`
    - `Punctuation`: `2/2`
    - `Spelling`: `1/2`
  - Post the individual private comment `'Awesome work sounding out your words and using sight words!'` in the `'Private comments'` panel.
- **Intermediate workspace navigation and `Hannah Koenig` score state:**
  - Using the `'Next student'` button in the grading workspace, the demonstrator steps to the `'Assigned'` entry for `Casey Boehm` (unscored `/2` rubric inputs, unedited worksheet template, disabled `'Return'` button) and then to `Hannah Koenig`'s submission, which shows an annotated laptop keyboard diagram and selected rubric levels totaling `0/8` with status `'0/8 Saving...'` and an enabled `'Return'` button, before closing the grading workspace back to the `'Student work'` overview.
  - *Scope and causal uncertainty:* No explicit rubric-selection action row is recorded for `Hannah Koenig`, so it is uncertain whether assigning a `0/8` rubric score to `Hannah Koenig` occurred during the compressed step transition as an intended grading requirement or reflected a pre-existing/incidental state.
- **Return selected submissions with a batch private comment:**
  - On the `'Week 1: Writing'` `'Student work'` page, select three student entries:
    1. `Casey Boehm` under `'Turned in'`
    2. `Casey Boehm` under `'Assigned'`
    3. `Hannah Koenig` under `'Assigned'`
    (Leave `Caitie Instone` under `'Assigned'` unselected.)
  - Click `'Return'`, confirm `'Return'` in the `'Return unsubmitted assignments?'` modal dialog, enter the private comment `'Super sentence writing!'` in the `'Return work to 3 students?'` confirmation dialog, and click `'Return'`.
  - **Resulting state:** `3` submissions are returned, updating `'Week 1: Writing'` to `0 Turned in`, `1 Assigned` (`Caitie Instone`), and `3 Graded` (both `Casey Boehm` entries and `Hannah Koenig`), each with the returned private comment `'Super sentence writing!'`.

### 3. Intermediate Gradebook and Version History Inspection (Uncertain Requirement Scope)
- **Demonstrated inspection:** After returning the `'Week 1: Writing'` submissions, the demonstrator opens the class `'Grades'` tab, clicks the three-dots menu on `Casey Boehm`'s `'Week 1: Writing'` grade cell (`7/8`, where `'Return'` is disabled), and selects `'View submission'` to open `'Casey Boehm - Sentence Writing'`. From there, the demonstrator clicks `'Last edit was made ... by Casey Boehm'` (`'Open version history'`), scrolls down to inspect the four student sentences with green revision highlights in `'August 6, 6:55 PM Current version'` (`'Total: 8 edits'`), selects the earlier `'August 6, 6:55 PM'` revision entry (`'Total: 1 edit'`, which displays a `'Restore this version'` button that is not clicked), switches back to `'August 6, 6:55 PM Current version'` (`'Total: 8 edits'`), and exits back to the `'Student work'` page.
- *Scope uncertainty:* Because no version is restored and no persistent state changes occur during this inspection, it is unresolved whether reviewing `Casey Boehm`'s submission version history was an independently requested verification task or an exploratory/demonstrative walkthrough; it should not be treated as an unconditional persistent requirement.

### 4. Export All Class Grades to Google Sheets and Annotate Cell D7
- **Export grades to Google Sheets:** Export all grades for `'Organize and Educate'` to Google Sheets by opening the settings gear menu on the `'Student work'` page and selecting `'Copy all grades to Google Sheets'` (rather than `'Download all grades as CSV'` or `'Download these grades as CSV'`).
- **Generated spreadsheet artifact:** This export creates and opens a Google Sheets spreadsheet auto-titled `'Grades Organize and Educate 08-06-2020'` containing my class roster and updated assignment grades (with cell `E9` initially selected, followed by an incidental click on cell `E6`). The `'08-06-2020'` date suffix reflects Google Classroom's automatic export naming on the demonstration date rather than a manual rename.
- **Comment on cell `D7`:** In the exported `'Organize and Educate'` grades spreadsheet, add and submit a comment on `cell D7` (which contains a formula in the formula bar) with the exact text `'Needs to make corrections'`—demonstrated by right-clicking `cell D7`, clicking `'Comment'` in the context menu, typing `'Needs to make corrections'`, and clicking `'Comment'` to publish.

### 5. Sequence and Dependencies
1. Scoring `Casey Boehm`'s `'Turned in'` `'Week 1: Writing'` submission (`7/8`) must precede returning `Casey Boehm`'s submission so the graded score is returned, and posting `'Awesome work sounding out your words and using sight words!'` preceded sending the batch return comment `'Super sentence writing!'`.
2. Completing the `'Week 1: Writing'` grading and returns must precede running `'Copy all grades to Google Sheets'` so that the exported Google Sheets gradebook captures the updated `'Week 1: Writing'` grades.
3. Running `'Copy all grades to Google Sheets'` must precede adding the comment `'Needs to make corrections'` to `cell D7` in the generated spreadsheet.
4. Marking `'How do you feel about online learning?'` as reviewed is independent of `'Week 1: Writing'` grading order, and equivalent UI navigation or comment-insertion methods in Google Classroom and Google Sheets may be used where they produce the same persistent results.