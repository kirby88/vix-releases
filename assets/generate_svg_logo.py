import base64
import os

from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(SCRIPT_DIR, "logo_640.png")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "logo.svg")


def crop_and_encode(path: str) -> tuple[str, int, int]:
    """Crop transparent borders and return (data_uri, width, height)."""
    import numpy as np
    with Image.open(path) as img:
        arr = np.array(img)
    alpha = arr[:, :, 3]
    rows = np.any(alpha > 0, axis=1)
    cols = np.any(alpha > 0, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    cropped = Image.fromarray(arr[rmin:rmax+1, cmin:cmax+1])
    import io
    buf = io.BytesIO()
    cropped.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    w, h = cropped.size
    return f"data:image/png;base64,{encoded}", w, h


def build_svg(image_data: str, width: int, height: int) -> str:
    beam_width = int(width * 0.20)
    start_x = -beam_width
    end_x = width + beam_width

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <!-- Soft bell-curve gradient: transparent → white → transparent -->
    <linearGradient id="beamGrad" x1="0" y1="0" x2="1" y2="0" gradientUnits="objectBoundingBox">
      <stop offset="0%"   stop-color="white" stop-opacity="0"/>
      <stop offset="40%"  stop-color="white" stop-opacity="0.3"/>
      <stop offset="50%"  stop-color="white" stop-opacity="0.55"/>
      <stop offset="60%"  stop-color="white" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="white" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <!-- Logo (transparent background preserved) -->
  <image
    href="{image_data}"
    x="0" y="0"
    width="{width}" height="{height}"
    image-rendering="optimizeQuality"
  />

  <!-- Sweeping light beam over the logo -->
  <rect
    x="0" y="0"
    width="{beam_width}" height="{height}"
    fill="url(#beamGrad)"
    style="mix-blend-mode: screen"
  >
    <animateTransform
      attributeName="transform"
      type="translate"
      from="{start_x} 0"
      to="{end_x} 0"
      dur="2.4s"
      repeatCount="indefinite"
      calcMode="linear"
    />
  </rect>
</svg>
"""


def main():
    print(f"Reading {INPUT_PATH}...")
    image_data, width, height = crop_and_encode(INPUT_PATH)
    print(f"Cropped size: {width}x{height}, data URI length: {len(image_data)}")
    svg = build_svg(image_data, width, height)
    with open(OUTPUT_PATH, "w") as f:
        f.write(svg)
    size_kb = os.path.getsize(OUTPUT_PATH) / 1024
    print(f"Written {OUTPUT_PATH} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
