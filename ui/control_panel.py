from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QSlider, QSpinBox, QGroupBox, QDoubleSpinBox, QCheckBox, 
                             QLineEdit, QFormLayout, QComboBox, QWidget, QScrollArea)
from PyQt5.QtCore import Qt
from core.characters import get_character_config, CHARACTER_PROFILES

class ControlPanel(QDialog):
    def __init__(self, pet_window):
        super().__init__()
        self.pet = pet_window
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Companion Control Center")
        self.resize(400, 700)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        
        # Modern Dark Theme
        self.setStyleSheet("""
    QDialog {
        background: #101217;
        color: #F4F5F7;
        font-family: "Segoe UI", "Inter", sans-serif;
    }

    QWidget {
        color: #F4F5F7;
    }

    QGroupBox {
        border: 1px solid #242833;
        border-radius: 16px;
        margin-top: 12px;
        padding: 18px;
        padding-top: 20px;
        background: #171A21;
        font-size: 12px;
        font-weight: 700;
        color: #AEB5C2;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        left: 16px;
        padding: 0 7px;
        color: #C8CDD6;
        background: #101217;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.3px;
    }

    QLabel {
        color: #D9DDE5;
        font-size: 13px;
    }

    QLabel#statusLabel {
        background: #13161C;
        border: 1px solid #2A303B;
        border-radius: 12px;
        padding: 11px 12px;
        font-size: 13px;
        font-weight: 700;
    }

    QPushButton {
        min-height: 36px;
        padding: 0 14px;
        background: #1C2028;
        color: #ECEFF4;
        border: 1px solid #2A303B;
        border-radius: 10px;
        font-size: 13px;
        font-weight: 600;
    }

    QPushButton:hover {
        background: #242933;
        border-color: #3B4352;
    }

    QPushButton:pressed {
        background: #15181F;
    }

    QPushButton:disabled {
        color: #6F7683;
        background: #171A20;
        border-color: #232833;
    }

    QPushButton#primaryBtn {
        background: #E7E9ED;
        color: #111318;
        border: none;
        font-weight: 700;
    }

    QPushButton#primaryBtn:hover {
        background: #FFFFFF;
    }

    QPushButton#primaryBtn:pressed {
        background: #D1D5DB;
    }

    QPushButton#dangerBtn {
        color: #FF858F;
        background: #21171A;
        border: 1px solid #49262B;
    }

    QPushButton#dangerBtn:hover {
        background: #2A191D;
        border-color: #72363D;
    }

    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox {
        min-height: 36px;
        background: #12151B;
        color: #F2F4F7;
        border: 1px solid #2A303B;
        border-radius: 10px;
        padding: 0 10px;
        selection-background-color: #424A58;
        font-size: 13px;
    }

    QLineEdit:hover,
    QSpinBox:hover,
    QDoubleSpinBox:hover,
    QComboBox:hover {
        border-color: #3A424F;
    }

    QLineEdit:focus,
    QSpinBox:focus,
    QDoubleSpinBox:focus,
    QComboBox:focus {
        border-color: #737C8C;
        background: #151920;
    }

    QComboBox::drop-down {
        border: none;
        width: 28px;
    }

    QComboBox QAbstractItemView {
        background: #171A21;
        color: #ECEFF4;
        border: 1px solid #2A303B;
        selection-background-color: #2A303A;
        selection-color: #FFFFFF;
        padding: 5px;
    }

    QCheckBox {
        spacing: 9px;
        color: #D7DBE3;
        font-size: 13px;
    }

    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border-radius: 6px;
        border: 1px solid #3A414D;
        background: #12151B;
    }

    QCheckBox::indicator:hover {
        border-color: #697282;
    }

    QCheckBox::indicator:checked {
        background: #E7E9ED;
        border-color: #E7E9ED;
    }

    QCheckBox::indicator:checked:hover {
        background: #FFFFFF;
        border-color: #FFFFFF;
    }

    QSlider::groove:horizontal {
        height: 4px;
        background: #2C323D;
        border-radius: 2px;
    }

    QSlider::sub-page:horizontal {
        background: #AEB5C2;
        border-radius: 2px;
    }

    QSlider::add-page:horizontal {
        background: #2C323D;
        border-radius: 2px;
    }

    QSlider::handle:horizontal {
        width: 16px;
        margin: -6px 0;
        border-radius: 8px;
        background: #F1F3F6;
        border: 1px solid #A8AFBB;
    }

    QScrollArea {
        border: none;
        background: transparent;
    }

    QScrollBar:vertical {
        width: 9px;
        border: none;
        background: transparent;
        margin: 3px 0;
    }

    QScrollBar::handle:vertical {
        background: #343A45;
        min-height: 40px;
        border-radius: 4px;
    }

    QScrollBar::handle:vertical:hover {
        background: #48505D;
    }

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        height: 0;
    }
""")
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(16)

        # Scroll Area for all content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(14)

        # 1. System Status Group
        power_group = QGroupBox("System Management")
        power_layout = QVBoxLayout()
        
        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.update_status_label()
        power_layout.addWidget(self.status_label)
        
        btn_row = QHBoxLayout()
        start_btn = QPushButton("Start Pet")
        start_btn.clicked.connect(self.handle_start)
        btn_row.addWidget(start_btn)
        
        stop_btn = QPushButton("Stop Pet")
        stop_btn.setObjectName("dangerBtn")
        stop_btn.clicked.connect(self.handle_stop)
        btn_row.addWidget(stop_btn)
        
        power_layout.addLayout(btn_row)
        power_group.setLayout(power_layout)
        content_layout.addWidget(power_group)
        
        # 2. Character Configuration Group
        char_group = QGroupBox("Character Configuration")
        char_layout = QVBoxLayout()
        
        char_select_layout = QHBoxLayout()
        char_select_layout.addWidget(QLabel("Active Profile:"))
        self.char_combo = QComboBox()
        for char_id, profile in CHARACTER_PROFILES.items():
            self.char_combo.addItem(profile["name"], char_id)
            
        current_char = getattr(self.pet, 'current_character', 'dragon')
        index = self.char_combo.findData(current_char)
        if index >= 0:
            self.char_combo.setCurrentIndex(index)
            
        self.char_combo.currentIndexChanged.connect(self.handle_character_change)
        char_select_layout.addWidget(self.char_combo)
        char_layout.addLayout(char_select_layout)
        
        mood_btn_row = QHBoxLayout()
        feed_btn = QPushButton("Feed Companion")
        feed_btn.clicked.connect(self.trigger_feed)
        mood_btn_row.addWidget(feed_btn)
        
        annoy_btn = QPushButton("Annoy Companion")
        annoy_btn.clicked.connect(self.trigger_annoy)
        mood_btn_row.addWidget(annoy_btn)
        char_layout.addLayout(mood_btn_row)
        
        char_group.setLayout(char_layout)
        content_layout.addWidget(char_group)

        # 3. Dynamic Actions Group
        self.anim_group = QGroupBox("Supported Actions")
        self.anim_layout = QVBoxLayout()
        self.anim_group.setLayout(self.anim_layout)
        self.refresh_dynamic_actions()
        content_layout.addWidget(self.anim_group)
        
        # 4. Communications (AI Chat)
        ai_group = QGroupBox("Communications (AI)")
        ai_layout = QVBoxLayout()
        
        ai_config_layout = QHBoxLayout()
        self.ai_enable_chk = QCheckBox("Enable AI Chat Integration")
        self.ai_enable_chk.setChecked(self.pet.ai.enabled)
        self.ai_enable_chk.toggled.connect(self.toggle_ai)
        ai_config_layout.addWidget(self.ai_enable_chk)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("API Key (or use .env)")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.textChanged.connect(self.update_api_key)
        ai_config_layout.addWidget(self.api_key_input)
        
        ai_layout.addLayout(ai_config_layout)
        
        chat_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Enter message payload...")
        self.chat_input.returnPressed.connect(self.send_chat)
        chat_layout.addWidget(self.chat_input)
        
        self.send_btn = QPushButton("Transmit")
        self.send_btn.setObjectName("primaryBtn")
        self.send_btn.clicked.connect(self.send_chat)
        chat_layout.addWidget(self.send_btn)
        ai_layout.addLayout(chat_layout)
        
        util_layout = QHBoxLayout()
        self.clear_btn = QPushButton("Clear Memory")
        self.clear_btn.clicked.connect(self.clear_chat)
        util_layout.addWidget(self.clear_btn)
        ai_layout.addLayout(util_layout)
        
        ai_group.setLayout(ai_layout)
        content_layout.addWidget(ai_group)
        
        # 5. Focus Timer (Pomodoro)
        pomo_group = QGroupBox("Focus Timer")
        pomo_layout = QVBoxLayout()
        
        spin_layout = QHBoxLayout()
        spin_layout.addWidget(QLabel("Work (mins):"))
        self.work_spin = QSpinBox()
        self.work_spin.setRange(1, 120)
        self.work_spin.setValue(self.pet.pomodoro.work_duration // 60)
        self.work_spin.valueChanged.connect(self.update_pomo)
        spin_layout.addWidget(self.work_spin)
        
        spin_layout.addWidget(QLabel("Break (mins):"))
        self.break_spin = QSpinBox()
        self.break_spin.setRange(1, 30)
        self.break_spin.setValue(self.pet.pomodoro.break_duration // 60)
        self.break_spin.valueChanged.connect(self.update_pomo)
        spin_layout.addWidget(self.break_spin)
        pomo_layout.addLayout(spin_layout)
        
        pomo_btn_layout = QHBoxLayout()
        start_pomo = QPushButton("Initiate Session")
        start_pomo.setObjectName("primaryBtn")
        start_pomo.clicked.connect(lambda: self.pet.start_pomo_safe(self.work_spin.value(), self.break_spin.value()))
        pomo_btn_layout.addWidget(start_pomo)
        
        stop_pomo = QPushButton("Terminate Timer")
        stop_pomo.clicked.connect(self.pet.stop_pomo_safe)
        pomo_btn_layout.addWidget(stop_pomo)
        pomo_layout.addLayout(pomo_btn_layout)
        
        pomo_group.setLayout(pomo_layout)
        content_layout.addWidget(pomo_group)
        
        # 6. System Settings
        behav_group = QGroupBox("System Settings")
        behav_layout = QVBoxLayout()
        
        self.video_chk = QCheckBox("Auto-sleep during video playback")
        self.video_chk.setChecked(getattr(self.pet.mood, 'sleep_on_video', True))
        self.video_chk.toggled.connect(self.toggle_video_sleep)
        behav_layout.addWidget(self.video_chk)
        
        row_wander = QHBoxLayout()
        row_wander.addWidget(QLabel("Wander Frequency:"))
        self.wander_spin = QDoubleSpinBox()
        self.wander_spin.setRange(0.0, 1.0)
        self.wander_spin.setSingleStep(0.01)
        self.wander_spin.setValue(getattr(self.pet, 'wander_chance', 0.02))
        self.wander_spin.valueChanged.connect(self.update_wander)
        row_wander.addWidget(self.wander_spin)
        behav_layout.addLayout(row_wander)
        
        behav_group.setLayout(behav_layout)
        content_layout.addWidget(behav_group)
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def update_status_label(self):
        if getattr(self.pet, 'is_stopped', False):
            self.status_label.setText("Status: Stopped (Pet Hidden)")
            self.status_label.setStyleSheet("color: #FF858F; border-color: #49262B; background: rgba(255, 133, 143, 0.08);")
        else:
            self.status_label.setText("Status: Active (Pet Running)")
            self.status_label.setStyleSheet("color: #65D391; border-color: rgba(101, 211, 145, 0.25); background: rgba(101, 211, 145, 0.08);")

    def handle_start(self):
        self.pet.start_pet_safe()
        self.update_status_label()

    def handle_stop(self):
        self.pet.stop_pet_safe()
        self.update_status_label()

    def handle_character_change(self):
        char_id = self.char_combo.currentData()
        self.pet.switch_character_safe(char_id)
        self.refresh_dynamic_actions()
        
    def refresh_dynamic_actions(self):
        # Clear existing buttons
        while self.anim_layout.count():
            item = self.anim_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
                
        char_id = self.char_combo.currentData() or 'dragon'
        config = get_character_config(char_id)
        actions = config.get("supported_actions", [])
        
        # Create grid of buttons 3 per row
        row_layout = None
        for i, anim in enumerate(actions):
            if i % 3 == 0:
                row_layout = QHBoxLayout()
                self.anim_layout.addLayout(row_layout)
            
            btn = QPushButton(anim.replace('_', ' ').title())
            btn.clicked.connect(lambda checked, a=anim: self.trigger_anim(a))
            row_layout.addWidget(btn)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def trigger_anim(self, anim_name):
        self.pet.trigger_anim_safe(anim_name)
        
    def trigger_feed(self):
        self.pet.feed_safe()
        
    def trigger_annoy(self):
        self.pet.annoy_safe()
        
    def trigger_sleepy(self):
        self.pet.mood.energy = 0
        self.pet.state_machine.force_state('sleep')

    def update_pomo(self):
        self.pet.pomodoro.work_duration = self.work_spin.value() * 60
        self.pet.pomodoro.break_duration = self.break_spin.value() * 60

    def update_wander(self):
        self.pet.wander_chance = self.wander_spin.value()

    def set_ai_loading(self, loading: bool):
        self.send_btn.setEnabled(not loading)
        self.clear_btn.setEnabled(not loading)
        self.chat_input.setEnabled(not loading)

    def toggle_video_sleep(self, checked):
        self.pet.mood.sleep_on_video = checked

    def toggle_ai(self, checked):
        self.pet.ai.set_enabled(checked)
        
    def update_api_key(self, text):
        self.pet.ai.set_api_key(text)
        
    def send_chat(self):
        text = self.chat_input.text().strip()
        if text:
            self.pet.process_chat_safe(text)
            self.chat_input.clear()
            
    def clear_chat(self):
        self.pet.ai.clear_memory()
        self.pet.say_safe("Memory cleared!")
