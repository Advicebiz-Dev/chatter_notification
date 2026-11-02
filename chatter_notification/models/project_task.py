from odoo import models


class ProjectTask(models.Model):
    _inherit = "project.task"


    def _get_notification_thread_name(self):
        """Build the label shown for task threads in Mail/Discuss.

        Format:
            Customer | Project | Task

        Missing elements are omitted.
        """
        self.ensure_one()

        partner = self.partner_id or self.project_id.partner_id

        parts = []
        if partner:
            parts.append(partner.display_name)
        if self.project_id:
            parts.append(self.project_id.display_name)
        if self.name:
            parts.append(self.name)

        return " | ".join(filter(None, parts)) or self.display_name

    def _thread_to_store(self, store, fields, *, request_list=None):
        """Use a contextual display name for task threads in Mail/Discuss.

        Important: do NOT call ``store.add(..., as_thread=True)`` from here,
        because that would invoke this method again and create infinite
        recursion.

        ``add_model_values`` updates the already-serialized JS ``mail.thread``
        record directly and therefore safely overrides only its display name.
        """
        super()._thread_to_store(
            store,
            fields,
            request_list=request_list,
        )

        for task in self:
            store.add_model_values(
                "mail.thread",
                {
                    "id": task.id,
                    "model": task._name,
                    "display_name": task._get_notification_thread_name(),
                },
            )

    def message_post(self, *, partner_ids=None, **kwargs):
        """Notify every internal follower of a manually posted task message."""
        self.ensure_one()

        if self._is_manual_chatter_message(kwargs):
            author_partner = self.env.user.partner_id
            follower_partners = self.message_follower_ids.partner_id.filtered(
                lambda partner: any(
                    user.active and not user.share for user in partner.user_ids
                )
            ) - author_partner

            partner_ids = list(set(partner_ids or []) | set(follower_partners.ids))

        return super().message_post(partner_ids=partner_ids, **kwargs)

    def _notify_get_recipients(self, message, msg_vals=False, **kwargs):
        """Force internal task followers to receive an Odoo Inbox notification.

        Adding followers as direct recipients is not enough when their personal
        notification preference is set to email. For manual chatter messages,
        internal followers are explicitly routed to the Odoo inbox.
        """
        recipients_data = super()._notify_get_recipients(
            message, msg_vals=msg_vals, **kwargs
        )

        self.ensure_one()
        values = msg_vals or {}
        if not self._is_manual_chatter_message(values, message=message):
            return recipients_data

        author_id = values.get("author_id") or message.author_id.id
        internal_follower_partner_ids = set(
            self.message_follower_ids.partner_id.filtered(
                lambda partner: partner.id != author_id
                and any(user.active and not user.share for user in partner.user_ids)
            ).ids
        )

        for recipient in recipients_data:
            if (
                recipient.get("id") in internal_follower_partner_ids
                and recipient.get("uid")
            ):
                recipient["notif"] = "inbox"

        return recipients_data

    def _is_manual_chatter_message(self, values, message=None):
        """Return whether the content is a manual chatter message or note."""
        message_type = values.get("message_type")
        if message_type is None and message:
            message_type = message.message_type
        if message_type is None:
            message_type = "notification"

        if message_type != "comment":
            return False

        subtype_xmlid = values.get("subtype_xmlid")
        subtype_id = values.get("subtype_id")
        if subtype_id is None and message:
            subtype_id = message.subtype_id.id

        allowed_subtypes = {
            self.env.ref("mail.mt_comment", raise_if_not_found=False),
            self.env.ref("mail.mt_note", raise_if_not_found=False),
        }
        allowed_subtype_ids = {
            subtype.id for subtype in allowed_subtypes if subtype
        }

        if subtype_xmlid:
            return subtype_xmlid in {"mail.mt_comment", "mail.mt_note"}
        if subtype_id:
            return subtype_id in allowed_subtype_ids
        return True
