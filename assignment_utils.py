import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import Axes3D
from tabulate import tabulate


def colour_histogram(image):
    colours = ("red", "green", "blue")
    channel_ids = (0, 1, 2)
    total_colours = count_RGB_colours(image)
    
    image_data = np.asarray(image)
    # create the histogram plot, with three lines, one for each colour component
    plt.figure(figsize=(10,6))
    plt.xlim([-10, 265])
    for channel_id, c in zip(channel_ids, colours):
        histogram, bin_edges = np.histogram(image_data[:, :, channel_id], bins=256, range=(0, 256))
        plt.bar(bin_edges[0:-1], histogram, color=c, alpha=0.4)
    
    plt.text(20, np.max(histogram), " RGB colours: " + str(total_colours))
    plt.xlabel("Component value")
    plt.ylabel("Pixel Count")
    
    plt.show()
    
    
def show_colour_cubes(cube_list):
    fig = plt.figure(figsize=(12, 7))
    ax = Axes3D(fig)
    cube_colours = iter(cm.rainbow(np.linspace(0, 1, len(cube_list))))
  
    for cube in cube_list:
        x = cube[:,0]
        y = cube[:,1]
        z = cube[:,2]
        ax.scatter3D(x, y, z, color=next(cube_colours))
    
    plt.title("Colour Cubes")
    ax.set_xlabel("R")
    ax.set_ylabel("G")
    ax.set_zlabel("B")
    plt.show()
 

def count_RGB_colours(img):
    rgb = np.array(img)[:,:,:3]                      #remove the alpha channel
    v = np.dot(rgb.astype(np.uint32),[1,256,65536])  #convert RGB planes into a single number
    return len(np.unique(v))
    
    
def image_psnr(img1, img2, max_value=255):
    """"Calculating peak signal-to-noise ratio (PSNR) between two images."""
    """"A difference of zero (identical images) is returned as PSNR = 100"""
    imgA = img1.convert('RGB')
    imgB = img2.convert('RGB')
    mse = np.mean((np.array(imgA, dtype=np.float32) - np.array(imgB, dtype=np.float32)) ** 2)
    if mse == 0:
        return 100
    return 20 * np.log10(max_value / (np.sqrt(mse)))
    
    
def difference_image(img1, img2):
    d1 = np.asarray(img1.convert('RGB'), dtype=np.int16)   #if we subtract the alpha channels
    d2 = np.asarray(img2.convert('RGB'), dtype=np.int16)   #the result will be invisible
    
    return Image.fromarray(np.absolute(d1 - d2).astype(np.uint8))


def side_by_side(img1, img2):
    '''present images side-by-side for visual comparison'''
    
    dst = Image.new('RGB', (img1.width + img2.width + 10, min(img1.height, img2.height)), color='white')
    dst.paste(img1, (0, 0))
    dst.paste(img2, (img1.width + 10, (img1.height - img2.height) // 2))
    return dst
    
    
def summarise_encoding(size, mbs_dct):
    '''A table of the number of zero coefficients in the six coding blocks of each macroblock'''
    (width, height) = size
    
    table = [[0 for c in range(0, width, 16)] for r in range(0, height, 16)] 
 
    for index, mb_dct in enumerate(mbs_dct):
        row = index // (width // 16)
        column = index % (width // 16)
        
        num_y_dct_zero = 0
        for i in range(0, 4):
            num_y_dct_zero += len(mb_dct.y[i][np.where(mb_dct.y[i] == 0)])
            
        num_cb_zero = len(mb_dct.cb[np.where(mb_dct.cb == 0)])
        num_cr_zero = len(mb_dct.cr[np.where(mb_dct.cr == 0)])
        
        table[row][column] = (np.round(100 * num_y_dct_zero / (4 * 8 * 8), 1), \
                              np.round(100 * num_cb_zero / (8 * 8), 1), \
                              np.round(100 * num_cr_zero / (8 * 8), 1))
        
    return tabulate(table, tablefmt='html')
    
    

    
    