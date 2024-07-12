from PIL import Image


def create_icns(input_file, output_file):
    """
    Convert an ICO file to an ICNS file.

    Parameters:
    input_file (str): The path to the input ICO file.
    output_file (str): The path to the output ICNS file.

    Example:
    create_icns('icon/LukeWare.ico', 'icon/LukeWare.icns')
    """
    img = Image.open(input_file)
    img.save(output_file, format='ICNS')


# Provide the paths to your input .ico file and output .icns file
create_icns('icons/LukeWare_icon.ico', 'icons/LukeWare_icon.icns')
