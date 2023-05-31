from coverage import coverage
from PIL import Image, ImageDraw, ImageFont


if __name__ == "__main__":
    cov = coverage()
    cov.load()
    total = cov.report()

    im = Image.new("RGB", (120, 20))
    fnt = ImageFont.load_default()
    d = ImageDraw.Draw(im)

    d.text((10, 5), "coverage:", fill=(255, 255, 255), font=fnt)
    d.rectangle([(80, 0), (150, 20)], fill=(220, 0, 0))
    d.text((90, 5), "{:.0f}%".format(total), fill=(0, 0, 0), font=fnt)

    im.save("covbadge.jpg")
