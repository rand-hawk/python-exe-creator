import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os


class PyToExeConverter(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Python to EXE Converter")
        self.geometry("600x500")

        # File path text entry
        self.label = tk.Label(self, text="Select Python file (.py):")
        self.label.pack(pady=10)

        self.file_path_entry = tk.Entry(self, width=60)
        self.file_path_entry.pack(pady=10, padx=10)

        # Browse button
        self.browse_button = tk.Button(self, text="Browse", command=self.browse_file)
        self.browse_button.pack(pady=5)

        # Output file name text entry
        self.output_label = tk.Label(self, text="Enter output EXE file name (optional):")
        self.output_label.pack(pady=10)

        self.output_entry = tk.Entry(self, width=60)
        self.output_entry.pack(pady=10, padx=10)

        # Button to create .exe file
        self.create_exe_button = tk.Button(self, text="Create .exe file from .py file", command=self.create_exe)
        self.create_exe_button.pack(pady=20)

        # Status text box
        self.status_text = tk.Text(self, height=15, width=70, state=tk.DISABLED)
        self.status_text.pack(pady=10)

    def browse_file(self):
        # Open file dialog to select a .py file
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)

    def create_exe(self):
        # Get the .py file path from entry
        file_path = self.file_path_entry.get()
        if not file_path.endswith(".py"):
            messagebox.showerror("Error", "Please select a valid Python (.py) file.")
            return

        # Get the output file name from entry
        output_name = self.output_entry.get().strip()
        if not output_name:
            # Use the Python file name if output name is not provided
            output_name = os.path.splitext(os.path.basename(file_path))[0]

        # Run pyinstaller command in a separate thread to avoid freezing the GUI
        threading.Thread(target=self.run_pyinstaller, args=(file_path, output_name), daemon=True).start()

    def run_pyinstaller(self, file_path, output_name):
        try:
            # Prepare the pyinstaller command to run with --onefile, --noconsole options, and hidden imports
            command = (
                f'pyinstaller --onefile --noconsole '
                f'--hidden-import=tkinter '
                f'--hidden-import=PIL '
                f'--hidden-import=PIL._imaging '
                f'--hidden-import=PIL._imagingtk '
                f'--name "{output_name}" "{file_path}"'
            )

            # Clear the status box and start updating status
            self.update_status(f"Starting the conversion process for {file_path}...\n")

            # Use subprocess to capture output and errors
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       stdin=subprocess.PIPE, text=True)

            # Read stdout and stderr line by line
            def read_stream(stream, stream_name):
                for line in iter(stream.readline, ''):
                    if line:
                        self.update_status(f"{stream_name}: {line}")
                stream.close()

            # Start threads to read stdout and stderr
            stdout_thread = threading.Thread(target=read_stream, args=(process.stdout, "stdout"), daemon=True)
            stderr_thread = threading.Thread(target=read_stream, args=(process.stderr, "stderr"), daemon=True)
            stdout_thread.start()
            stderr_thread.start()

            # Wait for the process to complete
            process.wait()
            stdout_thread.join()
            stderr_thread.join()

            if process.returncode == 0:
                self.update_status(f"\nEXE file '{output_name}.exe' created successfully!\n")
                messagebox.showinfo("Success", f"EXE file '{output_name}.exe' created successfully!")
            else:
                self.update_status(f"\nFailed to create EXE file. Return code: {process.returncode}\n")
                messagebox.showerror("Error", "Failed to create EXE file. Check the log for details.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.update_status(f"\nError: {str(e)}\n")

    def update_status(self, message):
        """Update the status text box."""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message)
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    app = PyToExeConverter()
    app.mainloop()
