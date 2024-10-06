import os
from datetime import datetime, timedelta



def get_unique_dates_and_raw_strings(directory):
    unique_dates = set()  # Use a set to store unique dates
    raw_date_strings = set()  # Use a set to store raw date strings

    # Iterate through files in the specified directory
    for filename in os.listdir(directory):
        # Check if the filename matches the expected pattern
        if filename.startswith("doy") and filename.endswith(".tif"):
            # Extract the year and day of the year
            year_day = filename[3:10]  # YYYYDDD
            
            # Extract year and day of year
            year = int(year_day[:4])  # YYYY
            day_of_year = int(year_day[4:])  # DDD
            
            # Convert to a date
            date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
            unique_dates.add(date.date())  # Add the date to the set
            
            # Add the raw date string (YYYYDDD) to the set
            raw_date_strings.add(year_day)

    # Sort unique dates and create an ordered list of raw date strings
    sorted_unique_dates = sorted(unique_dates)
    ordered_raw_date_strings = [
        f"{date.year}{date.timetuple().tm_yday:03d}"  # Recreate the YYYYDDD format
        for date in sorted_unique_dates
    ]

    return sorted_unique_dates, ordered_raw_date_strings  # Return sorted lists of unique dates and raw date strings


# Specify your directory path here
directory_path = './data/sat_images/2024-10-06_13-49-16/'
unique_dates, raw_date_strings = get_unique_dates_and_raw_strings(directory_path)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import rasterio

# Function to calculate NDVI, GCI, NDWI images
def calculate_indices(date, scale_factor=1.0):
    # NDVI, GCI, NDWI
    with rasterio.open(f'./data/sat_images/2024-10-06_13-49-16/doy{date}_B4.tif') as red_band, \
         rasterio.open(f'./data/sat_images/2024-10-06_13-49-16/doy{date}_B5.tif') as nir_band, \
         rasterio.open(f'./data/sat_images/2024-10-06_13-49-16/doy{date}_B3.tif') as green_band:

        # Read each band and scale
        red = red_band.read(1).astype('float32') * scale_factor
        nir = nir_band.read(1).astype('float32') * scale_factor
        green = green_band.read(1).astype('float32') * scale_factor

        # Calculate NDVI
        ndvi = (nir - red) / (nir + red + 1e-10)  # Added small constant to avoid division by zero
        gci =  (nir / green) - 1  # GCI calculation
        ndwi = (green - nir) / (green + nir + 1e-10)  # Added small constant to avoid division by zero
        
    return ndvi, gci, ndwi

# List of dates to choose from
dates = raw_date_strings  # Modify this list with your actual dates

# Initial date
initial_date = dates[0]
ndvi_image, gci_image, ndwi_image = calculate_indices(initial_date)

# Set up the figure and axes for the plots
fig, axs = plt.subplots(1, 3, figsize=(10, 12), sharex=True)

# Display initial images
ndvi_im = axs[0].imshow(ndvi_image, cmap='RdYlGn', vmin=-1, vmax=1)
axs[0].set_title('NDVI')
fig.colorbar(ndvi_im, ax=axs[0])

gci_im = axs[1].imshow(gci_image, cmap='Blues', vmin=-1, vmax=5)  # Adjust vmin and vmax if necessary
axs[1].set_title('GCI')
fig.colorbar(gci_im, ax=axs[1])

ndwi_im = axs[2].imshow(ndwi_image, cmap='Blues', vmin=-1, vmax=1)
axs[2].set_title('NDWI')
fig.colorbar(ndwi_im, ax=axs[2])

# Slider for selecting the date
ax_slider = plt.axes([0.1, 0.01, 0.8, 0.03])
slider = Slider(ax_slider, 'Date', 0, len(dates) - 1, valinit=0, valstep=1)

# Update function for slider
def update(val):
    index = int(slider.val)
    date = dates[index]
    ndvi_image, gci_image, ndwi_image = calculate_indices(date)

    # Update the imshow images with new data
    ndvi_im.set_data(ndvi_image)
    gci_im.set_data(gci_image)
    ndwi_im.set_data(ndwi_image)

    # Refresh the plots
    fig.canvas.draw_idle()

# Connect the slider to the update function
slider.on_changed(update)

# Show the plot
plt.tight_layout()
plt.show()