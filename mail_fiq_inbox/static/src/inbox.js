/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class MailFiqInbox extends Component {
    static template = "mail_fiq_inbox.Inbox";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.state = useState({
            messages: [],
            selected: null,
            loading: true,
        });
        onWillStart(async () => {
            this.state.messages = await this.orm.call(
                "mail.fiq.inbox", "get_messages", [40]);
            this.state.loading = false;
        });
    }

    async open(msg) {
        this.state.selected = await this.orm.call(
            "mail.fiq.inbox", "get_message", [msg.id]);
    }

    openRecord(cand) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: cand.model,
            res_id: cand.res_id,
            views: [[false, "form"]],
        });
    }

    async archive(cand) {
        const sel = this.state.selected;
        if (!sel) {
            return;
        }
        const res = await this.orm.call(
            "mail.fiq.inbox", "archive_to", [sel.id, cand.model, cand.res_id]);
        if (res) {
            this.notification.add(
                _t("Filed as PDF on %s", cand.name), { type: "success" });
        }
    }
}

registry.category("actions").add("mail_fiq_inbox.inbox", MailFiqInbox);
