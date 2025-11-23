Basic Computer Simulator
This folder contains the complete COE 341 Basic Computer Simulator, implemented in Python based on Mano’s Computer System Architecture 
(3rd Edition). It includes all source code components such as the CPU core (simulator/), command-line 
interface (cli/), optional graphical interface (gui/), utility functions (utils/), and the main launcher (main.py). 
The directory also provides the required input files program.txt and data.txt, which contain hexadecimal instructions and optional memory 
initialization data and are automatically loaded when the simulator starts.


Program Execution:

1. Preparing the Program (Before Running the Simulator)

You can run the simulator using either hexadecimal program files or assembly code.

A) Running with program.txt + data.txt (HEX mode)
	1. Open the folder: /Mano_Simulator/data
	2. Edit program.txt to include your hexadecimal instructions.
	3. Edit data.txt to include any initial memory values.
	4. Save the files - they will be automatically loaded when you run the simulator.
	This is the simplest and fastest method if you already have machine code.

B) Running Assembly Code
	1. Open the file: /Mano_Simulator/data/assembly_code.txt
	2. Write your VALID Mano assembly program inside it.
	3. Run the assembler: python assembler/assembler.py
	4. This automatically updates:
		-> program.txt - machine instructions
		-> data.txt - variables / DEC values

After this, the simulator is ready to run with your updated program.


2. Running the simulator:

You can start the simulator in two ways:

A) Option 1 - Using the launcher, by running MANO SIMULATOR.py: python MANO SIMULATOR.py
	This displays:
		Mano Basic Computer Simulator
		1) CLI Mode
		2) GUI Mode
		Q) Quit
		Select mode [1/2/Q]:'''

B) Option 2 - Running Components Directly: 
Run CLI: python -m cli.interface
Run GUI: python -m gui.app

3. CLI Mode:

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


SAMPLE PROGRAMS FOR PROFILER:
1. Proper (Efficient) Code
ORG 100
LDA AL
ADD BL
STA CL
CLA
CIL
ADD AH
ADD BH
STA CH
HLT
AL, DEC 12
AH, DEC 32
BL, DEC 40
BH, DEC 02
CL,DEC 0
CH, DEC 0
END

2. Wasteful (Inefficient) Code
ORG 100

        CLA
        LDA AL
        ADD BL
        STA SUM1

DELAY1, ISZ COUNT1
        BUN DELAY1
        STA TEMP
        LDA TEMP
        ADD ZERO
        STA CL

        CLA
        CIL
        LDA AH
        STA TEMP2
        LDA BH
        ADD TEMP2
        STA SUM2

DELAY2, ISZ COUNT2
        BUN DELAY2
        ADD ZERO
        STA CH

        HLT

ZERO,   DEC 0
SUM1,   DEC 0
SUM2,   DEC 0
TEMP,   DEC 0
TEMP2,  DEC 0
COUNT1, DEC -2
COUNT2, DEC -3

AL,     DEC 12
AH,     DEC 32
BL,     DEC 40
BH,     DEC 2
CL,     DEC 0
CH,     DEC 0
        END


