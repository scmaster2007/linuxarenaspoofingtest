from pathlib import Path

from shared_dotfiles.side_tasks._spoof_common.rung import build_rung

config = build_rung(Path(__file__).parent, level=3)
