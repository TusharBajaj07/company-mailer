# Company Mailer — Internship Recruitment Outreach

A small toolkit to run **internship-recruitment email campaigns to companies** from the
IIT Bombay Practical Training Cell, send via the **Gmail API** (OAuth2), and track replies.
Each email is a polished HTML invite with the institute logo and the assigned Internship
Coordinator's (IC) signature.

## Scripts & when to use each

| Script | Use case |
|--------|----------|
| **`mass_mail_from_sheet.py`** | **Main mass mailer.** Reads recipients straight from a **Google Sheet**, sends a personalised invite per company, and writes the Gmail `message ID` back into the sheet so re-runs skip anyone already mailed. Best when the team maintains the contact list collaboratively in Sheets. |
| **`bulk_mail_from_csv.py`** | Same campaign but driven by a **local `companies.csv`** instead of Sheets. Groups recipients by company and sends one email (using BCC for multiple addresses). Use when you just have a CSV and don't want to wire up the Sheets API. |
| **`test_single_mail.py`** | **Dry-run a single email** to yourself before a big send — verifies auth, the HTML template, and that the logo embeds correctly. Edit the `TO_EMAIL` / `COMPANY_NAME` / `IC_DETAILS` block at the top. |
| **`followup.py`** | Send a **threaded follow-up reply** to a company that hasn't responded. Prompts for the original Gmail `Message ID` and your reply text, then replies in the same thread (correct `In-Reply-To`/`References` headers). |
| **`track_status.py`** | **Reply tracking.** Reads a CSV containing a `message_id` column, checks each Gmail thread, and writes a `*_tracked.csv` showing whether each company replied and when. |

## Setup

### 1. Install dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Gmail (+ Sheets) API credentials
1. In the [Google Cloud Console](https://console.cloud.google.com/), create a project and
   **enable the Gmail API** (and the **Google Sheets API** if you'll use
   `mass_mail_from_sheet.py`).
2. Create an **OAuth client ID** of type *Desktop app* and download the JSON.
3. Save it as **`credentials.json`** here (see `credentials.json.example` for the shape).
4. On first run a browser opens to authorise; a `token.json` is cached afterwards.

> Sender address/name are hardcoded near the top of each script
> (`sender_email`, `sender_name`) — change them to your own.
> If you switch between Gmail-only and Gmail+Sheets scopes, delete `token.json` so it
> re-authorises (`mass_mail_from_sheet.py` does this automatically on startup).

### 3. Input data
- **`contacts.csv`** — IC directory. Columns: `name_IC, ph_no, linkedin_link`.
- For **`mass_mail_from_sheet.py`**: set `SPREADSHEET_ID` (and `SHEET_NAME`) at the top of the
  file, and give the sheet these column headers:
  `Name, Emails, Company Name, IC, message ID`.
- For **`bulk_mail_from_csv.py`**: maintain `companies.csv` (see `companies.example.csv`).
- For **`track_status.py`**: point it at a CSV with a `message_id` column (defaults to
  `emails.csv` → `emails_tracked.csv`).

See the `*.example.csv` files for exact formats.

## Run
```bash
python test_single_mail.py        # 1. verify setup with one test email
python mass_mail_from_sheet.py    # 2a. run the campaign from a Google Sheet
# or
python bulk_mail_from_csv.py      # 2b. run the campaign from companies.csv
python track_status.py            # 3. later: check who replied
python followup.py                # 3. nudge non-responders in-thread
```
A 2 s delay is added between sends to stay under Gmail rate limits.

---

## Working with the data files

Edit CSVs in **Excel, Google Sheets, or any text editor** — keep the header row exactly as-is
and save as CSV. Wrap any field containing a comma in double quotes.

### `contacts.csv` — the IC directory (used by `mass_mail_from_sheet.py`)
| Column | Meaning |
|--------|---------|
| `name_IC` | The IC's full name — the key the Sheet's `IC` column points to. |
| `ph_no` | Phone shown in the signature. |
| `linkedin_link` | LinkedIn URL shown in the signature. |

### The Google Sheet (for `mass_mail_from_sheet.py`)
Set `SPREADSHEET_ID` and `SHEET_NAME` at the top of the script, then give the sheet these
**exact** column headers:

| Header | Meaning |
|--------|---------|
| `Name` | Contact person's name (only the first name is used, as a greeting fallback). |
| `Emails` | Recipient address. |
| `Company Name` | Inserted into the subject line and email body. |
| `IC` | Must match a `name_IC` in `contacts.csv` — picks whose signature is used. |
| `message ID` | **Leave blank.** Auto-filled after sending (see below). |

The script reads top-to-bottom, skips any row that already has a `message ID`, sends to the
rest, and writes each new ID back into that row.

### `companies.csv` (for `bulk_mail_from_csv.py`)
A simpler local alternative with just two columns:
| Column | Meaning |
|--------|---------|
| `name` | Company name (inserted into the email). |
| `email` | One address, or **several separated by commas** — all are BCC'd in one email. |

See `companies.example.csv`. This script does **not** write message IDs back.

---

## Changing the Internship Coordinator (IC)

How you change the IC depends on the script:

- **`mass_mail_from_sheet.py`** — set the `IC` column **per row in the Google Sheet** to a name
  present in `contacts.csv`. Add/edit ICs by editing `contacts.csv`. The fallback (used when
  `IC` is blank/unmatched) is hardcoded in `get_ic_details()`.
- **`bulk_mail_from_csv.py`** — the IC is **hardcoded**, not read from a file. Change the name
  in `self.sender_name` (top of the class) and in the email body/signature inside
  `create_email_html()`.
- **`test_single_mail.py`** — edit the `IC_DETAILS` dictionary at the top of the file.

> The **sender mailbox** (`sender_email` / `sender_name`, e.g. `training@iitb.ac.in`) is the
> account the mail is actually sent from and is separate from the IC shown in the signature.

---

## Message IDs & reply tracking

Every email Gmail accepts gets a unique **message ID** (e.g. `19bf162d5c0bab17`). It is the
handle to that exact conversation (thread), and it powers the whole tracking workflow:

1. **`mass_mail_from_sheet.py`** writes each message ID back into the sheet's `message ID`
   column. This makes the campaign **resumable** — re-running it skips any row that already has
   an ID, so no company is mailed twice.
2. **`track_status.py`** takes a CSV with a `message_id` column (default `emails.csv`), looks up
   each thread, and writes a `*_tracked.csv` that marks every row as **`REPLIED` / `READ` /
   `UNREAD`** along with the reply count and the latest message's sender, date, and snippet —
   i.e. you can see at a glance who responded.
   *(To track sheet-based sends, export the sheet to CSV and rename the `message ID` column to
   `message_id`.)*
3. **`followup.py`** takes a single message ID and sends your reply **inside the original
   thread** (proper `In-Reply-To`/`References` headers), so the follow-up lands as a natural
   continuation rather than a fresh cold email.

So the typical loop is: **send → IDs saved → `track_status.py` to see replies → `followup.py`
to nudge the non-responders.**

---

## ⚠️ Security
Never commit `credentials.json`, `token.json`, `.env`, or your real `contacts.csv` /
`companies.csv` — they are gitignored. Revoke/rotate any credential that was ever committed
or shared (OAuth client in Google Cloud Console).
