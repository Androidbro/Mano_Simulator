# cli/interface.py

import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from simulator.machine import Machine
from cli import commands  # <- keep this

def main():
    # ----- build absolute paths to data/ like GUI does -----
    data_dir = os.path.join(ROOT_DIR, "data")
    prog_path = os.path.join(data_dir, "program.txt")
    data_path = os.path.join(data_dir, "data.txt")

    machine = Machine()

    if not os.path.exists(prog_path):
        print(f"[ERROR] program file not found: {prog_path}")
    else:
        machine.load_program_and_data(prog_file=prog_path, data_file=data_path)

    print("Mano Basic Computer Simulator")
    print(f"Program loaded from {prog_path} and {data_path}")
    print("Type 'help' for list of commands.")

    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break

        if not line:
            continue

        parts = line.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in ("exit", "quit"):
            break

        elif cmd == "help":
            print("Commands:")
            print("  next_cycle")
            print("  fast_cycle N")
            print("  next_inst")
            print("  fast_inst N")
            print("  run")
            print("  show REG")
            print("  show mem ADDR [COUNT]")
            print("  show all")
            print("  show profiler")
            print("  exit / quit")

        elif cmd == "next_cycle":
            commands.cmd_next_cycle(machine)

        elif cmd == "fast_cycle":
            if not args:
                print("Usage: fast_cycle N")
            else:
                try:
                    n = int(args[0])
                    commands.cmd_fast_cycle(machine, n)
                except ValueError:
                    print("N must be an integer")

        elif cmd == "next_inst":
            commands.cmd_next_inst(machine)

        elif cmd == "fast_inst":
            if not args:
                print("Usage: fast_inst N")
            else:
                try:
                    n = int(args[0])
                    commands.cmd_fast_inst(machine, n)
                except ValueError:
                    print("N must be an integer")

        elif cmd == "run":
            commands.cmd_run(machine)

        elif cmd == "show":
            commands.cmd_show(machine, args)

        else:
            print("Unknown command. Type 'help' for commands.")


if __name__ == "__main__":
    main()
