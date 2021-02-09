import cv2
from PIL import ImageFont, ImageDraw, Image
import numpy as np
import argparse


def add_text(img_path,
             font_path,
             output_path,
             loc,
             rgb,
             text_list,
             size,
             log_path="log.txt"):
    fail_list = []
    bk_img = cv2.imread(img_path)
    font = ImageFont.truetype(font_path, size)

    for text in text_list:
        text = text.strip()
        try:
            img_pil = Image.fromarray(bk_img)
            draw = ImageDraw.Draw(img_pil)
            draw.text(loc, text, font=font, fill=rgb)
            added = np.array(img_pil)
            cv2.imwrite("{0}/{1}.jpg".format(output_path, text), added)
        except Exception as e:
            print("{} Failed ".format(text))
            print(e)
            fail_list.extend(text)

    with open(log_path, "w") as f:
        for text in fail_list:
            f.write(text.join("\n"))


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", required=True, help="Text list filepath")
parser.add_argument("-B",
                    "--background",
                    required=True,
                    help="Background image path")
parser.add_argument("-o", "--output", required=True, help="Output path")
parser.add_argument("-f", "--font", required=True, help="font path")
parser.add_argument("-x", "--x", type=int, help="Location x", default=0)
parser.add_argument("-y", "--y", type=int, help="Location y", default=0)
parser.add_argument("-r", "--red", type=int, help="Red", default=0)
parser.add_argument("-g", "--green", type=int, help="Green", default=0)
parser.add_argument("-b", "--blue", type=int, help="Blue", default=0)
parser.add_argument("-s", "--size", type=int, help="Size", default=32)

if __name__ == "__main__":
    args = parser.parse_args()
    with open(args.input, "r") as f:
        texts = f.readlines()
        add_text(args.background,
                 args.font,
                 args.output, (args.x, args.y),
                 (args.red, args.green, args.blue),
                 texts,
                 size=args.size)
