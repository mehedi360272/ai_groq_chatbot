import json
import logging

from odoo import models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'


class GroqService(models.AbstractModel):
    _name = 'groq.service'
    _description = 'Groq API Service'

    def _get_config(self):
        ICP = self.env['ir.config_parameter'].sudo()
        return {
            'api_key': ICP.get_param('ai_groq_chatbot.groq_api_key', ''),
            'model': ICP.get_param('ai_groq_chatbot.groq_model', 'llama-3.3-70b-versatile'),
            'system_prompt': ICP.get_param(
                'ai_groq_chatbot.groq_system_prompt',
                'You are a helpful Odoo ERP assistant.'
            ),
            'max_tokens': int(ICP.get_param('ai_groq_chatbot.groq_max_tokens', 1024)),
            'enabled': ICP.get_param('ai_groq_chatbot.chatbot_enabled', 'True') == 'True',
        }

    def call_groq(self, messages, session_id=None):
        config = self._get_config()

        if not config['enabled']:
            raise UserError('AI Chatbot is currently inactive.')
        if not config['api_key']:
            raise UserError(
                'Groq API Key is not set.'
                'Settings > General Settings > Go to AI Chatbot'
            )

        full_messages = [{'role': 'system', 'content': config['system_prompt']}] + messages

        payload = {
            'model': config['model'],
            'messages': full_messages,
            'max_tokens': config['max_tokens'],
            'temperature': 0.7,
        }

        headers = {
            'Authorization': f"Bearer {config['api_key']}",
            'Content-Type': 'application/json',
        }

        # Try requests library first, fallback to urllib
        try:
            import requests as req_lib
            response = req_lib.post(
                GROQ_API_URL,
                json=payload,
                headers=headers,
                timeout=30,
                verify=True,
            )
            if response.status_code == 200:
                data = response.json()
                reply = data['choices'][0]['message']['content']
                tokens = data.get('usage', {}).get('total_tokens', 0)
                if session_id:
                    self._save_messages(session_id, messages, reply, tokens)
                return {'reply': reply, 'tokens': tokens, 'success': True}
            else:
                # Try without SSL verification
                response = req_lib.post(
                    GROQ_API_URL,
                    json=payload,
                    headers=headers,
                    timeout=30,
                    verify=False,
                )
                if response.status_code == 200:
                    data = response.json()
                    reply = data['choices'][0]['message']['content']
                    tokens = data.get('usage', {}).get('total_tokens', 0)
                    if session_id:
                        self._save_messages(session_id, messages, reply, tokens)
                    return {'reply': reply, 'tokens': tokens, 'success': True}
                else:
                    body = response.text
                    _logger.error('Groq API %s: %s', response.status_code, body)
                    try:
                        msg = response.json().get('error', {}).get('message', body)
                    except Exception:
                        msg = body
                    raise UserError(f'Groq API Error [{response.status_code}]: {msg}')

        except ImportError:
            # fallback to urllib
            _logger.warning('requests library not found, using urllib')
            self._call_groq_urllib(payload, headers, messages, session_id)

        except UserError:
            raise

        except Exception as e:
            _logger.error('Groq requests error: %s', e)
            raise UserError(f'Groq API connection issue: {str(e)}')

    def _call_groq_urllib(self, payload, headers, messages, session_id):
        import urllib.request
        import urllib.error
        import ssl

        data = json.dumps(payload).encode('utf-8')

        # Try with SSL verification disabled
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(
            GROQ_API_URL,
            data=data,
            method='POST',
            headers=headers,
        )

        try:
            with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                reply = result['choices'][0]['message']['content']
                tokens = result.get('usage', {}).get('total_tokens', 0)
                if session_id:
                    self._save_messages(session_id, messages, reply, tokens)
                return {'reply': reply, 'tokens': tokens, 'success': True}

        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8')
            _logger.error('Groq urllib HTTP %s: %s', e.code, body)
            try:
                msg = json.loads(body).get('error', {}).get('message', str(e))
            except Exception:
                msg = body
            raise UserError(f'Groq API Error [{e.code}]: {msg}')

        except urllib.error.URLError as e:
            _logger.error('Groq urllib URL error: %s', e)
            raise UserError(f'Groq API connection issue: {str(e)}')

    def _save_messages(self, session_id, messages, reply, tokens):
        try:
            History = self.env['ai.chat.history'].sudo()
            history = History.search([
                ('session_id', '=', session_id),
                ('user_id', '=', self.env.user.id),
            ], limit=1)
            if not history:
                history = History.create({
                    'session_id': session_id,
                    'user_id': self.env.user.id,
                })
            Msg = self.env['ai.chat.message'].sudo()
            if messages and messages[-1].get('role') == 'user':
                Msg.create({
                    'history_id': history.id,
                    'role': 'user',
                    'content': messages[-1]['content'],
                })
            Msg.create({
                'history_id': history.id,
                'role': 'assistant',
                'content': reply,
                'tokens_used': tokens,
            })
        except Exception as e:
            _logger.warning('Chat history save error: %s', e)
