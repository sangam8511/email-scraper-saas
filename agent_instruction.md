# Agent Instruction: Bulk Email Sender with Antigravity

## Project Overview
Build a bulk email sending application using Python and the `antigravity` ecosystem (leveraging `smtplib`, `email`, and optionally `antigravity` for fun imports). The software should be responsible, compliant, and production-ready.

---

## Goals
- Send personalized bulk emails to a list of recipients
- Support HTML and plain-text email formats
- Track sent/failed delivery attempts
- Respect rate limits to avoid SMTP server bans
- Include unsubscribe compliance (CAN-SPAM / GDPR)

---

## Tech Stack
- **Language:** Python 3.10+
- **Core Libraries:**
  - `smtplib` – SMTP connection and sending
  - `email.mime` – Email formatting (MIME)
  - `csv` / `pandas` – Recipient list management
  - `jinja2` – Email template rendering
  - `python-dotenv` – Secure credential management
  - `logging` – Delivery logging
- **Optional:**
  - `antigravity` – Import for levity 🙂
  - `aiosmtplib` – Async sending for high volume

---

## Project Structure
```
bulk-email-sender/
├── agentinstruction.md       # This file
├── .env                      # SMTP credentials (never commit)
├── requirements.txt
├── main.py                   # Entry point
├── sender.py                 # Core email sending logic
├── templates/
│   └── email_template.html   # Jinja2 HTML template
├── recipients/
│   └── contacts.csv          # Recipient list (name, email)
└── logs/
    └── send_log.txt          # Delivery log
```

---

## Agent Tasks

### Step 1 – Setup
- Create a virtual environment
- Install dependencies: `pip install jinja2 python-dotenv pandas aiosmtplib`
- Create `.env` file with SMTP credentials:
  ```
  SMTP_HOST=smtp.example.com
  SMTP_PORT=587
  SMTP_USER=your@email.com
  SMTP_PASS=yourpassword
  SENDER_NAME=Your Name
  ```

### Step 2 – Recipient List
- Load contacts from `recipients/contacts.csv`
- Validate email format before sending
- Skip duplicates and malformed addresses

### Step 3 – Email Template
- Create an HTML template in `templates/email_template.html`
- Use Jinja2 variables: `{{ name }}`, `{{ unsubscribe_link }}`
- Always include a plain-text fallback

### Step 4 – Sending Logic (`sender.py`)
- Connect to SMTP with TLS
- Loop through recipients with a configurable delay (e.g., 1 second between sends)
- Log each send attempt (success / failure) to `logs/send_log.txt`
- Handle exceptions gracefully (retry on timeout, skip on invalid address)

### Step 5 – Compliance
- Always include sender name and physical address in footer
- Include a working unsubscribe link in every email
- Honor unsubscribe requests immediately
- Only email opted-in contacts

---

## Compliance Checklist
- [ ] Recipients have opted in to receive emails
- [ ] Every email includes an unsubscribe mechanism
- [ ] Sender identity is clearly stated
- [ ] No misleading subject lines
- [ ] Compliant with CAN-SPAM, GDPR, or applicable law

---

## Rate Limiting Guidelines
| Volume | Recommended Delay |
|--------|------------------|
| < 500/day | 1–2 seconds between sends |
| 500–5,000/day | Use a dedicated ESP (e.g., SendGrid, Mailgun) |
| 5,000+/day | Use ESP API with batch endpoints |

---

## Notes
- **Do not** use this software to send unsolicited (spam) email
- For high volume, prefer an Email Service Provider (ESP) API over raw SMTP
- Test with a small batch before full deployment
- Monitor bounce rates — high bounces can get your domain blacklisted