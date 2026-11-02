from odoo import models


class MailMessage(models.Model):
    _inherit = "mail.message"

    def write(self, vals):
        """Re-notify internal task followers when a manual chatter message is edited.

        In Odoo 19, editing a chatter message updates ``mail.message`` directly,
        so ``project.task.message_post()`` is not called again.  We therefore
        detect a real body change here and re-create Inbox notifications for the
        internal followers of the related task.
        """
        messages_to_renotify = self.env["mail.message"]

        if "body" in vals and not self.env.context.get(
            "chatter_follower_skip_edit_notification"
        ):
            new_body = vals.get("body") or ""
            for message in self:
                if (
                    message.model == "project.task"
                    and message.res_id
                    and message.body != new_body
                    and self._is_manual_task_message(message)
                ):
                    messages_to_renotify |= message

        result = super().write(vals)

        for message in messages_to_renotify:
            task = self.env["project.task"].browse(message.res_id).exists()
            if not task:
                continue

            editor_partner = self.env.user.partner_id
            follower_users = task.message_follower_ids.partner_id.mapped("user_ids").filtered(
                lambda user: user.active and not user.share and user.partner_id != editor_partner
            )
            if not follower_users:
                continue

            follower_partner_ids = follower_users.partner_id.ids

            # A mail.notification is unique per (message, partner).  Remove the
            # previous notification for these followers before creating a fresh
            # unread Inbox notification for the edited message.
            old_notifications = self.env["mail.notification"].sudo().search([
                ("mail_message_id", "=", message.id),
                ("res_partner_id", "in", follower_partner_ids),
            ])
            old_notifications.unlink()

            recipients_data = [
                {
                    "id": user.partner_id.id,
                    "uid": user.id,
                    "notif": "inbox",
                }
                for user in follower_users
            ]

            # Reuse Odoo's native Inbox notification path.  It creates the
            # unread mail.notification record and pushes the update through the
            # bus so open browsers receive it immediately.
            task._notify_thread_by_inbox(
                message,
                recipients_data,
                msg_vals={"body": message.body},
            )

        return result

    def _is_manual_task_message(self, message):
        """Return True for user-authored comments/internal notes only."""
        if message.message_type != "comment":
            return False

        allowed_subtypes = {
            self.env.ref("mail.mt_comment", raise_if_not_found=False),
            self.env.ref("mail.mt_note", raise_if_not_found=False),
        }
        allowed_subtype_ids = {
            subtype.id for subtype in allowed_subtypes if subtype
        }

        return not message.subtype_id or message.subtype_id.id in allowed_subtype_ids
