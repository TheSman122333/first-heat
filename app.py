"""Web entry point for hosting FirstHeat (used by Vercel).
The desktop app still starts from main.py with ft.run(main)."""
import flet_web.fastapi as flet_fastapi

from main import main

app = flet_fastapi.app(main)
