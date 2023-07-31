from astropy.io import fits

def get_image_from_path(source_path):
    image = fits.getdata(source_path, ext=0)
    image.shape = image.shape[2:]
    return image