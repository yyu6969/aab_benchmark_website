Schedule two calendar items in my Microsoft Outlook calendar: a one-time timed appointment titled "SBS Study Session" on September 19, 2019, and a yearly recurring all-day event titled "National Dessert Day" occurring every October 14 starting in 2019.

### Required Calendar Entries and Parameters

1. **Single Timed Appointment: "SBS Study Session"**
   - **Subject:** `SBS Study Session`
   - **Location:** `Library Meeting Room`
   - **Date:** `September 19, 2019` (Thursday, `9/19/2019` for both start and end dates)
   - **Time:** `11:30 AM` to `12:30 PM` (1-hour duration)
   - **Configuration:** Standard non-recurring timed appointment (`All day event` left unchecked, body left blank), saved to my Outlook calendar.

2. **Yearly Recurring All-Day Event: "National Dessert Day"**
   - **Subject:** `National Dessert Day`
   - **Location:** Left blank (empty, alongside a blank body)
   - **Start / Effective Date:** `October 14, 2019` (Monday, `10/14/2019`)
   - **Event Type:** `All day event` enabled/checked (setting start and end times to `12:00 AM` with a `1 day` duration)
   - **Recurrence Pattern:** `Yearly`, recurring every `1` year(s) on `October 14`, effective `10/14/2019` with no end-date modification (producing the Outlook summary `Occurs every October 14 effective 10/14/2019`), saved to my Outlook calendar.

### Demonstrated Workflow and Intermediate States

- **Initial Workspace State:** Microsoft Outlook begins in the Mail `Inbox` view for my account with the `Home` ribbon tab active, an email titled `SBS Test` selected in the reading pane, and `Thursday, September 12, 2019` (`Thu 9/12/2019`) as the current default calendar date.
- **Creating "SBS Study Session" from Mail View:**
  1. From the `Home` ribbon in Mail view, click `New Items` and select `Appointment` to open an `Untitled - Appointment` window.
  2. Enter `SBS Study Session` in the `Subject` field (updating the window title to `SBS Study Session - Appointment`) and `Library Meeting Room` in the `Location` field.
  3. Open the `Start time` calendar picker (initially showing `Thu 9/12/2019`) and select `September 19, 2019`, which updates both the `Start time` and `End time` date fields to `Thu 9/19/2019`.
  4. Open the `Start time` time dropdown (initially displaying `7:00 PM`), scroll up to daytime hours, and select `11:30 AM`; Outlook automatically adjusts the `End time` field to `12:00 PM`.
  5. Open the `End time` dropdown (initially highlighting `12:00 PM (30 minutes)`) and select `12:30 PM (1 hour)`, setting `End time` to `12:30 PM`.
  6. Click `Save & Close` on the Appointment ribbon to save the appointment and return to the `Inbox` view.
- **Creating "National Dessert Day" from Calendar View:**
  1. Click the `Calendar` button in the bottom-left navigation bar to switch to the `September 2019` monthly calendar grid (where `September 12` is highlighted and `SBS Study Session` appears on `Thursday, September 19`).
  2. Click `New Appointment` on the `Home` ribbon to open an `Untitled - Appointment` window (initially defaulting to `Thu 9/12/2019` from `11:00 AM` to `11:30 AM`).
  3. Enter `National Dessert Day` in the `Subject` field while leaving `Location` empty.
  4. Open the `Start time` date picker dropdown (showing `September 2019`), click the next-month arrow to advance to `October 2019`, and select `October 14, 2019`, updating the `Start time` date to `Mon 10/14/2019`.
  5. Check the `All day event` checkbox, converting the window to `National Dessert Day - Event` and changing the start and end times to `12:00 AM`.
  6. Click `Recurrence` (`Ctrl+G`) on the ribbon to open the `Appointment Recurrence` modal dialog (`Start: 12:00 AM`, `End: 12:00 AM`, `Duration: 1 day`), change the `Recurrence pattern` radio button from the default `Weekly` to `Yearly` (displaying `Recur every 1 year(s)` and `On: October 14`), and click `OK`. The editor updates to `National Dessert Day - Recurring Event` displaying `Occurs every October 14 effective 10/14/2019`.
  7. Click `Save & Close` to save the recurring event and return to the `September 2019` monthly calendar view.
- **Post-Save Calendar Navigation and Preview:**
  - After saving the second item, the monthly Calendar view is navigated forward from `September 2019` to `October 2020`, and the cursor hovers over the `National Dessert Day` entry on `Wednesday, October 14, 2020` (`10/14/2020`–`10/15/2020`), opening its event details preview card.

### Expected Outcomes, Method Flexibility, and Scope Notes

- **Persistent Outcomes:** My Outlook calendar contains both saved entries: the single appointment `SBS Study Session` at `Library Meeting Room` on `September 19, 2019` from `11:30 AM` to `12:30 PM`, and the yearly all-day recurring event `National Dessert Day` occurring every `October 14` effective `10/14/2019`.
- **Method and Order Flexibility:** Creating the first entry from the Mail `New Items` menu and the second after switching to `Calendar` view, using mouse dropdowns rather than direct keyboard input, and creating `SBS Study Session` prior to `National Dessert Day` are demonstrated execution choices rather than mandatory constraints; the two calendar entries have no dependency on each other.
- **Scope Qualification on Final Navigation:** Navigating the Calendar view to `October 2020` and hovering over the `October 14, 2020` instance of `National Dessert Day` confirms that the yearly recurrence populates future years, but the trajectory alone does not establish whether displaying/checking `October 2020` was an explicit user requirement or voluntary post-save verification by the demonstrator. Accordingly, saving the two configured calendar items represents the core required work, while navigating to `October 2020` to inspect the recurring event is an optional or secondary verification step unless specifically desired.