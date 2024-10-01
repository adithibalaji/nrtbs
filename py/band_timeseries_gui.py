'''
A GUI which allows you to visualize the band values inside a square as a time series
>>> interactive_time_series('bin_fil_dir, 'image', 10)
'''
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from dNBR import NBR
from operator import add, sub
import datetime
import numpy as np
import math
from misc import extract_date
import os

fig, ((ax1,ax2),(ax3,ax4),(ax5,ax6)) = plt.subplots(3, 2, figsize=(15,8))
clicks = []
plot_colors = ['b','r','y','k','c','m']

def interactive_time_serise(file_dir,plot_type:str('image or nbr'), width):
    '''
    takes a directory with bin files, an image type, and a square width and creates an interactive plot which allows the user to see band values inside a square as a time series
    '''
    #extracting bin files
    files = os.listdir(file_dir)
    file_list = []
    for n in range(len(files)):
        if files[n].split('.')[-1] == 'bin':
            file_list.append(files[n])
        else:
            continue;
        
    sorted_file_names = sorted(file_list, key=extract_date) #sorting files by date
    
    global params
    params = [NBR(f'{file_dir}/{file}') for file in sorted_file_names]
    
    global square_width
    square_width = width
    #selecting image type
    if plot_type == 'image':
        data = NBR(f'{file_dir}/{sorted_file_names[-1]}')
        image = np.stack([scale(data[0]),scale(data[1]),scale(data[2])], axis=2)
        ax1.imshow(image)
    
    elif plot_type == 'nbr':
        image = NBR(f'{file_dir}/{sorted_file_names[-1]}')[4]
        ax1.imshow(image, cmap='grey')
        
    else:
        print('invalid image type')
    
    cid = fig.canvas.mpl_connect('button_press_event', on_click)
    
    plt.show()
    
def param_plots(clicks, width):
    '''
    takes the list of click locations and square_width and plots the B12, B11, B09, B08, and NBR of the mean value timeserise in a box with side lenght = square_width
    '''
    ax = [ax2,ax3,ax4,ax5,ax6]
    band_names = ['B12', 'B11', 'B09', 'B08', 'NBR']
    b = [[] for i in range(len(band_names))]
    mean = [[] for i in range(len(band_names))]
    std = [[] for i in range(len(band_names))]
    
    time = []
    y = int(clicks[-1][1])
    x = int(clicks[-1][0])
    
    for file in range(len(params)):#loops finding pixel values for each parameter in the square
        for band in range(len(band_names)):
            b[band] = []
        
        date  = datetime.datetime.strptime(filenames[file].split('_')[2].split('T')[0],'%Y%m%d')
        for i in range(y,y+width):
            for j in range(x,x+width):
                for n in range(len(band_names)):
                    b[n] += [params[file][n][i][j]]
                    
        for band in range(len(band_names)):
            mean[band] += [np.nanmean(b[band])]
            std[band] += [np.nanstd(b[band])]        
        time += [date]

    
    for band in range(len(band_names)): #plotting each time serise
        ax[band].plot(time, mean[band], color=f'{plot_colors[len(clicks)-1]}',label=f'Mean at ({x},{y})')
        ax[band].plot(time, list(map(add,mean[band], std[band])), color=f'{plot_colors[len(clicks)-1]}', linestyle='dashed')
        ax[band].plot(time, list(map(sub,mean[band], std[band])), color=f'{plot_colors[len(clicks)-1]}', linestyle='dotted')

        ax[band].legend()
        ax[band].set_title(band_names[band])

    plt.tight_layout()
    plt.show()

def on_click(event):
    '''
    interactive function
    '''
    print(f"Clicked at: {event.xdata}, {event.ydata}")
    if event.inaxes is not None and len(clicks) < 6:  # Check if the click is inside the plot area
        # Store the click coordinates
        clicks.append((event.xdata, event.ydata))
        print(f"Clicked at: {event.xdata}, {event.ydata}")
        
        # Create a square patch
        square = patches.Rectangle((event.xdata, event.ydata), square_width, square_width, 
                                   linewidth=1, edgecolor=f'{plot_colors[len(clicks)-1]}', facecolor='none')
        ax1.add_patch(square)  # Add the square to the plot
        fig.canvas.draw()  # Update the plot
        param_plots(clicks,square_width)
        
def scale(X):
    '''
    Used to scale the image if necesary
    '''
    # default: scale a band to [0, 1]  and then clip
    mymin = np.nanmin(X) # np.nanmin(X))
    mymax = np.nanmax(X) # np.nanmax(X))
    X = (X-mymin) / (mymax - mymin)  # perform the linear transformation

    X[X < 0.] = 0.  # clip
    X[X > 1.] = 1.

    # use histogram trimming / turn it off to see what this step does!
    if  True:
        values = X.ravel().tolist()
        values.sort()
        n_pct = 1. # percent for stretch value
        frac = n_pct / 100.
        lower = int(math.floor(float(len(values))*frac))
        upper = int(math.floor(float(len(values))*(1. - frac)))
        mymin, mymax = values[lower], values[upper]
        X = (X-mymin) / (mymax - mymin)  # perform the linear transformation
    
    return X
