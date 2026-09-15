from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    groq_api_key = fields.Char(
        string='Groq API Key',
        config_parameter='ai_groq_chatbot.groq_api_key',
        groups='base.group_system',
    )
    groq_model = fields.Selection([
        (
            'openai/gpt-oss-20b',
            'GPT-OSS 20B (Fast)'
        ),
        (
            'openai/gpt-oss-120b',
            'GPT-OSS 120B (Best)'
        ),
    ], string='AI Model', default='openai/gpt-oss-20b')

    groq_system_prompt = fields.Char(
        string="System Prompt",
        config_parameter="ai_groq_chatbot.groq_system_prompt",
        default="You are a helpful Odoo ERP assistant. You can access and analyze Odoo data including sales, purchase, inventory, and manufacturing reports. When a user asks about reports or data, analyze it carefully and provide clear insights in Bengali or English as preferred.",
    )
    groq_max_tokens = fields.Integer(
        string='Max Tokens',
        config_parameter='ai_groq_chatbot.groq_max_tokens',
        default=1024,
    )
    groq_chatbot_enabled = fields.Boolean(
        string='Active Chatbot',
        config_parameter='ai_groq_chatbot.chatbot_enabled',
        default=True,
    )
