# 3DS2PNG
---
**Filter and Render PNGs from raw HANS screencaptures**

### Purpose

Smealum's HANS allows users to capture raw screen images on the 3DS to a single
file on the system's SD card. A second tool, scrtool can iterate over the raw
data in this file and extract PNG images from it, which is totally awesome.

Unfortunately, the process involves tying up your 3DS while the images are
created. 3DS2PNG provides a way to extract these images on your computer
allowing you to copy the raw_screenshots.bin file, and then resuming play
shortly after. It also provides the ability to filter screen captures,
ignoring the top left, top right, or bottom screens rather than rendering images
which are either blank (in the case of 2D games) or generally unwanted
(such as the bottom screen in Virtual Console titles).

### Requirements

The script requires Python 3.5 (though earlier versions will likely work), as
well as an installation of Pillow. Windows binaries are planned for a future
date (though Python and Pillow on Windows should work fine).
Usage

```
python3 3ds2png.py
```

You may provide a raw_screenshot.bin file either as a parameter or by dragging
it onto the script/executable. Additional settings can be modified in
```config.ini``` such as input/output paths and screens to skip rendering.

### Issues

Currently two methods of of parsing the raw screen information are used
(the same as scrtool). One of these methods seems to produce inaccurate
colors (very red if the Pokémon TCG VC rom is any indication), this needs to be
adjusted at some point.

### Credits

Program createdby Dr. Dos.<br>
Thanks to Smealum for HANS and scrtool
