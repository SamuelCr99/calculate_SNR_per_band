from QuasarModel import gauss
from QuasarModel.tools import get_image_from_path as get_image
from QuasarModel.source_model import SourceModel as sm

image = get_image("fits/J0211-0145_C_2019_07_24_pet_map.fits")
gauss_list = sm().process(image)

gauss = gauss_list[0]

print(gauss)