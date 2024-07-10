from PIL import Image


def create_icns(input_file, output_file):
    img = Image.open(input_file)
    img.save(output_file, format='ICNS')


# Provide the paths to your input .ico file and output .icns file
create_icns('icon/LukeWare.ico', 'icon/LukeWare.icns')
