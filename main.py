# This file is the main entry point of the basic computer simulator. When the user runs "python main.py",
#this file asks whether they want to use the CLI (Command Line Interface) or the GUI (Graphical Interface).

# It then initializes the CPU (BasicComputer), the Profiler, and
# the Formatter, and launches the chosen interface.

# Import the main components of the simulator
from simulator.machine import BasicComputer
from profiler.profiler import Profiler
from utils.formatter import Formatter

from cli.interface import CommandLineInterface

# Try importing the GUI.
# If the GUI folder or app is missing, we disable GUI mode.
try:
    from gui.app import start_gui
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

#Launches the CLI version of the simulator, which allows the user to type commands 
def start_cli_mode(machine, profiler, formatter):
    print("\n CLI mode...\n")
    cli = CommandLineInterface(machine, profiler, formatter)
    cli.start() #reading user comments 

# Launches the GUI version of the simulator.
#If the GUI is not available, the function displays a message rather than crashing. 
    
def start_gui_mode(machine):
    if not GUI_AVAILABLE:
        print("GUI is not available in this project.")
        return
    print("\n GUI mode...\n")
    start_gui(machine)

# Displays a menu that asks the user which mode they want to use.
#Then initializes the CPU , the profiler, and the formatter.
#It then lanuches the selected mode 
def main():
    print(" BASIC COMPUTER SIMULATOR")
    print("Choose mode:")
    print("1. Command Line Interface (CLI)")
    print("2. Graphical User Interface (GUI)")
    print("3. Exit\n")

    choice = input("> ").strip()

 # Create the core components of the simulator.
    # These objects are used by both CLI and GUI:
    # BasicComputer: simulates registers, memory, micro-ops, instructions
    #  Profiler: counts cycles, CPI, memory reads/writes
    # Formatter: converts numbers to hex/binary strings
    machine = BasicComputer()
    profiler = Profiler(machine)
    formatter = Formatter()
    
 # Launch CLI mode
    if choice == "1":
        start_cli_mode(machine, profiler, formatter)
        
 # Launch GUI mode (if available)
    elif choice == "2":
        start_gui_mode(machine)
        
  # Exit the program
    else:
        print("Exiting.")

# This ensures that main() runs only when this file is executed directly.
if __name__ == "__main__":
    main()


