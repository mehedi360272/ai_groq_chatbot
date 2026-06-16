import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

# Keywords যেগুলো দেখলে Odoo data fetch করবো
REPORT_KEYWORDS = [
    'sale', 'sales', 'invoice', 'বিক্রয়', 'ইনভয়েস',
    'purchase', 'vendor', 'bill', 'ক্রয়', 'বিল', 'সাপ্লায়ার',
    'stock', 'inventory', 'product', 'স্টক', 'পণ্য', 'ইনভেন্টরি',
    'manufacturing', 'production', 'mrp', 'ম্যানুফ্যাকচারিং', 'উৎপাদন',
    'customer', 'client', 'কাস্টমার', 'গ্রাহক',
    'overdue', 'unpaid', 'due', 'বকেয়া', 'অপরিশোধিত',
    'report', 'রিপোর্ট', 'তথ্য', 'data', 'summary',
]


def _needs_report(text):
    """User message-এ report keyword আছে কিনা check করে।"""
    lower = text.lower()
    return any(kw in lower for kw in REPORT_KEYWORDS)


class AiChatbotController(http.Controller):

    @http.route('/ai_chat/send', type='json', auth='user', methods=['POST'])
    def send_message(self, messages, session_id=None, **kwargs):
        try:
            if not messages or not isinstance(messages, list):
                return {'error': 'The messages field is required.'}

            for msg in messages:
                if msg.get('role') not in ('user', 'assistant'):
                    return {'error': 'Invalid message role'}
                if not msg.get('content', '').strip():
                    return {'error': 'Empty message'}

            # সর্বশেষ user message
            last_user_msg = ''
            for m in reversed(messages):
                if m.get('role') == 'user':
                    last_user_msg = m.get('content', '')
                    break

            is_admin = request.env.user.has_group('base.group_system')

            # ── Step 1: Fixed report commands চেক করো ──
            if _needs_report(last_user_msg):
                report_svc = request.env['odoo.report.service']
                report_result = report_svc.get_report(last_user_msg, is_admin=is_admin)

                if report_result.get('found'):
                    report_text = report_result['text']

                    # Report data + user question → Groq-এ পাঠাও enriched context দিয়ে
                    enriched_messages = list(messages)
                    enriched_messages.append({
                        'role': 'user',
                        'content': (
                            f"[Odoo System Data]\n{report_text}\n\n"
                            f"[User Question]\n{last_user_msg}\n\n"
                            "Answer the user's question by looking at the Odoo data above. "
                            "Present the data clearly. Answer in English."
                        ),
                    })

                    groq = request.env['groq.service']
                    result = groq.call_groq(enriched_messages, session_id=session_id)
                    # Original report data-ও attach করো (UI-তে দেখানোর জন্য)
                    if result.get('success'):
                        result['report_data'] = report_text
                    return result

            # ── Step 2: AI fallback (general questions) ──
            groq = request.env['groq.service']
            result = groq.call_groq(messages, session_id=session_id)
            return result

        except Exception as e:
            _logger.error('AI Chat error: %s', e)
            return {'error': str(e), 'success': False}

    @http.route('/ai_chat/history', type='json', auth='user', methods=['POST'])
    def get_history(self, session_id, **kwargs):
        try:
            messages = request.env['ai.chat.message'].sudo().search([
                ('history_id.session_id', '=', session_id),
                ('history_id.user_id', '=', request.env.user.id),
            ], order='create_date asc')
            return {
                'messages': [
                    {'role': m.role, 'content': m.content}
                    for m in messages
                ]
            }
        except Exception as e:
            return {'error': str(e)}

    @http.route('/ai_chat/clear', type='json', auth='user', methods=['POST'])
    def clear_history(self, session_id, **kwargs):
        try:
            history = request.env['ai.chat.history'].sudo().search([
                ('session_id', '=', session_id),
                ('user_id', '=', request.env.user.id),
            ])
            history.unlink()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}

    @http.route('/ai_chat/set_key', type='json', auth='user', methods=['POST'])
    def set_api_key(self, api_key, **kwargs):
        try:
            if not request.env.user.has_group('base.group_system'):
                return {'error': 'Admin access required'}
            if not api_key or not api_key.strip().startswith('gsk_'):
                return {'error': 'Invalid API key format (must start with gsk_)'}
            ICP = request.env['ir.config_parameter'].sudo()
            ICP.set_param('ai_groq_chatbot.groq_api_key', api_key.strip())
            saved = ICP.get_param('ai_groq_chatbot.groq_api_key', '')
            if saved == api_key.strip():
                return {'success': True, 'message': 'API key saved successfully!'}
            return {'error': 'Save failed'}
        except Exception as e:
            return {'error': str(e)}

    @http.route('/ai_chat/check_config', type='json', auth='user', methods=['POST'])
    def check_config(self, **kwargs):
        try:
            if not request.env.user.has_group('base.group_system'):
                return {'error': 'Admin access required'}
            ICP = request.env['ir.config_parameter'].sudo()
            api_key = ICP.get_param('ai_groq_chatbot.groq_api_key', '')
            model = ICP.get_param('ai_groq_chatbot.groq_model', '')
            enabled = ICP.get_param('ai_groq_chatbot.chatbot_enabled', '')
            return {
                'api_key_set': bool(api_key),
                'api_key_preview': f'...{api_key[-6:]}' if api_key else 'EMPTY',
                'model': model,
                'enabled': enabled,
            }
        except Exception as e:
            return {'error': str(e)}

    @http.route('/ai_chat/quick_report', type='json', auth='user', methods=['POST'])
    def quick_report(self, report_type, **kwargs):
        """Direct report endpoint — JS quick buttons থেকে call করা যাবে।"""
        try:
            is_admin = request.env.user.has_group('base.group_system')
            report_svc = request.env['odoo.report.service']
            result = report_svc.get_report(report_type, is_admin=is_admin)
            return result
        except Exception as e:
            _logger.error('Quick report error: %s', e)
            return {'found': False, 'error': str(e)}
