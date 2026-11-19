This Reference Guidance reconstructs the complete Salesforce CRM setup, sales-pipeline execution, and analytics workflow demonstrated across steps 0–308. The overarching objective is to register and activate my new Salesforce Developer Edition organization, switch into the `Sales` application, manage an end-to-end lead-to-cash cycle for company `ABC` (converting a new lead into an account, contact, and opportunity, adding a second contact, and closing the `$100,000` opportunity as `Closed Won`), configure a filtered `My Open Leads` list view, build and chart a public `Closed Won Opportunities` report grouped by `Lead Source`, assemble and refresh a `Closed Won Dashboard` from that report, and subscribe to receive dashboard updates every Monday at `7:00 AM`.

### 1. Salesforce Developer Edition Registration and Account Activation
Provision and activate my new Salesforce Developer Edition account and sign in to Salesforce Lightning:
- **Signup Form Submission (Demonstrated in Steps 0–16):**
  - Starting on the Salesforce Developer Edition registration page (`'Sign up for your Salesforce Developer Edition'`, initially showing validation prompts `'Enter your first name'` and `'Please select an item in the list.'`), populate the form with these exact values:
    - **First Name:** `Emily`
    - **Last Name:** `Call`
    - **Email:** `sfemilycall@gmail.com`
    - **Role:** `Developer` (chosen from the `Role` dropdown with placeholder `'Your job role'`)
    - **Company:** `Call Solutions LLC`
    - **Country/Region:** `United States` (selecting `United States` dynamically reveals the `State/Province` dropdown)
    - **State/Province:** `Utah`
    - **Postal Code:** `98002`
    - **Username:** `EEC@callcompany.com`
    - **Terms Agreement:** Check the agreement checkbox (`Main Services Agreement – Developer Services and Salesforce Program Agreement`).
  - Click `Sign me Up` to submit the registration, transitioning to `https://developer.salesforce.com/signup/account-verification` (`'Almost there...'` / `'Please check your email to verify your account.'`).
- **Email Verification and Password Setup (Demonstrated in Steps 17–21):**
  - Switch to my Gmail browser tab, open the `'Welcome to Salesforce: Verify your account'` email, and click `Verify Account` to open the Salesforce `'Change Your Password'` page in a new tab.
  - Enter matching valid passwords satisfying Salesforce's password complexity requirements into `New Password` and `Confirm New Password` (characters are masked in the UI; all requirement indicators turn green).
  - Retain the default `Security Question` selection and enter [redacted] in the `Answer` field, then click `Change Password`.
  - **Outcome:** Account activation completes and logs in to Salesforce Lightning `Setup Home` (displaying `Emily Call` in `Most Recently Used`). *(Uncertainty: The evidence does not establish whether a specific password string was externally prescribed or any compliant password sufficed, nor whether retaining the default security question with answer [redacted] was explicitly required.)*

### 2. Accessing the Sales Application and Inspecting Contact Mr. John Bond
Enter the `Sales` workspace from `Setup Home` and inspect the existing sample contact record for `Mr. John Bond`:
- **Switch to the Sales Application (Demonstrated in Steps 22–25):** Open the 3x3 `App Launcher` menu in the top navigation bar, type `sales` in `Search apps and items...`, and click `Sales` to load the `Seller Home` dashboard (displaying navigation tabs including `Home`, `Opportunities`, and `Leads`).
- **Inspect Contact `Mr. John Bond` (Demonstrated in Steps 32–39; Scope Qualification Below):**
  - In the top `Global Search` bar (`Search...`), enter `john`, click `'Show more results for "john"'` from the search overlay, and click `John Bond` under `Recommended Result` on the `Search Results` page to open the `Mr. John Bond` contact record.
  - Switch from the initial `Related` tab to the `Details` tab to view his loaded contact fields (`Name`, `Title`, `Account Name` `Grand Hotels & Resorts Ltd`, `Phone`, `Email`, and `Address`).
  - *Scope Uncertainty and Non-Mutating Detour:* Prior to searching (steps 26–31), the demonstrator opened and immediately closed (`X`) the `App Launcher` -> `View All` modal without selecting anything. Furthermore, the trajectory does not uniquely establish whether viewing `Mr. John Bond`'s `Details` tab was an explicitly requested lookup/inspection subtask or exploratory browsing of pre-populated Developer Edition sample data before creating new CRM records.

