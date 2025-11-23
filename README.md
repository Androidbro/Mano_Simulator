Basic Computer Simulator
This folder contains the complete COE 341 Basic Computer Simulator, implemented in Python based on Mano’s Computer System Architecture 
(3rd Edition). It includes all source code components such as the CPU core (simulator/), command-line 
interface (cli/), optional graphical interface (gui/), utility functions (utils/), and the main launcher (main.py). 
The directory also provides the required input files program.txt and data.txt, which contain hexadecimal instructions and optional memory 
initialization data and are automatically loaded when the simulator starts.


Program Execution:

1. Running the program: 
	To run the simulator, you can open the python executable file main.exe (\Mano_Simulator\dist) which presents a menu allowing you 
to choose between the Command Line Interface (CLI) and the optional GUI. You may also launch the CLI directly using python -m cli.interface, or run the GUI with python -m gui.app if it is implemented. 

Running the main.exe file will present you with the following menu:

Mano Basic Computer Simulator
1) CLI mode
2) GUI mode
Q) Quit
Select mode [1/2/Q]:

Select the mode of execution by inputting '1' for CLI Mode and '2' for GUI Mode. Input 'q' or 'Q' to exit the program.

2. CLI Mode:

Selecting this mode assumes that the program is available in hexadecimal instruction format. if 'program.txt' and 'data.txt' are not present in 
'\Mano_Simulator\data' directory, the cli will not show intended behavior.
If the program to be run is written in assembly, Run the assembler.py using python in the directory '\Mano_Simulator\assembler'

Inside the CLI, the following commands are implemented: 

help				/shows the list of commands
next_cycle			/shows the next cycle of the instruction
fast_cycle N			/shows the cycle after N (integer) cycles are executed
next_inst			/shows the next instruction 
fast_inst N			/shows the instruction after N (integer) cycles are executed
run				/runs the whole program
show REG			/shows the value stored in the register REG (replace with AC, IR, etc.)
show mem ADDR [COUNT]		/shows the values of COUNT number of consecutive memoery adresses 
				 starting from memory address ADDR(in hex)
show all			/shows the value of all registers
show profiler			/shows the profiler statistics
exit / quit			/exits the CLI

3. GUI Mode:

GUI provides the functionality to run the assembler. if 'program.txt' and 'data.txt' are not present in 
'\Mano_Simulator\data' directory, the gui will not show intended behavior. Click on 'Import assembly.txt' to assemble the code into program.txt and data.txt.

4.Assembler
If the program to be run is written in assembly, Run the assembler.py using python in the directory '\Mano_Simulator\assembler'
The label section within the assembly code must be followed with a comma for proper functionality.


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
