import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import os
import sys
import json
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
import read_metfile


class SignalLabeler:
    def __init__(self, data_directory, output_directory):
        """
        Initialize the labeler tool.
        
        Parameters:
        -----------
        data_directory : str
            Path to directory containing signal data files
        output_directory : str
            Path to save labeled data information
        """
        self.data_directory = data_directory
        self.output_directory = output_directory
        
        # Create output directory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)
        
        # Get all signal files
        self.signal_files = [f for f in os.listdir(data_directory) ]
        self.current_index = 0
        self.labels = {}
        
        # Load existing labels if available
        self.label_file = os.path.join(output_directory, 'labels.json')
        if os.path.exists(self.label_file):
            with open(self.label_file, 'r') as f:
                self.labels = json.load(f)
                
        # Setup the plot
        self.setup_plot()
        
    def setup_plot(self):
        """Set up the matplotlib figure with buttons and key bindings"""
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 6))
        plt.subplots_adjust(bottom=0.2)


        # Add buttons
        self.btn_yes_ax = plt.axes([0.3, 0.05, 0.15, 0.075])
        self.btn_no_ax = plt.axes([0.5, 0.05, 0.15, 0.075])
        self.btn_prev_ax = plt.axes([0.1, 0.05, 0.15, 0.075])
        self.btn_next_ax = plt.axes([0.7, 0.05, 0.15, 0.075])
        
        self.btn_yes = Button(self.btn_yes_ax, 'YES (Space)')
        self.btn_no = Button(self.btn_no_ax, 'NO (Del)')
        self.btn_prev = Button(self.btn_prev_ax, 'Previous')
        self.btn_next = Button(self.btn_next_ax, 'Next')
        
        self.btn_yes.on_clicked(self.label_yes)
        self.btn_no.on_clicked(self.label_no)
        self.btn_prev.on_clicked(self.previous_signal)
        self.btn_next.on_clicked(self.next_signal)
        
        # Connect key press events
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        
        # Status text
        self.status_text = self.fig.text(0.5, 0.95, '', ha='center')
        
        # Progress text
        self.progress_text = self.fig.text(0.5, 0.01, '', ha='center')
        
    def load_signal(self, file_path):
        with open(file_path, "rb") as f:
            data = read_metfile.MeteorFile(f)
            return (data.amplitude, data.phase)
    
    def display_current_signal(self):
        """Display the current signal in the plot"""
        if not self.signal_files:
            self.status_text.set_text("No signal files found!")
            return
            
        if self.current_index >= len(self.signal_files):
            self.current_index = 0
            
        file_name = self.signal_files[self.current_index]
        file_path = os.path.join(self.data_directory, file_name)
        
        try:
            (amp, phase) = self.load_signal(file_path)
            
            # Clear previous plot
            self.ax1.clear()
            self.ax1.plot(amp)

            self.ax2.clear()
            self.ax2.plot(phase)

#    plt.subplot(2,1,1)
#         plt.plot(amp)
#         # plt.plot(data.amplitude[:n])
#         plt.title("Amplitude")
#         plt.xlabel("Sample number")
#         plt.subplot(2,1,2)
#         plt.title("Phase")
#         plt.plot(arg)
#         # plt.plot(data.phase[:n])
#         plt.xlabel("Sample number")
#         plt.ylabel("Angle (deg)")
#         plt.tight_layout()
#         plt.show()


            # # Plot the signal
            # time = np.arange(len(signal_data))
            # self.ax.plot(time, signal_data)
            
            # # Add title and labels
            # self.ax.set_title(f"Signal: {file_name}")
            # self.ax.set_xlabel("Time")
            # self.ax.set_ylabel("Amplitude")
            
            # Show if this signal has been labeled
            label_status = "Not Labeled"
            if file_name in self.labels:
                label_status = "Underdense" if self.labels[file_name] else "Overdense"
                
            self.status_text.set_text(f"Status: {label_status}")
            
            # Show progress
            labeled_count = len(self.labels)
            total_count = len(self.signal_files)
            self.progress_text.set_text(f"Progress: {labeled_count}/{total_count} ({labeled_count/total_count*100:.1f}%)")
            
            self.fig.canvas.draw_idle()
        
        except Exception as e:
            self.status_text.set_text(f"Error loading signal: {str(e)}")
    
    def save_labels(self):
        """Save labels to the JSON file"""
        with open(self.label_file, 'w') as f:
            json.dump(self.labels, f)
        print(f"Labels saved to {self.label_file}")
        
        # Also export a simple CSV with two columns: filename, is_underdense
        csv_path = os.path.join(self.output_directory, 'labels.csv')
        with open(csv_path, 'w') as f:
            f.write("filename,is_underdense\n")
            for filename, is_underdense in self.labels.items():
                f.write(f"{filename},{1 if is_underdense else 0}\n")
        print(f"Labels also exported to {csv_path}")
    
    def label_yes(self, event=None):
        """Label current signal as underdense (YES)"""
        if not self.signal_files:
            return
            
        file_name = self.signal_files[self.current_index]
        self.labels[file_name] = True
        self.save_labels()
        self.next_signal()
    
    def label_no(self, event=None):
        """Label current signal as overdense (NO)"""
        if not self.signal_files:
            return
            
        file_name = self.signal_files[self.current_index]
        self.labels[file_name] = False
        self.save_labels()
        self.next_signal()
    
    def next_signal(self, event=None):
        """Move to the next signal"""
        self.current_index = (self.current_index + 1) % len(self.signal_files)
        self.display_current_signal()
    
    def previous_signal(self, event=None):
        """Move to the previous signal"""
        self.current_index = (self.current_index - 1) % len(self.signal_files)
        self.display_current_signal()
    
    def on_key(self, event):
        """Handle key press events"""
        if event.key == ' ':  # Spacebar
            self.label_yes()
        elif event.key == 'delete':
            self.label_no()
        elif event.key == 'right':
            self.next_signal()
        elif event.key == 'left':
            self.previous_signal()
    
    def run(self):
        """Run the labeling tool"""
        self.display_current_signal()
        plt.show()
        
        # Save labels when closing
        self.save_labels()
        
        return self.labels


# Example usage
if __name__ == "__main__":
    # Create a root Tkinter window for directory selection dialogs
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Ask for data directory
    print("Please select the directory containing meteoroid signal data files...")
    data_directory = filedialog.askdirectory(initialdir=os.getcwd(), title="Signal Data Directory")
    
    if not data_directory:
        print("No directory selected. Exiting.")
        exit()
    
    # # Ask for output directory
    # print("Please select where to save the labeled data...")
    # output_directory = filedialog.askdirectory(title="Select Output Directory")
    
    # if not output_directory:
    #     print("No output directory selected. Exiting.")
    #     exit()
    
    # Create and run the labeler
    labeler = SignalLabeler(data_directory, os.getcwd())
    labels = labeler.run()
    
    # Print summary
    underdense_count = sum(1 for v in labels.values() if v)
    overdense_count = sum(1 for v in labels.values() if not v)
    total = len(labels)
    
    print(f"\nLabeling Summary:")
    print(f"Total signals labeled: {total}")
    print(f"Underdense signals: {underdense_count} ({underdense_count/total*100:.1f}%)")
    print(f"Overdense signals: {overdense_count} ({overdense_count/total*100:.1f}%)")