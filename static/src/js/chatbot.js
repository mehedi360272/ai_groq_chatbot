/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { Component, useState, useRef, onMounted, markup } from "@odoo/owl";

function generateSessionId() {
    return "sess_" + Date.now() + "_" + Math.random().toString(36).slice(2, 8);
}

// Simple markdown → HTML (bold, inline code, newline)
function simpleMarkdown(text) {
    let html = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/`([^`]+)`/g, "<code>$1</code>")
        .replace(/\n/g, "<br/>");
    return markup(html);
}

// Quick report buttons config
const QUICK_REPORTS = [
    { label: "📊 Sales",         keyword: "sales report"         },
    { label: "🛒 Purchase",      keyword: "purchase report"       },
    { label: "📦 Stock",         keyword: "stock report"          },
    { label: "🏭 Manufacturing", keyword: "manufacturing report"  },
    { label: "👥 Customers",     keyword: "customer report"       },
    { label: "⚠️ Overdue",       keyword: "overdue report"        },
];

class AiChatbotWidget extends Component {
    static template = "ai_groq_chatbot.ChatbotWidget";
    static props = {};

    setup() {
        this.messagesRef = useRef("messages");

        this.state = useState({
            isOpen: false,
            isLoading: false,
            inputText: "",
            messages: [],
            sessionId: generateSessionId(),
            error: null,
            showQuickReports: true,
        });

        onMounted(() => {
            this.state.messages.push({
                role: "assistant",
                content: "Assalamu Alaikum! I am your AI assistant. View a quick report or ask any question using the button below.",
                html: simpleMarkdown("Assalamu Alaikum! I am your AI assistant. View a quick report or ask any question using the button below."),
                time: new Date().toLocaleTimeString("bn-BD", { hour: "2-digit", minute: "2-digit" }),
            });
        });
    }

    get quickReports() {
        return QUICK_REPORTS;
    }

    toggleChat() {
        this.state.isOpen = !this.state.isOpen;
        if (this.state.isOpen) this._scrollToBottom();
    }

    onKeyDown(ev) {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            this.sendMessage();
        }
    }

    // Quick report button click
    async onQuickReport(keyword) {
        this.state.showQuickReports = false;
        // User message হিসেবে show করো
        this.state.messages.push({
            role: "user",
            content: keyword,
            html: simpleMarkdown(keyword),
            time: new Date().toLocaleTimeString("bn-BD", { hour: "2-digit", minute: "2-digit" }),
        });
        await this._doSend([{ role: "user", content: keyword }]);
    }

    async sendMessage() {
        const text = this.state.inputText.trim();
        if (!text || this.state.isLoading) return;

        this.state.messages.push({
            role: "user",
            content: text,
            html: simpleMarkdown(text),
            time: new Date().toLocaleTimeString("bn-BD", { hour: "2-digit", minute: "2-digit" }),
        });
        this.state.inputText = "";
        this.state.showQuickReports = false;

        // Last 12 messages slice করে পাঠাও
        const apiMessages = this.state.messages
            .slice(-12)
            .map((m) => ({ role: m.role, content: m.content }));

        await this._doSend(apiMessages);
    }

    async _doSend(apiMessages) {
        this.state.isLoading = true;
        this.state.error = null;
        this._scrollToBottom();

        try {
            const result = await rpc("/ai_chat/send", {
                messages: apiMessages,
                session_id: this.state.sessionId,
            });

            if (result.error) {
                this.state.error = result.error;
            } else {
                const replyText = result.reply || "";
                this.state.messages.push({
                    role: "assistant",
                    content: replyText,
                    html: simpleMarkdown(replyText),
                    time: new Date().toLocaleTimeString("bn-BD", { hour: "2-digit", minute: "2-digit" }),
                    // raw report data (optional, for debugging)
                    reportData: result.report_data || null,
                });
            }
        } catch (e) {
            this.state.error = "There was a problem connecting. Please try again.";
        } finally {
            this.state.isLoading = false;
            this._scrollToBottom();
        }
    }

    async clearChat() {
        try {
            await rpc("/ai_chat/clear", { session_id: this.state.sessionId });
        } catch (_) {}
        this.state.sessionId = generateSessionId();
        this.state.showQuickReports = true;
        this.state.messages = [
            {
                role: "assistant",
                content: "Chat cleared. Start a new conversation.",
                html: simpleMarkdown("Chat cleared. Start a new conversation."),
                time: new Date().toLocaleTimeString("bn-BD", { hour: "2-digit", minute: "2-digit" }),
            },
        ];
    }

    _scrollToBottom() {
        setTimeout(() => {
            const el = this.messagesRef.el;
            if (el) el.scrollTop = el.scrollHeight;
        }, 60);
    }
}

registry.category("systray").add("ai_groq_chatbot", {
    Component: AiChatbotWidget,
    sequence: 5,
});
