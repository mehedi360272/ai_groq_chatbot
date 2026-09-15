# AI Groq Chatbot — Odoo 18

AI Chatbot in Odoo 18 using Groq API.

## Features

- Chat widget in the systray, available on every page
- Quick Report buttons (Sales, Purchase, Stock, Manufacturing, Customers, Overdue) — collapsible via the "Short Report" header, click to expand/collapse
- Chat history saved per user, viewable under **AI Chatbot > Chat History** (managers only)
- Customizable system prompt and model
- Bengali + English support

## installation

```bash

# 1. Odoo restart
sudo systemctl restart odoo
# or
python odoo-bin -u ai_groq_chatbot -d your_database
```

## Setup

1. Go to **Apps > Update Apps List.**
2. search for **"AI Groq Chatbot"** and click **Install**.
3. Navigate to **Settings > General Settings > AI Chatbot** then:
   - Enter your Groq API Key (available for free from console.groq.com).
   - Select a model (GPT-OSS 20B for speed, GPT-OSS 120B for best quality).
   - Customize the System Prompt according to your requirements.
4. Click **Save** to apply the settings.

## Using Quick Reports

Click the chatbot icon in the systray to open the chat window. Under **Short Report**, tap any category button (Sales, Purchase, Stock, Manufacturing, Customers, Overdue) to get an instant summary. Click the "Short Report" header again anytime to collapse or re-expand the button list — it stays available throughout the conversation.

## System Prompt Example

```
You are an Odoo 18 ERP assistant for a Bangladeshi company.
Please help in both Bengali and English.
Please give short and clear answers.
```

## Odoo Version
Odoo 18 Community & Enterprise
