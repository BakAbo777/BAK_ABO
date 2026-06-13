from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image


@dataclass
class ImageProcessor:
    output_dir: Path

    def inspect_image(self, path: Path) -> dict[str, Any]:
        with Image.open(path) as image:
            return {
                "path": str(path),
                "width": image.width,
                "height": image.height,
                "mode": image.mode,
                "format": image.format,
            }

    def optimize_copy(self, source: Path, target: Path, quality: int = 90) -> Path:
        target.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(source) as image:
            image.save(target, quality=quality, optimize=True)
        return target

