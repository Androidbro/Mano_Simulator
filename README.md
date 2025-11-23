Basic Computer simulator
This folder contains the complete COE 341 Basic Computer Simulator, implemented in Python based on Mano’s Computer System Architecture 
(3rd Edition). It includes all source code components such as the CPU core (simulator/), control logic (control/), command-line 
interface (cli/), optional graphical interface (gui/), profiler (profiler/), utility functions (utils/), and the main launcher (main.py). 
The directory also provides the required input files program.txt and data.txt, which contain hexadecimal instructions and optional memory 
initialization data and are automatically loaded when the simulator starts.


Running the Program: 
To run the simulator, you can execute python main.py, which presents a menu allowing you to choose between the Command Line
Interface (CLI) and the optional GUI. You may also launch the CLI directly using python -m cli.interface, or run the GUI with 
python -m gui.app if it is implemented. Inside the CLI, commands such as next_cycle, fast_cycle N, next_inst, fast_inst N, run, and 
the various show commands enable step-by-step execution and inspection of registers, memory, and micro-operations. The built-in profiler 
reports total cycles, number of executed instructions, CPI, and memory read/write counts, which can be used to evaluate program 
performance.
