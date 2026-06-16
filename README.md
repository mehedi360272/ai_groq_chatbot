# AI Groq Chatbot — Odoo 18

Groq API ব্যবহার করে Odoo 18 এ AI Chatbot।

## ইনস্টলেশন

```bash
# 1. addons folder এ কপি করুন
cp -r ai_groq_chatbot /path/to/odoo/addons/

# 2. Odoo restart
sudo systemctl restart odoo
# অথবা
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

## System Prompt উদাহরণ

```
আপনি একটি বাংলাদেশী কোম্পানির Odoo 18 ERP সহকারী।
বাংলা ও ইংরেজি উভয় ভাষায় সাহায্য করুন।
সংক্ষিপ্ত ও স্পষ্ট উত্তর দিন।
```

## Odoo Version
✅ Odoo 18 Community & Enterprise
