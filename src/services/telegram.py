"""Telegram bot service for approval gates."""

from telegram import Bot
from telegram.error import TelegramError

from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class TelegramService:
    """Service for Telegram notifications and approvals."""

    def __init__(self):
        self.bot_token = settings.telegram_bot_token
        self.admin_chat_id = settings.telegram_admin_chat_id
        self.approval_timeout = settings.telegram_approval_timeout
        self._bot: Bot | None = None

    def get_bot(self) -> Bot | None:
        """Get or create bot instance."""
        if not self.bot_token:
            logger.warning("Telegram bot token not configured")
            return None

        if self._bot is None:
            self._bot = Bot(token=self.bot_token)
        return self._bot

    async def send_message(self, message: str, chat_id: str | None = None) -> bool:
        """Send a message to a chat."""
        bot = self.get_bot()
        if not bot:
            return False

        target_chat_id = chat_id or self.admin_chat_id
        if not target_chat_id:
            logger.warning("No chat ID configured")
            return False

        try:
            await bot.send_message(chat_id=target_chat_id, text=message, parse_mode="Markdown")
            logger.info("Message sent to Telegram", chat_id=target_chat_id)
            return True
        except TelegramError as e:
            logger.error("Failed to send Telegram message", error=str(e))
            return False

    async def request_approval(
        self, action_description: str, risk_level: str, action_id: int
    ) -> bool | None:
        """Request approval for an action via Telegram."""
        if not settings.enable_approval_gate:
            logger.info("Approval gate disabled, auto-approving")
            return True

        bot = self.get_bot()
        if not bot or not self.admin_chat_id:
            logger.warning("Telegram not configured, cannot request approval")
            return None

        message = f"""
🤖 **Action Approval Required**

**Action ID:** {action_id}
**Risk Level:** {risk_level.upper()}
**Description:**
{action_description}

Reply with:
- `/approve {action_id}` to approve
- `/reject {action_id}` to reject

_This request will timeout in {self.approval_timeout} seconds._
"""

        try:
            await bot.send_message(
                chat_id=self.admin_chat_id,
                text=message,
                parse_mode="Markdown",
            )
            logger.info("Approval requested via Telegram", action_id=action_id)

            # In a real implementation, you would set up webhook handlers
            # or polling to listen for the response. For now, we return None
            # to indicate the request was sent but approval is pending.
            return None

        except TelegramError as e:
            logger.error("Failed to request approval", error=str(e))
            return None

    async def notify_action_result(self, action_id: int, success: bool, result: str) -> None:
        """Notify about action execution result."""
        status_emoji = "✅" if success else "❌"
        message = f"""
{status_emoji} **Action Execution Result**

**Action ID:** {action_id}
**Status:** {"Success" if success else "Failed"}
**Result:**
```
{result[:1000]}  # Limit result length
```
"""
        await self.send_message(message)

    async def check_health(self) -> bool:
        """Check if Telegram service is available."""
        bot = self.get_bot()
        if not bot:
            return False

        try:
            me = await bot.get_me()
            logger.info("Telegram bot connected", bot_username=me.username)
            return True
        except TelegramError as e:
            logger.error("Telegram health check failed", error=str(e))
            return False
