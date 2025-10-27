"""Telegram bot for human approval workflow."""

import asyncio

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from src.core.config import get_settings
from src.core.logging import get_logger
from src.infra.logging import audit_log
from src.runner.sandbox import exec_in_sandbox
from src.security.policy import ApprovalGate

logger = get_logger(__name__)
settings = get_settings()


class TelegramApprovalBot:
    """
    Telegram bot for approving/denying proposed actions.

    Features:
    - Shows proposed code, rationale, and risk level
    - Approve button → executes in sandbox
    - Deny button → closes proposal
    - Logs all approval decisions
    """

    def __init__(
        self,
        token: str | None = None,
        admin_chat_id: str | None = None,
    ):
        self.token = token or settings.telegram_bot_token
        self.admin_chat_id = admin_chat_id or settings.telegram_admin_chat_id
        self.approval_gate = ApprovalGate()
        self.app: Application | None = None

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        await update.message.reply_text(
            "🤖 Otis Cybersecurity Agent - Approval Bot\n\n"
            "I will send you approval requests for high-risk actions.\n\n"
            "Commands:\n"
            "/start - Show this message\n"
            "/pending - List pending approvals\n"
            "/status - Bot status"
        )

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command."""
        pending = self.approval_gate.list_pending()
        await update.message.reply_text(
            f"✅ Bot is running\n" f"📋 Pending approvals: {len(pending)}"
        )

    async def pending_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /pending command."""
        pending = self.approval_gate.list_pending()

        if not pending:
            await update.message.reply_text("No pending approvals.")
            return

        message = "📋 Pending Approvals:\n\n"
        for approval in pending:
            action_id = approval["action_id"]
            action_type = approval["action_type"]
            risk_level = approval["risk_level"]
            message += f"• {action_id}: {action_type} (Risk: {risk_level})\n"

        await update.message.reply_text(message)

    async def send_approval_request(
        self,
        action_id: str,
        action_type: str,
        description: str,
        code: str | None,
        rationale: str,
        risk_level: str,
    ) -> bool:
        """
        Send an approval request to the admin.

        Args:
            action_id: Unique action identifier
            action_type: Type of action
            description: Action description
            code: Code to execute
            rationale: Justification
            risk_level: Risk level

        Returns:
            True if sent successfully
        """
        if not self.app or not self.admin_chat_id:
            logger.warning("Telegram bot not configured, approval request not sent")
            return False

        try:
            # Register the approval request
            self.approval_gate.request_approval(
                action_id=action_id,
                action_type=action_type,
                risk_level=risk_level,
                code=code,
                rationale=rationale,
            )

            # Format the message
            message = (
                f"🔔 <b>Approval Request</b>\n\n"
                f"<b>Action ID:</b> <code>{action_id}</code>\n"
                f"<b>Type:</b> {action_type}\n"
                f"<b>Risk Level:</b> {risk_level.upper()}\n\n"
                f"<b>Description:</b>\n{description}\n\n"
                f"<b>Rationale:</b>\n{rationale}\n"
            )

            if code:
                message += f"\n<b>Proposed Code:</b>\n<pre>{code[:500]}</pre>"
                if len(code) > 500:
                    message += "\n<i>(code truncated)</i>"

            # Create inline keyboard with Approve/Deny buttons
            keyboard = [
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"approve_{action_id}"),
                    InlineKeyboardButton("❌ Deny", callback_data=f"deny_{action_id}"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Send message
            await self.app.bot.send_message(
                chat_id=self.admin_chat_id,
                text=message,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )

            logger.info("Approval request sent", action_id=action_id)
            return True

        except Exception as e:
            logger.error("Failed to send approval request", error=str(e))
            return False

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button callbacks (Approve/Deny)."""
        query = update.callback_query
        await query.answer()

        callback_data = query.data
        action = callback_data.split("_")[0]  # approve or deny
        action_id = "_".join(callback_data.split("_")[1:])

        approval = self.approval_gate.pending_approvals.get(action_id)
        if not approval:
            await query.edit_message_text("❌ Approval request not found or already processed.")
            return

        if action == "approve":
            # Approve the action
            self.approval_gate.approve(action_id)

            # Execute code in sandbox if provided
            code = approval.get("code")
            execution_result = None

            if code:
                logger.info("Executing approved code in sandbox", action_id=action_id)
                execution_result = exec_in_sandbox(
                    code=code,
                    lang="python",
                    timeout=30,
                    net=True,  # Allow network after approval
                )

            # Update message
            result_text = ""
            if execution_result:
                if execution_result["success"]:
                    result_text = f"\n\n📊 <b>Execution Result:</b>\n<pre>{execution_result['output'][:200]}</pre>"
                else:
                    result_text = f"\n\n❌ <b>Execution Failed:</b>\n<pre>{execution_result['error'][:200]}</pre>"

            await query.edit_message_text(
                f"✅ <b>APPROVED</b>\n\n"
                f"Action ID: <code>{action_id}</code>\n"
                f"Status: Executed in sandbox"
                f"{result_text}",
                parse_mode="HTML",
            )

            # Audit log
            audit_log(
                action="approval_granted",
                action_id=action_id,
                user=query.from_user.username,
                risk_level=approval.get("risk_level"),
                status="approved",
                execution_success=execution_result.get("success") if execution_result else None,
            )

        elif action == "deny":
            # Deny the action
            self.approval_gate.deny(action_id, reason="Denied by admin")

            await query.edit_message_text(
                f"❌ <b>DENIED</b>\n\n"
                f"Action ID: <code>{action_id}</code>\n"
                f"Status: Rejected",
                parse_mode="HTML",
            )

            # Audit log
            audit_log(
                action="approval_denied",
                action_id=action_id,
                user=query.from_user.username,
                risk_level=approval.get("risk_level"),
                status="denied",
            )

        logger.info("Approval decision recorded", action_id=action_id, decision=action)

    async def setup(self) -> None:
        """Setup the bot application."""
        if not self.token:
            logger.warning("Telegram bot token not configured")
            return

        # Create application
        self.app = Application.builder().token(self.token).build()

        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CommandHandler("pending", self.pending_command))
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))

        logger.info("Telegram bot setup complete")

    async def start(self) -> None:
        """Start the bot."""
        if not self.app:
            await self.setup()

        if self.app:
            logger.info("Starting Telegram bot")
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling()

    async def stop(self) -> None:
        """Stop the bot."""
        if self.app:
            logger.info("Stopping Telegram bot")
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()


async def run_bot(token: str | None = None, admin_chat_id: str | None = None) -> None:
    """
    Run the Telegram approval bot.

    Args:
        token: Telegram bot token (reads from env if not provided)
        admin_chat_id: Admin chat ID (reads from env if not provided)
    """
    bot = TelegramApprovalBot(token=token, admin_chat_id=admin_chat_id)
    await bot.setup()
    await bot.start()

    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested")
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(run_bot())
