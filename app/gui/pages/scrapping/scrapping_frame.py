from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QFrame, QStackedWidget
from qfluentwidgets import TabBar, TabCloseButtonDisplayMode, VBoxLayout

from app.database.models import get_engine
from app.gui.components.common import TopPage
from app.gui.pages.scrapping.scrapping_craft_tab.scrapping_craft import ScrappingCraft
from app.gui.pages.scrapping.scrapping_presentation_tab.scrapping_presentation import (
    ScrappingPresentation,
)
from app.gui.pages.scrapping.scrapping_progression import ScrappingProgression
from app.gui.signals import AppSignals
from app.types_.models.common import BotInfo


class ScrappingFrame(QFrame):
    def __init__(self, bot_info: BotInfo, app_signals: AppSignals, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = get_engine()
        self.bot_info = bot_info
        self.app_signals = app_signals

        self.setLayout(VBoxLayout(self))
        self.layout().setAlignment(Qt.AlignTop)

        self.init_header()

        self.init_tabs()

        self.app_signals.on_new_buying_hdv_playing_value.connect(
            lambda: self.on_update_do_play_scrapping(
                self.bot_info.scraping_info.is_playing_event.is_set()
            )
        )

    def init_tabs(self):
        self.tabs_stacked = QStackedWidget(self)

        self.tabs = TabBar(self)
        self.tabs.setCloseButtonDisplayMode(TabCloseButtonDisplayMode.NEVER)
        self.tabs.setAddButtonVisible(False)

        self.scapping_pres = ScrappingPresentation(
            self.bot_info, self.app_signals, self.engine
        )
        self.tabs_stacked.addWidget(self.scapping_pres)
        self.tabs.addTab("scraping.presentation", "Présentation")

        self.scrapping_craft = ScrappingCraft(
            self.bot_info, self.app_signals, self.engine
        )
        self.tabs_stacked.addWidget(self.scrapping_craft)
        self.tabs.addTab("scraping.craft", "Craft")

        self.tabs.currentChanged.connect(self.on_tab_changed)

        self.layout().addWidget(self.tabs)
        self.layout().addWidget(self.tabs_stacked)

    @pyqtSlot(int)
    def on_tab_changed(self, index: int):
        self.tabs_stacked.setCurrentIndex(index)

    def init_header(self):
        self.progress_widget = ScrappingProgression(bot_info=self.bot_info)
        self.progress_widget.hide()
        self.app_signals.on_leaving_hdv.connect(self.progress_widget.hide)
        self.app_signals.on_new_scraping_current_state.connect(
            self.progress_widget.update_content
        )
        self.layout().addWidget(self.progress_widget)

        self.header = TopPage()
        self.header.do_play(self.bot_info.scraping_info.is_playing_event.is_set())
        self.header.button_play.clicked.connect(
            lambda: self.on_update_do_play_scrapping(True)
        )
        self.header.button_stop.clicked.connect(
            lambda: self.on_update_do_play_scrapping(False)
        )

        self.layout().addWidget(self.header)

    @pyqtSlot(bool)
    def on_update_do_play_scrapping(self, do_play: bool):
        if do_play:
            self.bot_info.scraping_info.is_playing_event.set()
        else:
            self.bot_info.scraping_info.is_playing_event.clear()
        self.header.do_play(do_play)
