import os
import tkinter as tk
from tkinter import messagebox
import numpy as np
from PIL import Image, ImageDraw
import pickle
from utils import *
from dense_neural_class import *
import requests
import json

# Function to load the model with absolute path
def load_model(filename):
    # Gets the current directory where the script is being executed
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Constructs the full path of the .pkl file
    filepath = os.path.join(current_dir, filename + '.pkl')
    
    with open(filepath, 'rb') as file:
        model_loaded = pickle.load(file)
    
    return model_loaded

# Load the model when starting the program
model = load_model('model')

def predict(image_vector):
    url = "http://127.0.0.1:8000/predict"
    
    # Flatten the image vector to a 1D list of floats
    payload = {"image_vector": [float(x) for x in image_vector.flatten()]}  
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        result = response.json()
        messagebox.showinfo("Result", f"Digit is {result}")
    else:
        messagebox.showerror("Error", f"Failed to get prediction: {response.text}")

# Drawing application class
class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("My Drawing Canvas 28x28")

        # Canvas settings
        self.canvas_size = 680  # Canvas size in pixels
        self.image_size = 28  # Image size for vectorization
        self.brush_size = 20  # Size of the white brush

        # Canvas for drawing
        self.canvas = tk.Canvas(root, bg="black", width=self.canvas_size, height=self.canvas_size)
        self.canvas.pack()

        # Creation of the image and the object for drawing
        self.image = Image.new("L", (self.image_size, self.image_size), "black")
        self.draw = ImageDraw.Draw(self.image)

        # Action buttons
        self.button_frame = tk.Frame(root)
        self.button_frame.pack()
        
        self.predict_button = tk.Button(self.button_frame, text="  Predict The Digit  ", command=self.predict_image)
        self.predict_button.pack(side="left")

        self.clear_button = tk.Button(self.button_frame, text="  Erase  ", command=self.clear_canvas)
        self.clear_button.pack(side="right")

        # Drawing event
        self.canvas.bind("<B1-Motion>", self.paint)

    def paint(self, event):
        # Draw on the screen and on the image
        x1, y1 = (event.x - self.brush_size), (event.y - self.brush_size)
        x2, y2 = (event.x + self.brush_size), (event.y + self.brush_size)
        
        # Draw on the canvas (screen) with a white brush
        self.canvas.create_oval(x1, y1, x2, y2, fill="yellow", outline="yellow")

        # Draw on the 28x28 image for vectorization
        scaled_x1, scaled_y1 = (x1 * self.image_size // self.canvas_size), (y1 * self.image_size // self.canvas_size)
        scaled_x2, scaled_y2 = (x2 * self.image_size // self.canvas_size), (y2 * self.image_size // self.canvas_size)
        self.draw.ellipse([scaled_x1, scaled_y1, scaled_x2, scaled_y2], fill="yellow")

    def predict_image(self):
        # Convert the image to a vector and normalize the values (0 to 1)
        image_data = np.array(self.image).reshape(1, -1) / 255.0
        predict(image_data)

    def clear_canvas(self):
        # Clears the canvas and creates a new black image
        self.canvas.delete("all")
        self.image = Image.new("L", (self.image_size, self.image_size), "black")
        self.draw = ImageDraw.Draw(self.image)

# Application initialization
root = tk.Tk()
root.tk.call('tk','scaling',4.0)
app = DrawingApp(root)
root.mainloop()
