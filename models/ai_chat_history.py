from odoo import api, fields, models


class AiChatHistory(models.Model):
    _name = 'ai.chat.history'
    _description = 'AI Chat History'
    _order = 'create_date desc'

    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        readonly=True,
    )
    session_id = fields.Char(string='Session ID', required=True, index=True)
    message_ids = fields.One2many(
        'ai.chat.message',
        'history_id',
        string='Messages',
    )
    message_count = fields.Integer(
        string='Messages',
        compute='_compute_message_count',
    )
    active = fields.Boolean(default=True)

    @api.depends('message_ids')
    def _compute_message_count(self):
        for rec in self:
            rec.message_count = len(rec.message_ids)

    def action_view_messages(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Chat - {self.user_id.name}',
            'res_model': 'ai.chat.message',
            'view_mode': 'list,form',
            'domain': [('history_id', '=', self.id)],
        }


class AiChatMessage(models.Model):
    _name = 'ai.chat.message'
    _description = 'AI Chat Message'
    _order = 'create_date asc'

    history_id = fields.Many2one(
        'ai.chat.history',
        string='Session',
        required=True,
        ondelete='cascade',
    )
    role = fields.Selection(
        [('user', 'User'), ('assistant', 'Assistant')],
        required=True,
    )
    content = fields.Text(string='Message', required=True)
    tokens_used = fields.Integer(string='Tokens Used', default=0)
