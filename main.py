

from simulator.machine import BasicComputer
from profiler.profiler import Profiler
from utils.formatter import Formatter

from cli.interface import CommandLineInterface


try:
    from gui.app import start_gui
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False


def start_cli_mode(machine, profiler, formatter):
    print("\n CLI mode...\n")
    cli = CommandLineInterface(machine, profiler, formatter)
    cli.start()


def start_gui_mode(machine):
    if not GUI_AVAILABLE:
        print("GUI is not available in this project.")
        return
    print("\n GUI mode...\n")
    start_gui(machine)


def main():
    print(" BASIC COMPUTER SIMULATOR")
    print("Choose mode:")
    print("1. Command Line Interface (CLI)")
    print("2. Graphical User Interface (GUI)")
    print("3. Exit\n")

    choice = input("> ").strip()


    machine = BasicComputer()
    profiler = Profiler(machine)
    formatter = Formatter()

    if choice == "1":
        start_cli_mode(machine, profiler, formatter)

    elif choice == "2":
        start_gui_mode(machine)

    else:
        print("Exiting.")


if __name__ == "__main__":
    main()

