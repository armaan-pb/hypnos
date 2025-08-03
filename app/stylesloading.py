import os

def load_stylesheet(accent_color):
    """
    Loads the QSS stylesheet and replaces placeholder variables
    with theme values.

    Parameters:
        accent_color (str): Main accent color for the app (hex format).

    Returns:
        str: Final QSS stylesheet as a string.
    """
    theme_vars = {
        "{{BG_DARK}}": "#121212",
        "{{BG_PANEL}}": "#181818",
        "{{BG_TITLEBAR}}": "#202030",
        "{{BG_INPUT}}": "#2a2a2a",
        "{{BG_HOVER}}": "#2e2e40",
        "{{ACCENT}}": accent_color,
        "{{ACCENT_HOVER}}": "#ff6666",
        "{{ACCENT_PRESS}}": "#cc0000",
        "{{BORDER}}": "#444",
        "{{TEXT}}": "#ffffff",
        "{{TEXT_MUTED}}": "#888",
        "{{GRIDLINE}}": "#444",
    }

    style_path = os.path.join(os.path.dirname(__file__), "styles.qss")
    try:
        with open(style_path, "r") as f:
            style = f.read()
    except FileNotFoundError:
        raise RuntimeError(f"Stylesheet file not found: {style_path}")

    for placeholder, value in theme_vars.items():
        style = style.replace(placeholder, value)

    return style
