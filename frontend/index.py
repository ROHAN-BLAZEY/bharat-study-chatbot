import reflex as rx
import httpx

# Update this to your H200 Ngrok URL or network IP (e.g., [http://192.168.1.50:8000](http://192.168.1.50:8000))
BACKEND_URL = "http://localhost:8000" 

class AppState(rx.State):
    logged_in: bool = False
    is_registering: bool = False
    theme: str = "light"
    auth_error: str = ""
    
    name: str = ""
    email: str = ""
    phone: str = ""
    password: str = ""
    
    language: str = "English"
    tier: str = "Pro"
    chat_input: str = ""
    chat_history: list[dict] = []
    active_kb: str = "Connected to ChromaDB"

    def authenticate(self):
        self.auth_error = ""
        endpoint = "/api/register" if self.is_registering else "/api/login"
        payload = {"name": self.name, "email": self.email, "phone": self.phone, "password": self.password}
        
        try:
            res = httpx.post(f"{BACKEND_URL}{endpoint}", json=payload, timeout=10.0)
            if res.status_code == 200:
                if self.is_registering:
                    self.is_registering = False
                else:
                    self.logged_in = True
            else:
                self.auth_error = res.json().get("detail", "Error authenticating.")
        except Exception:
            self.auth_error = "Could not connect to H200 backend."

    def send_message(self):
        if not self.chat_input:
            return
            
        self.chat_history.append({"role": "user", "text": self.chat_input, "sources": []})
        data = {"prompt": self.chat_input, "tier": self.tier}
        
        try:
            res = httpx.post(f"{BACKEND_URL}/api/chat", data=data, timeout=45.0)
            if res.status_code == 200:
                reply = res.json()
                self.chat_history.append({
                    "role": "bot", 
                    "text": reply["response"], 
                    "sources": reply["sources"],
                    "model": reply["model"]
                })
        except Exception:
            self.chat_history.append({"role": "bot", "text": "Failed to reach AI Engine.", "sources": []})
            
        self.chat_input = ""

def glass_card(*children, **kwargs):
    return rx.vstack(
        *children, bg="rgba(255, 255, 255, 0.65)", backdrop_filter="blur(16px)",
        border="1px solid rgba(255, 255, 255, 0.3)", border_radius="1.5rem",
        box_shadow="0 8px 32px 0 rgba(31, 38, 135, 0.07)", **kwargs
    )

def login_screen() -> rx.Component:
    return rx.center(
        glass_card(
            rx.heading("Bharat Study Chatbot", size="8", weight="bold", color="indigo.900"),
            rx.cond(AppState.auth_error, rx.text(AppState.auth_error, color="red.500", size="2")),
            rx.select(["light", "dark"], value=AppState.theme, on_change=AppState.set_theme),
            rx.cond(AppState.is_registering, rx.input(placeholder="Full Name", on_change=AppState.set_name, size="3", width="100%")),
            rx.cond(AppState.is_registering, rx.input(placeholder="Phone Number", on_change=AppState.set_phone, size="3", width="100%")),
            rx.input(placeholder="Email Address", on_change=AppState.set_email, size="3", width="100%"),
            rx.input(placeholder="Password", type="password", on_change=AppState.set_password, size="3", width="100%"),
            rx.button("Enter Chatbot", on_click=AppState.authenticate, size="4", width="100%", bg="linear-gradient(90deg, #4F46E5, #7C3AED)"),
            rx.button(rx.cond(AppState.is_registering, "Back to Login", "Create Account"), on_click=lambda: AppState.set_is_registering(~AppState.is_registering), variant="ghost"),
            padding="3rem", width="400px", spacing="4"
        ), height="100vh", bg="linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%)"
    )

def sidebar() -> rx.Component:
    return rx.vstack(
        rx.heading("Settings", size="5"), rx.divider(),
        rx.text("Regional Language", weight="medium", size="2"),
        rx.select(["English", "Hindi", "Tamil", "Telugu", "Kannada", "Marathi"], value=AppState.language, on_change=AppState.set_language),
        rx.text("AI Tier Speed", weight="medium", size="2", margin_top="4"),
        rx.select(["Fast", "Fast-Elite", "Pro"], value=AppState.tier, on_change=AppState.set_tier),
        rx.spacer(), rx.text("Current Affairs Recap", weight="medium", size="2"), rx.date_picker(),
        width="260px", height="100%", padding="1.5rem", bg="gray.50", border_right="1px solid #eaeaea"
    )

def chat_interface() -> rx.Component:
    return rx.hstack(
        rx.desktop_only(sidebar()),
        rx.vstack(
            rx.hstack(
                rx.badge(f"🟢 {AppState.active_kb}", color_scheme="green", variant="soft"), rx.spacer(),
                rx.badge(f"Tier: {AppState.tier}", color_scheme="indigo", variant="surface"),
                width="100%", padding="1rem", border_bottom="1px solid #eaeaea"
            ),
            rx.box(
                rx.foreach(
                    AppState.chat_history,
                    lambda msg: rx.vstack(
                        rx.box(rx.text(msg["text"]), bg=rx.cond(msg["role"] == "user", "indigo.500", "gray.100"), color=rx.cond(msg["role"] == "user", "white", "black"), padding="1rem", border_radius="1rem"),
                        rx.cond(
                            msg["sources"],
                            rx.hstack(rx.text("Sources Consulted:", size="1", color="gray.500", weight="bold"), rx.foreach(msg["sources"], lambda s: rx.badge(s, size="1", color_scheme="gray")), rx.badge(msg["model"], size="1", color_scheme="blue"))
                        ),
                        align_items=rx.cond(msg["role"] == "user", "flex-end", "flex-start"), width="100%", padding_y="0.5rem"
                    )
                ), flex="1", width="100%", padding="2rem", overflow_y="auto"
            ),
            rx.hstack(
                rx.upload(rx.icon(tag="paperclip", size=20, color="gray.500"), id="file_upload", padding="0.5rem", border="none", cursor="pointer"),
                rx.input(placeholder="Message Dual RAG System...", value=AppState.chat_input, on_change=AppState.set_chat_input, width="100%", radius="full", size="3"),
                rx.button(rx.icon(tag="send"), on_click=AppState.send_message, color_scheme="indigo", radius="full"),
                width="92%", margin_bottom="1rem", padding="0.5rem", border="1px solid #eaeaea", border_radius="2rem", bg="white", box_shadow="sm"
            ), width="100%", height="100vh"
        ), width="100vw", height="100vh"
    )

@rx.page(route="/")
def index() -> rx.Component:
    return rx.cond(AppState.logged_in, chat_interface(), login_screen())

app = rx.App(theme=rx.theme(appearance="light"))