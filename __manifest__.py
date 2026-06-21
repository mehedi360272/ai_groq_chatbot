{
    'name': 'AI Groq Chatbot',
    'version': '18.0.2.0.0',
    'category': 'Tools',
    'summary': 'Chatbot in Odoo with Groq AI',
    'description': """
        AI Chatbot in Odoo using Groq API.
        - Chat widget on any page (Systray)
        - Chat history saving
        - Customize system prompt
        - LLaMA / Mixtral model support
    """,
    'author': 'Custom Dev',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/chat_history_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ai_groq_chatbot/static/src/css/chatbot.css',
            'ai_groq_chatbot/static/src/xml/chatbot_widget.xml',
            'ai_groq_chatbot/static/src/js/chatbot.js',
        ],
    },
    'installable': True,
    'application': False,
    'images': ['static/description/icon.png'],
    'license': 'LGPL-3',
}