### 3. Lead Creation, Conversion, Contact Association, and Opportunity Closing for ABC
Execute the CRM sales pipeline for `ABC` by creating and converting lead `Jane Doe`, adding contact `John Doe`, and closing opportunity `ABC- Initial Contract` at `$100,000`:
1. **Create Lead `Jane Doe` (Demonstrated in Steps 40–60):**
   - Navigate to `Leads` (`My Leads` Lead Intelligence View) and click `New` to open the `New Lead` modal.
   - Populate the following exact fields:
     - **First Name:** `Jane`
     - **Last Name:** `Doe`
     - **Company:** `ABC`
     - **Lead Source:** `Web` (updated from `--None--`)
     - **Industry:** `Education` (updated from `--None--`)
     - **Lead Status:** `Working - Contacted` (updated from default `Open - Not Contacted`)
   - Leave optional address, additional, and description fields blank/default and click `Save`, producing toast `'Lead "Jane Doe" was created.'` and opening the `Jane Doe` Lead record (`Lead Owner`: `Emily Call`).
2. **Convert Lead `Jane Doe` (Demonstrated in Steps 74–82):**
   - *Non-Mutating Detours (Steps 61–73):* Viewing `Details`, opening and canceling `Change Lead Owner`, switching to `Related`/`Activity`, and opening then closing the docked `Email` composer without sending made no persistent changes and are not required.
   - Initiate lead conversion on `Jane Doe` (demonstrated by clicking `Converted` on the lead status path and clicking `'Select Converted Status'` to open the `Convert Lead` modal) with these target settings:
     - **Account:** Create new Account `ABC`
     - **Contact:** Create new Contact `Jane Doe`
     - **Opportunity:** Expand `Opportunity` and set **Opportunity Name** to `ABC- Initial Contract` (updated from default `ABC-`; exact spacing has no space before `-` and one space after `-`)
     - **Converted Status:** `Closed - Converted`
   - Click `Convert` to display `'Your lead has been converted'` with cards for Account `ABC`, Contact `Jane Doe`, and Opportunity `ABC- Initial Contract` (created at initial Stage `Prospecting`, default Close Date `6/30/2024`, and carrying over `Lead Source = Web`). Clicking `ABC` (step 82) opens the `ABC` Account record page.
