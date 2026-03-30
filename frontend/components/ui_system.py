import flet as ft

# Base colors
BG_DARK = "#0F172A"
SURFACE = "#1E293B"
PRIMARY = "#8B5CF6"
SECONDARY = "#3B82F6"
TEXT_SECONDARY = "#94A3B8"

# Glass Container
class GlassContainer(ft.Container):
    def __init__(self, content, padding=20, expand=False):
        super().__init__()
        self.content = content
        self.padding = padding
        self.expand = expand
        self.border_radius = 20
        self.bgcolor = ft.Colors.with_opacity(0.08, ft.Colors.WHITE)
        self.border = ft.Border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE))
        self.blur = ft.Blur(20, 20)

# Modern button
class PrimaryButton(ft.Container):
    def __init__(self, text, on_click):
        super().__init__()
        self.content = ft.Text(text, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
        self.alignment = ft.Alignment(0, 0)
        self.height = 50
        self.padding = ft.Padding.symmetric(horizontal=20, vertical=10)
        self.margin = ft.Margin.symmetric(vertical=5)
        self.border_radius = 12
        self.gradient = ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=[PRIMARY, SECONDARY]
        )
        self.on_click = on_click
        self.on_hover = self._hover
        self.mouse_cursor = "pointer"
        self.animate = ft.Animation(200)

    def _hover(self, e):
        self.scale = 1.03 if e.data == "true" else 1
        self.update()