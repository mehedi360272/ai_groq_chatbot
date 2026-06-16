# AI Groq Chatbot — Odoo 18

Groq API ব্যবহার করে Odoo 18 এ AI Chatbot।

## installation

```bash

# 1. Odoo restart
sudo systemctl restart odoo
# or
python odoo-bin -u ai_groq_chatbot -d your_database
```

## Setup

1. **Apps > Update Apps List** করুন
2. "AI Groq Chatbot" search করে **Install** করুন
3. **Settings > General Settings > AI Chatbot** section এ:
   - Groq API Key দিন ([console.groq.com](https://console.groq.com) থেকে বিনামূল্যে)
   - Model বেছে নিন (LLaMA 3.3 70B recommended)
   - System Prompt কাস্টমাইজ করুন
4. **Save** করুন

## System Prompt Example

```
You are an Odoo 18 ERP assistant for a Bangladeshi company.
Please help in both Bengali and English.
Please give short and clear answers.
```

## Odoo Version
✅ Odoo 18 Community & Enterprise
