# AI Groq Chatbot — Odoo 18

AI Chatbot in Odoo 18 using Groq API.

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
   - Select a model (LLaMA 3.3 70B is recommended).
   - Customize the System Prompt according to your requirements.
4. Click **Save** to apply the settings.

## System Prompt Example

```
You are an Odoo 18 ERP assistant for a Bangladeshi company.
Please help in both Bengali and English.
Please give short and clear answers.
```

## Odoo Version
Odoo 18 Community & Enterprise
