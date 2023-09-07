from PIL import Image
from string import Template
import os

dir_path = ".\source"
dist_path = ".\generated"

os.makedirs(dist_path, exist_ok=True)
os.makedirs(dir_path, exist_ok=True)


def create_file_if_needed(path, content):
    try:
        my_file = open(path, "r")
        print("File Exists")
    except IOError:
        my_file = open(path, "w+", encoding="utf-8")
        print("File is Created")
        my_file.write(content)
    finally:
        my_file.close()


def get_template(path):
    template_file = open(path, "r", encoding="utf-8")
    template = template_file.read()
    template_file.close()
    return Template(template)


def open_file(path):
    opened_file = open(path, "r", encoding="utf-8")
    file = opened_file.read()

    return file


def docs_file():
    path = "README.md"
    content = """
    source - pliki źródłowe
    generated - pliki wyjściowe
    resolutions - plik z rozdzielczościami
    image.tpl - plik odpowiadający za generowanie kodu znacznika img
    srcset.tpl - plik odpowiadający za generowanie zawartości atrybutu srcset wewnątrz znacznika img
    srcset.tpl - plik odpowiadający za ciąg znaków oddzielających wartości srcset
    picture.tpl - plik odpowiadający za generowanie kodu znacznika picture
    source.tpl - plik odpowiadający za generowanie zawartości znacznika source wewnątrz picture
    source_separator.tpl - plik odpowiadający za ciąg znaków oddzielających znaczniki source
    """
    docs = open(path, "w", encoding="utf-8")
    docs.write(content)
    docs.close()


def resolutions_file():
    path = "resolutions.csv"
    resolutions = []
    try:
        my_file = open(path, "r")
        print("File Exists")
        for line in my_file.readlines():
            resolutions.append(line)
    except IOError:
        my_file = open(path, "w+")
        print("File is Created")
        resolutions = ["150\n", "300\n", "256\n", "512\n", "800\n", "1024\n", "1600\n"]
        my_file.writelines(resolutions)
    finally:
        my_file.close()
        return [int(res.replace("\n", "")) for res in resolutions]


create_file_if_needed(
    "image.tpl",
    """<img
    alt="${file_name}"
    srcset="
        ${srcsets}
    "
    src="${file_name}-${resolution}w.${ext}"
/>""",
)
create_file_if_needed("srcset.tpl", "${file_name}-${resolution}w.${ext} ${resolution}w")
create_file_if_needed(
    "srcset_separator.tpl",
    """,\n\t\t""",
)
create_file_if_needed(
    "picture.tpl",
    """<picture>
    ${srcsets}
    <img src="${file_name}.${ext}" alt="">
</picture>
/>""",
)
create_file_if_needed(
    "source.tpl",
    """<source media="(min-width:${resolution}px)" srcset="${file_name}-${resolution}w.${ext}">""",
)
create_file_if_needed(
    "source_separator.tpl",
    """\n\t""",
)

docs_file()
res_list = resolutions_file()
img_tags = []
picture_tags = []
for path in os.listdir(dir_path):
    if os.path.isfile(os.path.join(dir_path, path)):
        image = Image.open(f"{dir_path}\{path}")
        print(f"Original size : {image.size}")
        width, height = image.size
        ratio = height / width
        new_name, ext = path.split(".")

        srcsets = []
        sources = []
        for resolution in res_list:
            srcset_template = get_template("srcset.tpl")
            srcset = srcset_template.substitute(
                ext=ext, file_name=new_name, resolution=resolution
            )
            srcsets.append(srcset)
            source_template = get_template("source.tpl")
            source = source_template.substitute(
                ext=ext, file_name=new_name, resolution=resolution
            )
            sources.append(source)
            image_resized = image.resize((resolution, int(resolution * ratio)))
            image_resized.save(f".\generated\{new_name}_{resolution}w.{ext}")

        source_separator = (
            open_file("source_separator.tpl")
            .replace("\\n", "\n")
            .replace("\\t", "\t")
            .replace("\\w", "\w")
        )
        srcset_separator = (
            open_file("srcset_separator.tpl")
            .replace("\\n", "\n")
            .replace("\\t", "\t")
            .replace("\\w", "\w")
        )
        srcset_attribute = srcset_separator.join(srcsets)
        picture_content = source_separator.join(sources)
        img_template = get_template("image.tpl")
        img_tag = img_template.substitute(
            srcsets=srcset_attribute,
            file_name=new_name,
            ext=ext,
            resolution=res_list[-1],
        )
        img_tags.append(img_tag)

        picture_template = get_template("picture.tpl")
        picture_tag = picture_template.substitute(
            srcsets=picture_content,
            file_name=new_name,
            ext=ext,
            resolution=res_list[-1],
        )
        picture_tags.append(picture_tag)
        image.copy().save(f".\generated\{new_name}.{ext}")

images_file = open("images.html", "w")
images_file.write("\n".join(img_tags))
images_file.close()


pictures_file = open("pictures.html", "w")
pictures_file.write("\n".join(picture_tags))
pictures_file.close()
