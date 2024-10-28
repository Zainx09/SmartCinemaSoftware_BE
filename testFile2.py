import cv2
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk

class CameraApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        # Initialize camera capture as None (it will be opened later)
        self.cap = None

        # Create a tkinter label to hold the camera feed
        self.label = Label(window)
        self.label.pack()

        # Create a button to start the camera
        self.start_button = Button(window, text="Start Camera", command=self.start_camera)
        self.start_button.pack()

        # Create a button to stop the camera
        self.stop_button = Button(window, text="Stop Camera", command=self.stop_camera)
        self.stop_button.pack()

        # Run the Tkinter event loop
        self.window.mainloop()

    def start_camera(self):
        """ Start the camera and begin video capture """
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)  # Open the front camera (or change the index if needed)
            self.update()

    def stop_camera(self):
        """ Stop the camera and release the resources """
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            self.label.config(image='')  # Clear the displayed image

    def update(self):
        """ Update the video feed """
        if self.cap is not None:
            ret, frame = self.cap.read()

            if ret:
                # Convert the frame from BGR (OpenCV default) to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Convert the frame to a PIL Image
                img = Image.fromarray(frame)

                # Convert the PIL image to an ImageTk object
                imgtk = ImageTk.PhotoImage(image=img)

                # Update the label with the new image
                self.label.imgtk = imgtk
                self.label.configure(image=imgtk)

            # Call this method again after 10ms to keep the video stream going
            self.window.after(10, self.update)

    def __del__(self):
        """ Destructor to ensure the camera is released """
        self.stop_camera()

# Create the main window and run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root, "Tkinter Camera App")