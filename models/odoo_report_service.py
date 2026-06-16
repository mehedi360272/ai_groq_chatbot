import logging
from datetime import datetime, timedelta
from odoo import models, api

_logger = logging.getLogger(__name__)


class OdooReportService(models.AbstractModel):
    _name = 'odoo.report.service'
    _description = 'Odoo Data Report Service for AI Chatbot'

    # ─────────────────────────────────────────────
    # Public entry point
    # ─────────────────────────────────────────────

    def get_report(self, keyword, is_admin=False):
        """
        keyword থেকে report type detect করে data return করে।
        Returns: dict { 'found': bool, 'text': str }
        """
        kw = keyword.lower()

        # Sales / Invoice
        if any(w in kw for w in ['sale', 'sales', 'invoice', 'বিক্রয়', 'ইনভয়েস']):
            return self._sales_report(is_admin)

        # Purchase / Vendor Bills
        if any(w in kw for w in ['purchase', 'vendor', 'bill', 'ক্রয়', 'বিল', 'সাপ্লায়ার']):
            return self._purchase_report(is_admin)

        # Inventory / Stock
        if any(w in kw for w in ['stock', 'inventory', 'product', 'স্টক', 'পণ্য', 'ইনভেন্টরি']):
            return self._stock_report(is_admin)

        # Manufacturing
        if any(w in kw for w in ['manufacturing', 'production', 'mrp', 'ম্যানুফ্যাকচারিং', 'উৎপাদন']):
            return self._manufacturing_report(is_admin)

        # Top customers
        if any(w in kw for w in ['customer', 'client', 'কাস্টমার', 'গ্রাহক']):
            return self._top_customers_report(is_admin)

        # Overdue / unpaid
        if any(w in kw for w in ['overdue', 'unpaid', 'due', 'বকেয়া', 'অপরিশোধিত']):
            return self._overdue_report(is_admin)

        return {'found': False, 'text': ''}

    # ─────────────────────────────────────────────
    # Sales Report
    # ─────────────────────────────────────────────

    def _sales_report(self, is_admin):
        try:
            env = self.env
            today = datetime.now()
            month_start = today.replace(day=1, hour=0, minute=0, second=0)

            domain = [
                ('state', 'in', ['sale', 'done']),
                ('date_order', '>=', month_start.strftime('%Y-%m-%d %H:%M:%S')),
            ]
            if not is_admin:
                domain.append(('user_id', '=', env.user.id))

            orders = env['sale.order'].sudo().search_read(
                domain,
                ['name', 'partner_id', 'amount_total', 'date_order', 'state'],
                limit=10,
                order='amount_total desc',
            )

            total = sum(o['amount_total'] for o in orders)
            count = env['sale.order'].sudo().search_count(domain)

            lines = [f"📊 **Sales Report** — {today.strftime('%B %Y')}",
                     f"মোট Orders: {count} | মোট পরিমাণ: {total:,.2f}",
                     ""]

            if orders:
                lines.append("🔝 Top Sales Orders:")
                for o in orders[:8]:
                    partner = o['partner_id'][1] if o['partner_id'] else 'N/A'
                    lines.append(f"• {o['name']} | {partner} | {o['amount_total']:,.2f}")
            else:
                lines.append("এই মাসে কোনো confirmed sale order নেই।")

            return {'found': True, 'text': '\n'.join(lines)}

        except Exception as e:
            _logger.error('Sales report error: %s', e)
            return {'found': True, 'text': f'Sales report আনতে সমস্যা হয়েছে: {str(e)}'}

    # ─────────────────────────────────────────────
    # Purchase Report
    # ─────────────────────────────────────────────

    def _purchase_report(self, is_admin):
        try:
            env = self.env
            today = datetime.now()
            month_start = today.replace(day=1, hour=0, minute=0, second=0)

            domain = [
                ('state', 'in', ['purchase', 'done']),
                ('date_order', '>=', month_start.strftime('%Y-%m-%d %H:%M:%S')),
            ]

            orders = env['purchase.order'].sudo().search_read(
                domain,
                ['name', 'partner_id', 'amount_total', 'date_order'],
                limit=10,
                order='amount_total desc',
            )

            total = sum(o['amount_total'] for o in orders)
            count = env['purchase.order'].sudo().search_count(domain)

            lines = [f"🛒 **Purchase Report** — {today.strftime('%B %Y')}",
                     f"মোট Orders: {count} | মোট পরিমাণ: {total:,.2f}",
                     ""]

            if orders:
                lines.append("🔝 Top Purchase Orders:")
                for o in orders[:8]:
                    partner = o['partner_id'][1] if o['partner_id'] else 'N/A'
                    lines.append(f"• {o['name']} | {partner} | {o['amount_total']:,.2f}")
            else:
                lines.append("এই মাসে কোনো confirmed purchase order নেই।")

            return {'found': True, 'text': '\n'.join(lines)}

        except Exception as e:
            _logger.error('Purchase report error: %s', e)
            return {'found': True, 'text': f'Purchase report আনতে সমস্যা হয়েছে: {str(e)}'}

    # ─────────────────────────────────────────────
    # Stock / Inventory Report
    # ─────────────────────────────────────────────

    def _stock_report(self, is_admin):
        try:
            env = self.env

            # Low stock products (qty_available <= reordering point)
            quants = env['stock.quant'].sudo().search_read(
                [('location_id.usage', '=', 'internal')],
                ['product_id', 'quantity', 'reserved_quantity', 'location_id'],
                limit=15,
                order='quantity asc',
            )

            # Aggregate by product
            product_qty = {}
            for q in quants:
                pid = q['product_id'][0]
                pname = q['product_id'][1]
                product_qty[pid] = {
                    'name': pname,
                    'qty': product_qty.get(pid, {}).get('qty', 0) + q['quantity'],
                    'reserved': product_qty.get(pid, {}).get('reserved', 0) + q['reserved_quantity'],
                }

            lines = ["📦 **Stock / Inventory Report**", ""]

            low_stock = [(pid, d) for pid, d in product_qty.items() if d['qty'] <= 10]
            normal = [(pid, d) for pid, d in product_qty.items() if d['qty'] > 10]

            if low_stock:
                lines.append("⚠️ কম স্টক (≤10 unit):")
                for pid, d in sorted(low_stock, key=lambda x: x[1]['qty'])[:8]:
                    available = d['qty'] - d['reserved']
                    lines.append(f"• {d['name']} | হাতে: {d['qty']:.1f} | available: {available:.1f}")
                lines.append("")

            if normal:
                lines.append("✅ পর্যাপ্ত স্টক:")
                for pid, d in sorted(normal, key=lambda x: -x[1]['qty'])[:6]:
                    lines.append(f"• {d['name']} | হাতে: {d['qty']:.1f}")

            if not quants:
                lines.append("কোনো internal stock location-এ পণ্য পাওয়া যায়নি।")

            return {'found': True, 'text': '\n'.join(lines)}

        except Exception as e:
            _logger.error('Stock report error: %s', e)
            return {'found': True, 'text': f'Stock report আনতে সমস্যা হয়েছে: {str(e)}'}

    # ─────────────────────────────────────────────
    # Manufacturing Report
    # ─────────────────────────────────────────────

    def _manufacturing_report(self, is_admin):
        try:
            env = self.env

            # Count by state
            states = ['draft', 'confirmed', 'progress', 'to_close', 'done', 'cancel']
            state_labels = {
                'draft': 'Draft',
                'confirmed': 'Confirmed',
                'progress': '🔧 In Progress',
                'to_close': 'To Close',
                'done': '✅ Done',
                'cancel': 'Cancelled',
            }

            today = datetime.now()
            month_start = today.replace(day=1, hour=0, minute=0, second=0)

            lines = [f"🏭 **Manufacturing Report** — {today.strftime('%B %Y')}", ""]

            for state in states:
                count = env['mrp.production'].sudo().search_count([
                    ('state', '=', state),
                    ('create_date', '>=', month_start.strftime('%Y-%m-%d %H:%M:%S')),
                ])
                if count:
                    lines.append(f"{state_labels[state]}: {count} টি")

            lines.append("")

            # Recent in-progress
            in_progress = env['mrp.production'].sudo().search_read(
                [('state', 'in', ['confirmed', 'progress'])],
                ['name', 'product_id', 'product_qty', 'date_start'],
                limit=8,
                order='date_start asc',
            )

            if in_progress:
                lines.append("🔄 চলমান Production Orders:")
                for mo in in_progress:
                    product = mo['product_id'][1] if mo['product_id'] else 'N/A'
                    lines.append(f"• {mo['name']} | {product} | qty: {mo['product_qty']:.1f}")

            return {'found': True, 'text': '\n'.join(lines)}

        except Exception as e:
            _logger.error('Manufacturing report error: %s', e)
            return {'found': True, 'text': f'Manufacturing report আনতে সমস্যা হয়েছে: {str(e)}'}

    # ─────────────────────────────────────────────
    # Top Customers
    # ─────────────────────────────────────────────

    def _top_customers_report(self, is_admin):
        try:
            env = self.env
            today = datetime.now()
            year_start = today.replace(month=1, day=1, hour=0, minute=0, second=0)

            domain = [
                ('state', 'in', ['sale', 'done']),
                ('date_order', '>=', year_start.strftime('%Y-%m-%d %H:%M:%S')),
            ]
            if not is_admin:
                domain.append(('user_id', '=', env.user.id))

            orders = env['sale.order'].sudo().search_read(
                domain, ['partner_id', 'amount_total']
            )

            customer_totals = {}
            for o in orders:
                if o['partner_id']:
                    pid, pname = o['partner_id']
                    customer_totals[pid] = {
                        'name': pname,
                        'total': customer_totals.get(pid, {}).get('total', 0) + o['amount_total'],
                        'count': customer_totals.get(pid, {}).get('count', 0) + 1,
                    }

            sorted_customers = sorted(customer_totals.values(), key=lambda x: -x['total'])[:10]

            lines = [f"👥 **Top Customers** — {today.year}", ""]
            for i, c in enumerate(sorted_customers, 1):
                lines.append(f"{i}. {c['name']} | {c['total']:,.2f} ({c['count']} orders)")

            if not sorted_customers:
                lines.append("এই বছর কোনো sale data পাওয়া যায়নি।")

            return {'found': True, 'text': '\n'.join(lines)}

        except Exception as e:
            _logger.error('Customer report error: %s', e)
            return {'found': True, 'text': f'Customer report আনতে সমস্যা হয়েছে: {str(e)}'}

    # ─────────────────────────────────────────────
    # Overdue Invoices
    # ─────────────────────────────────────────────

    def _overdue_report(self, is_admin):
        try:
            env = self.env
            today = datetime.now().date()

            domain = [
                ('move_type', 'in', ['out_invoice', 'in_invoice']),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'partial']),
                ('invoice_date_due', '<', str(today)),
            ]

            invoices = env['account.move'].sudo().search_read(
                domain,
                ['name', 'partner_id', 'move_type', 'amount_residual', 'invoice_date_due'],
                limit=15,
                order='invoice_date_due asc',
            )

            out_invoices = [i for i in invoices if i['move_type'] == 'out_invoice']
            in_invoices = [i for i in invoices if i['move_type'] == 'in_invoice']

            lines = [f"⚠️ **Overdue Report** — আজ {today}", ""]

            if out_invoices:
                total = sum(i['amount_residual'] for i in out_invoices)
                lines.append(f"📤 Customer Invoices বকেয়া: {len(out_invoices)} টি | মোট: {total:,.2f}")
                for inv in out_invoices[:6]:
                    partner = inv['partner_id'][1] if inv['partner_id'] else 'N/A'
                    due = inv['invoice_date_due'] or 'N/A'
                    lines.append(f"  • {inv['name']} | {partner} | {inv['amount_residual']:,.2f} | due: {due}")
                lines.append("")

            if in_invoices:
                total = sum(i['amount_residual'] for i in in_invoices)
                lines.append(f"📥 Vendor Bills বকেয়া: {len(in_invoices)} টি | মোট: {total:,.2f}")
                for inv in in_invoices[:6]:
                    partner = inv['partner_id'][1] if inv['partner_id'] else 'N/A'
                    due = inv['invoice_date_due'] or 'N/A'
                    lines.append(f"  • {inv['name']} | {partner} | {inv['amount_residual']:,.2f} | due: {due}")

            if not invoices:
                lines.append("✅ কোনো overdue invoice নেই!")

            return {'found': True, 'text': '\n'.join(lines)}

        except Exception as e:
            _logger.error('Overdue report error: %s', e)
            return {'found': True, 'text': f'Overdue report আনতে সমস্যা হয়েছে: {str(e)}'}
