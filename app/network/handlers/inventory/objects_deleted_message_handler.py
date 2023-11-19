import logging

from app.gui.signals import AppSignals
from app.types_.dofus.scripts.com.ankamagames.dofus.network.messages.game.inventory.items.ObjectsDeletedMessage import (
    ObjectsDeletedMessage,
)
from app.types_.models.common import BotInfo, ParsedMessageHandler

logger = logging.getLogger(__name__)


class ObjectsDeletedMessageHandler(ParsedMessageHandler, ObjectsDeletedMessage):
    def handle(self, bot_info: BotInfo, app_signals: AppSignals) -> None:
        if (character := bot_info.common_info.character) is not None:
            for _object in self.objectUID:
                logger.info(f"remove object {self.objectUID} to character")
                character.on_object_deleted_msg(_object)
