import configparser
import sys
import os
import time

from PIL import Image


SCREENS = {b"SCR0": "TL", b"SCR1": "TR", b"SCR2": "BT"}
SIZES = {"TL": (400, 240), "TR": (400, 240), "BT": (320, 240)}


def main():
    timestamp = str(int(time.time()))
    if not os.path.isfile("config.ini"):
        print("config.ini file not found! Aborting.")
        return False

    config = configparser.ConfigParser()
    config.read("config.ini")

    if len(sys.argv) != 2:
        if config["IO"]["Default File"]:
            source_file_name = config["IO"]["Default File"]
    else:
        source_file_name = sys.argv[1]

    output_dir = config["IO"]["Output Directory"]
    ignored = config["Screens"]["Ignored Screens"]
    if "," in ignored:
        ignored = ignored.split(",")
    else:
        ignored = [ignored]

    print("Loading", source_file_name)
    fh = open(source_file_name, "rb")
    data = fh.read()
    print("Loaded.")

    set_count = 1
    png_count = 1

    while True:
        # 2nd SCR0 makes looping easier, skip it in the for-loop
        order = [b"SCR0", b"SCR1", b"SCR2", b"SCR0"]
        for screen_idx in range(0, len(order) - 1):
            screen_key = order[screen_idx]

            proc_string = "Processing: Set {} Image {} - [{}]"
            print(proc_string.format(set_count,
                                     png_count,
                                     SCREENS[screen_key])
                  end=" ", flush=True)

            # Find start of current picture and start of next (to find the end)
            start = data.find(screen_key) + len(screen_key)

            if screen_key != b"SCR2":
                end = data.find(order[screen_idx+1]) + len(order[screen_idx+1])
            else:
                end_loc = data[4:].find(order[screen_idx+1])
                if end_loc == -1:  # Last screenshot
                    end = -1
                else:
                    end = end_loc + len(order[screen_idx+1]) + 4

            # That range is the raw screenshot data
            raw = data[start:end]

            # Output path/filename
            output_format = config["IO"]["Output Format"]
            input_fn = os.path.splitext(os.path.basename(source_file_name))[0]
            output_format = output_format.replace("$I", input_fn)
            output_format = output_format.replace("$T", timestamp)
            output_format = output_format.replace("$S", str(set_count))
            output_format = output_format.replace("$P", str(png_count))
            output_format = output_format.replace("$K", SCREENS[screen_key])
            output = os.path.join(output_dir, output_format)+".png"

            os.makedirs(os.path.dirname(output), exist_ok=True)

            # Render it
            if SCREENS[screen_key] not in ignored:
                success = render(raw, SCREENS[screen_key], output)
                if success:
                    print("OK!")
                else:
                    print("FAILURE!")
            png_count += 1

        data = data[end - 4:]  # First bytes for next png should be SCR#
        set_count += 1

        if end == -1:
            break

    print("DONE.")
    return True


def render(raw, screen, output):
    size = SIZES[screen]

    # Create the image
    im = Image.new("RGB", size, "red")
    pixel_idx = 0

    method = int.from_bytes(raw[8:9], byteorder="little")

    if method == 208:
        for x in range(0, size[0] + 1):  # 2nd Draw from left to right
            # Do not question the extra pixel in the width.
            for y in range(size[1] - 1, -1, -1):  # Draw pixels bottom to top
                true_x = x
                true_y = y

                # Move the bottom that's first to the actual bottom
                if y <= 70:
                    true_y = size[1] - 71 + y
                else:
                    true_y = y - 71

                # Shift slightly left
                if true_y < (size[1] - 71):
                    true_x = x - 1

                color_r = raw[pixel_idx]
                color_g = raw[pixel_idx + 2]
                color_b = raw[pixel_idx + 1]

                set_pixel(im, true_x, true_y, color_r, color_g, color_b)
                pixel_idx += 3
    elif method == 224:
        for x in range(0, size[0] + 1):  # 2nd Draw from left to right
            # Do not question the extra pixel in the width.
            for y in range(size[1] - 1, -1, -1):  # Draw pixels bottom to top
                true_x = x
                true_y = y

                # Move the bottom that's first to the actual bottom
                if y >= 226:
                    true_y = y - 226
                else:
                    true_y = y + 14

                # Shift slightly left
                if true_y < 14:
                    true_x = x - 1

                color = int.from_bytes(raw[pixel_idx:pixel_idx+2],
                                       byteorder="little")
                bits = bin(color)[2:]

                # Thanks to Smealum for these values
                color_b = (color & 0x1F) << 3
                color_g = ((color >> 5) & 0x3F) << 2
                color_r = ((color >> 11) & 0x1F) << 3

                set_pixel(im, true_x, true_y, color_r, color_g, color_b)
                pixel_idx += 2
    else:
        print("UNKNOWN DECODING METHOD:", method, end=" ", flush=True)
        return False

    im.save(output + ".png")
    return True


def set_pixel(im, x, y, color_r, color_g, color_b):
    try:
        im.putpixel((x, y), (color_r, color_g, color_b))
    except IndexError:
        # Being lazy with pixels shifting means ignore these
        pass
    except Exception as e:
        print(e)
        print("Couldn't place pixel at", x, y)

if __name__ == "__main__":
    main()