3. **Create Contact `John Doe` Under Account `ABC` (Demonstrated in Steps 96–102):**
   - *Non-Mutating Detours (Steps 83–95):* No-op inline editing/saving on `ABC`'s `Details` tab and opening/canceling `New Account` from `Accounts` made no persistent changes.
   - Create a new contact (demonstrated via `Contacts` -> `New`, where `My Contacts` initially listed 21 contacts; creating from `ABC`'s `Related` Contacts list is an equivalent path) with exact values:
     - **First Name:** `John`
     - **Last Name:** `Doe`
     - **Account Name:** `ABC` (selected from `Recent Accounts`)
   - Click `Save` to create the `John Doe` Contact record linked to Account `ABC` (`Contact Owner`: `Emily Call`).
4. **Update Opportunity `ABC- Initial Contract` to `$100,000` and `Closed Won` (Demonstrated in Steps 103–142):**
   - Navigate to `Opportunities` and open `ABC- Initial Contract`.
   - **Amount Update (Steps 109–116):** On the `Details` tab, inline-edit `Amount` to `100000` and click `Save`. Intermediate state: `Amount` formats as `$100,000.00`, and while Stage is still `Prospecting` (10% probability), `Expected Revenue` temporarily calculates as `$10,000.00`.
   - *Non-Mutating Detours (Steps 117–132):* Opening and canceling the header `Edit` modal, `Description` inline edit, and `Share` modal made no changes.
   - **Stage Update (Steps 133–142):** Advance **Stage** to `Closed Won` (demonstrated by clicking `Closed` on the sales path, clicking `'Select Closed Stage'` to open `'Close This Opportunity'`, selecting `Closed Won` in the `Stage` dropdown, and clicking `Save`; updating `Amount` and `Stage` together via standard record editing would reach the same persistent state).
   - **Outcome:** Banner `'Stage changed successfully.'` appears, leaving `ABC- Initial Contract` at **Amount** = `$100,000.00` and **Stage** = `Closed Won`.

### 4. Creating and Filtering the "My Open Leads" List View
Create a custom lead list view named `My Open Leads` and filter it to display only open, unconverted leads:
- **Create List View (Demonstrated in Steps 143–152):**
  - Navigate to `Leads` (initially displaying `22` leads in `My Leads`), open `List View Controls` (gear icon), and click `Create New View`.
  - Set **Lead View Name** to `My Open Leads`, which auto-populates **Lead View API Name** as `My_Open_Leads`, keep `Who sees this lead view?` set to `Only I can see this view`, and click `Save` (toast `'Lead view My Open Leads was created.'`, loading `22` lead records).
- **Configure Filter Criteria (Demonstrated in Steps 153–185):**
  - Click the `filter` button to open the `Filters` side panel (which retains default `Created Date` and `Owner` filters under `'Matching all of these filters'`).
  - Add two field filters:
    1. **Field:** `Converted`, **Operator:** `equals`, **Value:** `False` (demonstrated by clicking `Add Filter`, selecting `Converted`, clicking `Done`, and clicking `Save`, which reloaded `22` Total Leads).
    2. **Field:** `Lead Status`, **Operator:** `not equal to`, **Value:** `Closed - Converted` and `Closed - Not Converted` (`2 options selected`; demonstrated by clicking `Add Filter`, configuring both closed statuses, clicking `Done`, and clicking `Save`).
  - **Outcome:** Saving the complete filter criteria updates `My Open Leads` from `22` to **`15`** filtered leads (excluding converted lead `Jane Doe` and any closed sample leads). Closing the `Filters` sidebar (`X` at step 185) and saving after each filter individually rather than once at the end are UI execution details.

### 5. Building, Saving, and Charting the "Closed Won Opportunities" Report
Create a public `Opportunities` summary report named `Closed Won Opportunities` grouped by `Lead Source` with `Amount` summed, and configure a Donut chart visualization:
- **Report Creation and Column Customization (Demonstrated in Steps 186–203 & 224–229):**
  - Go to `Reports` -> `New Report`, choose the **`Opportunities`** report type, and click `Start Report` to open Report Builder (where `'Update Preview Automatically'` was toggled `on` as a builder convenience).
  - Remove three default columns from the report: **`Owner Role`** (removed via column header menu -> `Remove Column`), **`Age`** (`# Age`, removed via the Outline `Columns` list), and **`Next Step`** (removed via the Outline `Columns` list).
  - Add **`Last Modified Date`** to `Columns` (demonstrated via `Outline` -> expanding `Fields` -> clicking `Last Modified Date`, inserting it between `Stage` and `Fiscal Period`, then collapsing `Fields`).
- **Report Filters, Grouping, and Summary (Demonstrated in Steps 204–223 & 230–236):**
  - In `Filters`, set the **`Close Date`** standard filter **Range** to **`All Time`** (replacing `Current FQ`) and click `Apply`.
  - Add a field filter for **`Stage`** **`equals`** **`Closed Won`** and click `Apply`.
  - In `Outline` under `GROUP ROWS`, group rows by **`Lead Source`**.
  - On the **`Amount`** column header menu, choose `Summarize` -> **`Sum`**, producing `Lead Source` subtotals and a grand total of **`$3,745,000.00`**.
- **Naming, Public Folder Placement, and Run-View Donut Chart (Demonstrated in Steps 237–256):**
  - Rename the report to **`Closed Won Opportunities`** and click `Save & Run`. In `Save Report` (where `Report Unique Name` auto-generated as `Closed_Won_Opportunities_jM0`, an automatic API suffix rather than a required value), change **Folder** from `Private Reports` to **`Public Reports`** via `Select Folder`, and click `Save`.
  - **Saved Report Outcome:** Toast `'Report "Closed Won Opportunities" was saved'` appears, and the report runs displaying **`19`** Closed Won opportunity records grouped by `Lead Source` (including the `$100,000.00` `ABC- Initial Contract` under `Web`, bringing `Web` to `$335,000` and the grand total to **`$3,745,000.00`**).
  - **Chart Visualization (Steps 250–256):** On the saved report run view, click `Add Chart` (initially a Horizontal Bar chart), open `Chart Properties` (gear icon), select **`Donut`** under `Display As` (`Value` = `Sum of Amount`, `Sliced By` = `Lead Source`, `Show Values` = `True`, `Show Percentages` = `False`, `Combine Small Groups into "Others"` = `True`, central total **`3.7M`**), and close `Chart Properties`. *(Uncertainty: Because the chart was configured in the interactive run view without reopening Report Builder to re-save the report definition, it is uncertain whether run-view chart configuration satisfied an independent report-chart requirement, whether persisting the chart in Report Builder would also be expected, or whether this previewed the chart prior to dashboard creation.)*

### 6. Building, Refreshing, and Subscribing to the "Closed Won Dashboard"
Create `Closed Won Dashboard` with Metric and Donut chart widgets sourced from `Closed Won Opportunities`, refresh its view-mode data, and schedule a weekly Monday `7:00 AM` subscription:
- **Create Dashboard and Add Components (Demonstrated in Steps 257–292):**
  - Navigate to `Dashboards` -> `New Dashboard`, enter **Name** `Closed Won Dashboard`, leave **Folder** at the default `Private Dashboards`, and click `Create`.
  - **Metric Widget (Steps 266–279):** Click `+ Widget` -> `Chart or Table`, select `Closed Won Opportunities`, set `Display As` to **`123` (Metric)** (`Measure` = `Sum of Amount`, `Display Units` = `Shortened Number`, `Title` = `Closed Won Opportunities`, showing **`$3.7M`**), and click `Add`. On the top-left of the grid, resize the widget from `2x2` to **4 columns wide by 3 rows tall (`4x3`)** so the full title is visible.
  - **Donut Chart Widget (Steps 280–292):** Click `+ Widget` -> `Chart or Table`, select `Closed Won Opportunities` (under `All Folders` -> `Public Reports`), set `Display As` to **`Donut`** (`Value` = `Sum of Amount`, `Sliced By` = `Lead Source`, `Display Units` = `Shortened Number`, `Title` = `Closed Won Opportunities`, showing **`$3.7M`** sliced by `Lead Source`), click `Add`, and position it immediately **to the right of the Metric widget** along the top row. *(Exact `4x3` sizing and side-by-side placement are preserved as demonstrated layout details that may reflect visual formatting preferences.)*
- **Save, Exit Editor, and Refresh (Demonstrated in Steps 293–297):**
  - Click `Save` (`'Dashboard saved'`), click `Done` to enter view mode (where the left Metric component initially read `'No data. Try refreshing the dashboard.'` while the Donut widget showed `'$3.7M'`), and refresh the dashboard (step 297) so both components render **`$3.7M`**.
- **Configure Weekly Subscription (Demonstrated in Steps 298–308):**
  - Click `Subscribe` in the dashboard header to open `Edit Subscription`.
  - Set **Frequency** to **`Weekly`**, set **Days** to **`Mon`** only (deselecting `Sat` from the initial `Mon` + `Sat` selection), set **Time** to **`7:00 AM`** (changed from `12:00 PM`), keep the email notification option checked, and click `Save`.
  - **Final Outcome:** `Edit Subscription` closes and `Closed Won Dashboard` displays the green confirmation banner **`'You started a dashboard subscription.'`** above the populated `$3.7M` Metric and Donut chart components.

### 7. Workflow Sequence, Cross-Stage Dependencies, and Flexible Execution Details
- **Genuine Dependencies:** Registering and verifying my Developer Edition org (steps 0–21) must precede all CRM operations. Lead `Jane Doe` must be created and converted via Salesforce lead conversion (rather than standalone manual record creation) before finalizing downstream views and analytics because conversion marks `Jane Doe` as `Converted = True` / `Closed - Converted` (excluding her from the `15` records in `My Open Leads`) and propagates `Lead Source = Web` onto `ABC- Initial Contract`. Likewise, updating `ABC- Initial Contract` to `$100,000` and `Closed Won` must precede final report/dashboard data evaluation so its `$100,000` value is included in the `$3,745,000.00` (`$3.7M`) total and `$335,000` `Web` slice. Finally, `Closed Won Opportunities` must be saved before adding its components to `Closed Won Dashboard`, which must be created before subscribing.
- **Flexible Execution Paths:** Navigation routes, column removal method (table header dropdown vs. `Outline` panel), order of report customizations before `Save & Run`, saving list-view filters individually vs. together, and updating opportunity `Amount` and `Stage` separately vs. in one edit are demonstrated UI mechanics rather than strict constraints.