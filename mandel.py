import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import RectangleSelector, Button
import time
import tkinter as tk
from tkinter import ttk
from concurrent.futures import ProcessPoolExecutor

# Mandelbrot set parameters
def mandelbrot(c, max_iter):
    z = 0
    for n in range(max_iter):
        if abs(z) > 2:
            return n
        z = z**2 + c
    return max_iter

# Compute a row of the Mandelbrot set (this function is now global)
def compute_row(i, real, imag, max_iter, width):
    row = []
    for j in range(width):
        c = real[j] + 1j * imag[i]
        row.append(mandelbrot(c, max_iter))
    return row

# Generate Mandelbrot set with parallel processing
def generate_mandelbrot(xmin, xmax, ymin, ymax, width, height, max_iter):
    real = np.linspace(xmin, xmax, width)
    imag = np.linspace(ymin, ymax, height)
    
    # Parallelize row computations using ProcessPoolExecutor
    with ProcessPoolExecutor() as executor:
        mandelbrot_set = list(executor.map(compute_row, range(height), [real]*height, [imag]*height, [max_iter]*height, [width]*height))

    return np.array(mandelbrot_set)

# Global variables for zoom management and timing
zoom_params = {'xmin': -2.5, 'xmax': 1, 'ymin': -1.5, 'ymax': 1.5}
original_zoom = zoom_params.copy()  # Save original zoom
zoom_history = [zoom_params.copy()]  # Keep track of zoom steps
timing_history = []  # Store the timing of each step
width, height, max_iter = 800, 800, 100  # Default resolution and iterations

# Function to update plot based on zoom
def update_plot(xmin, xmax, ymin, ymax):
    global zoom_params, timing_history
    zoom_params.update({'xmin': xmin, 'xmax': xmax, 'ymin': ymin, 'ymax': ymax})

    # Measure time for Mandelbrot generation
    start_time = time.time()
    mandelbrot_zoom = generate_mandelbrot(xmin, xmax, ymin, ymax, width, height, max_iter)
    elapsed_time = time.time() - start_time
    timing_history.append(elapsed_time)

    # Calculate average time
    average_time = sum(timing_history) / len(timing_history)

    # Update plot
    ax.clear()
    ax.imshow(mandelbrot_zoom, extent=[xmin, xmax, ymin, ymax], cmap='hot', origin='lower')
    ax.set_title("Interactive Mandelbrot Zoom")
    ax.set_xlabel("Re(c)")
    ax.set_ylabel("Im(c)")

    # Update timing information
    time_text.config(text=f"Last step: {elapsed_time:.2f}s, Average: {average_time:.2f}s")
    canvas.draw()

    # Print to console
    print(f"Last step time: {elapsed_time:.2f}s, Average time: {average_time:.2f}s")

# Callback function for rectangle selector
def onselect(eclick, erelease):
    xmin, xmax = sorted([eclick.xdata, erelease.xdata])
    ymin, ymax = sorted([eclick.ydata, erelease.ydata])
    zoom_history.append(zoom_params.copy())  # Save current zoom before changing
    update_plot(xmin, xmax, ymin, ymax)

# Reset to original zoom
def reset():
    global zoom_params, zoom_history, timing_history
    zoom_params = original_zoom.copy()
    zoom_history = [original_zoom.copy()]  # Clear history
    timing_history = []  # Clear timing history
    update_plot(**original_zoom)

# Go back one zoom step
def zoom_back():
    global zoom_history
    if len(zoom_history) > 1:
        zoom_history.pop()  # Remove current zoom
        previous_zoom = zoom_history[-1]  # Get the last zoom
        update_plot(**previous_zoom)

# Tkinter GUI setup
def run_gui():
    root = tk.Tk()
    root.title("Mandelbrot Set Zoom")

    # Create a matplotlib figure
    fig, ax = plt.subplots(figsize=(10, 10))

    # Initial plot
    mandelbrot_initial = generate_mandelbrot(
        zoom_params['xmin'], zoom_params['xmax'], zoom_params['ymin'], zoom_params['ymax'], width, height, max_iter
    )
    ax.imshow(mandelbrot_initial, extent=[zoom_params['xmin'], zoom_params['xmax'],
                                          zoom_params['ymin'], zoom_params['ymax']], cmap='hot', origin='lower')
    ax.set_title("Interactive Mandelbrot Zoom")
    ax.set_xlabel("Re(c)")
    ax.set_ylabel("Im(c)")

    # Add rectangle selector
    toggle_selector = RectangleSelector(ax, onselect, useblit=True, button=[1], interactive=True)

    # Create a canvas to embed the figure in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Add a Frame for Buttons and Time Info
    frame = tk.Frame(root)
    frame.pack(side=tk.BOTTOM, fill=tk.X)

    # Reset Button
    reset_button = ttk.Button(frame, text="Reset", command=reset)
    reset_button.pack(side=tk.LEFT, padx=5)

    # Zoom Back Button
    zoom_back_button = ttk.Button(frame, text="Back", command=zoom_back)
    zoom_back_button.pack(side=tk.LEFT, padx=5)

    # Add a Label for time information
    time_text = tk.Label(frame, text="Last step: 0.00s, Average: 0.00s")
    time_text.pack(side=tk.LEFT, padx=5)

    # Start Tkinter main loop
    root.mainloop()

if __name__ == '__main__':
    run_gui()
