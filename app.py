import os
import tempfile
from pdf2image import convert_from_path
from PIL import Image
import shutil
import skimage
from skimage import io

Image.MAX_IMAGE_PIXELS = 933120000

def convert_pdf(file_path):
    tempDir = tempfile.mkdtemp()
    """ Extract individual PDF pages and save as ppm (Unfortunately it can only
     output to ppm) """
    images = convert_from_path(
        file_path, output_folder=tempDir, poppler_path=os.path.join(os.getcwd(), 'poppler'))

    """Because pdf2image only supports ppm, we must use pillow to change to tiff"""
    temp_images = []
    for i in range(len(images)):
        image_path = f'{tempDir}/{i}.tiff'
        images[i].save(image_path, 'TIFF')
        temp_images.append(image_path)

    """Creating the image array"""
    images = list(map(Image.open, temp_images))

    """ Creating the blank image here and giving it a width and height based on 
    the tiff images. """
    minWidth = min(i.width for i in images)
    theHeight = 0
    for i, img in enumerate(images):
        theHeight += images[i].height
    merged_image = Image.new(images[0].mode, (minWidth, theHeight))

    """ stitch images back together. For each image in the image list, paste into 
    the blank image"""
    y = 0
    for img in images:
        merged_image.paste(img, (0, y))
        y += img.height

    """save merged image (If we could load libtiff we could compress the tiff files 
    at this step. Since I cannot get libtiff to install on windows we will have 
    huge files)"""
    newFile = file_path.replace('.PDF', '.tiff')
    merged_image.save(newFile, format='TIFF')

    """Now we are reloading these huge files and using scikit-image to deflate them. 
    I tried doing the conversion to tiff using skimage, but from what I can tell 
    it will only output multipage tiff files"""
    uncompressed = io.imread(newFile)
    io.imsave(newFile, uncompressed, plugin='tifffile', compress=5)

    shutil.rmtree(tempDir)


if __name__ == '__main__':
    import tkinter.filedialog
    tkinter.Tk().withdraw()
    pth = tkinter.filedialog.askdirectory()
    if len(pth) > 5:
        for filename in os.listdir(pth):
            if filename.lower().endswith(".pdf"):
                convert_pdf(os.path.join(pth, filename))
