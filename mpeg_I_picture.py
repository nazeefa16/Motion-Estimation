from PIL import Image
import numpy as np
from scipy.fft import dct, idct

DEFAULT_Q_TABLE = np.array([  [ 8, 16, 19, 22, 26, 27, 29, 34],  
                              [16, 16, 22, 24, 27, 29, 34, 37],  
                              [19, 22, 26, 27, 29, 34, 34, 38],  
                              [22, 22, 26, 27, 29, 34, 37, 40],  
                              [22, 26, 27, 29, 32, 35, 40, 48],  
                              [26, 27, 29, 32, 35, 40, 48, 58],  
                              [26, 27, 29, 34, 38, 46, 56, 69],  
                              [27, 29, 35, 38, 46, 56, 69, 83]])
                              

# MPEG-1 Quantisation Process

def quantize(block, p):
    q_block = (16.0 * block) / (DEFAULT_Q_TABLE * p)
    return np.round(q_block)
    

def dequantize(block, p):
    return block / 16 * DEFAULT_Q_TABLE * p
    

# Two dimensional DCT
# Block size is not specified, but in MPEG-1 the Transform Unit is always 8x8

def forward_dct2(a):
    return dct(dct(a, norm='ortho', axis=0), norm='ortho', axis=1)

def inverse_dct2(a):
    return idct(idct(a, norm='ortho', axis=0), norm='ortho', axis=1)
    

# The MPEG-1 process quantise the DCT coefficients
# Should be 16-235 (luma) or 16-240 (Chroma)
# But use full range for simplicity (we use YCbCr images in PIL which use the JPEG range)

def component_to_quantised_dct(cpt, p):
    return quantize(forward_dct2(cpt), p)
    
def quantised_dct_to_component(dct, p):
    return np.clip(inverse_dct2(dequantize(dct, p)), 0, 255)
    
    
# The MPEG-1 Picture structure
# Picture > Slice > Macroblock > Coding Block

def image_to_slices(image):
    slices = []
    
    for r in range(0, image.height, 16):
        slices.append(image.crop((0, r, image.width, r + 16)))
        
    return slices
    
def slice_to_macroblocks(slice):
    macroblocks = []
    
    for c in range(0, slice.width, 16):
        mb = slice.crop((c, 0, c + 16, slice.height))
        (y, cb, cr) = mb.convert('YCbCr').split()
        # at this point chroma subsample Cb and Cr (cheating here with a resize! 16x16 -> 8x8)
        macroblocks.append((y, cb.resize((8,8)), cr.resize((8,8))))
        
    return macroblocks
    
def macroblock_to_blocks(mb):    
    y = np.asarray(mb[0])
    cb = np.asarray(mb[1])
    cr = np.asarray(mb[2])
    
    blocks = list(map(lambda m: np.hsplit(m,2), np.vsplit(y, 2)))
    blocks = [item for sublist in blocks for item in sublist]      # flatten the nested split Y
    
    blocks.append(cb)
    blocks.append(cr)
    
    return blocks
    
    
# Code the blocks in a macroblock

def code_macroblock(mb, p):
    blocks = macroblock_to_blocks(mb)
    q_dct_coefficients = []
    
    for b in blocks:
        q_dct_coefficients.append(component_to_quantised_dct(b, p))
    
    return q_dct_coefficients
   
 
# Code the picture 
    
def code_picture(image, p):
    coded = []
    
    slices = image_to_slices(image)
    
    for slice in slices:
        macroblocks = slice_to_macroblocks(slice)
        
        for macroblock in macroblocks:
            coded_blocks = code_macroblock(macroblock, p)
            coded.append(coded_blocks)
            
    return coded
    
    
# The encoding and decoding applications must decode the MPEG-1 
# representation of the picture
# We reconstruct a YCbCr image

def reconstruct_picture(size, coded, p):
    width, height = size
    
    reconstructed_image = Image.new('YCbCr', size)
    
    for index, blocks in enumerate(coded):
        yb = []
        for i in range(0, 4):
            yb.append(quantised_dct_to_component(blocks[i], p))
            
        cb = quantised_dct_to_component(blocks[4], p)
        cr = quantised_dct_to_component(blocks[5], p)
        
        full_y = np.vstack((np.hstack((yb[0], yb[1])), np.hstack((yb[2], yb[3]))))
        
        i_y = Image.fromarray(full_y.astype('uint8'))
        i_cb = Image.fromarray(cb.astype('uint8')).resize((16,16))
        i_cr = Image.fromarray(cr.astype('uint8')).resize((16,16))
        
        
        mb_image = Image.merge('YCbCr', (i_y, i_cb, i_cr))
        row = index // (width // 16)
        column = index % (width // 16)
        reconstructed_image.paste(mb_image, (column * 16, row * 16))
        
    return reconstructed_image

    

    
    
