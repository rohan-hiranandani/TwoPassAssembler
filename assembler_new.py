"""
######################### GLOBAL VARIABLES #########################
"""

OpCode_list = {'CLA': 0, 'LAC': 1, 'SAC': 2, 'ADD': 3, 'SUB': 4, 'BRZ': 5, 'BRN': 6, 'BRP': 7, 'INP': 8, 'DSP': 9,
               'MUL': 10, 'DIV': 11, 'STP': 12}     # List containing info about available OpCodes

Lines = []      # List contains lines of input file after removing comments and blank spaces
Symbol_Table = []       # List to store labels and symbols
Final_Output = []       # List to display final Output

ErrorFlag = False
ErrorList = []
Program_Counter = 0

ErrorFlagP2 = False
ErrorListP2 = []
Program_Counter_Pass2 = 0

"""
######################### HELPER FUNCTIONS #########################
"""


# Check if string holds an integer
def RepresentsInt(Str):
    """
    :param Str: A string
    :return: Whether the inputted string is an integer or not
    """
    try:
        int(Str)
        return True

    except ValueError:
        return False


# Convert OpCode / Data to binary (4 bit & 8 bit)
def BinConversion(line, Val):
    """
    :param line: Argument to be converted to binary
    :param Val: Type of conversion :
                1 -> 8 bit
                2-> 4 bit
    :return: A string b containing the binary equivalent of input line
    """
    l = len(line)
    b = ''

    if Val == 1:
        c = 8 - l

        for i in range(c):
            b += str(0)

        b += line
        return b

    elif Val == 2:
        c = 4 - l

        for i in range(c):
            b += str(0)

        b += line
        return b


# Check label Vs. Symbol
def lineCheck(line):
    """
    :param line: A list containing a line of the input file split into elements
    :return: 1 -> If first element is a label
             2 -> If first element is an OpCode symbol
    """
    if line[0][-1] == ':':      # A label would have a ':' after it
        return 1

    else:
        return 2


# Check and convert CLA & STP to machine code
def Check_CLA_STP(line, Y):
    """
    :param line: A list containing a line of the input file split into elements
    :param Y: A string
    :return: False , string containing binary equivalent of program counter and OpCode
             True (if line does not contain 'CLA' or 'STP') , Y (as inputted)
    """
    if line[0] == 'CLA':        # To check 'CLA'
        Y += BinConversion(str(bin(Program_Counter_Pass2))[2:], 1) + ' '    # Convert program counter to 8 bit binary
        Y += BinConversion(str(bin(OpCode_list['CLA']))[2:], 2)     # Convert OpCode to 4 bit binary corresponding to position in OpCode_list
        return False, Y


    elif line[0] == 'STP':      # To check 'STP'
        Y += BinConversion(str(bin(Program_Counter_Pass2))[2:], 1) + ' '    # Convert program counter to 8 bit binary
        Y += BinConversion(str(bin(OpCode_list['STP']))[2:], 2)     # Convert OpCode to 4 bit binary corresponding to position in OpCode_list
        return False, Y

    return True, Y


# Check and convert all other opcodes & corresponding data to machine code
def Check_Pass2(line, X):
    """
    :param line: A list containing a line of the input file split into elements
    :param X: A string
    :return: A string containing binary equivalent of program counter , OpCode , and Argument if no error is flagged
    """
    global ErrorFlagP2
    FoundSym = False

    if line[0] == 'CLA' or line[0] == 'STP':    # To check if 'CLA' and 'STP' have been entered with some arguments, which is invalid
        X = ''
        ErrorFlagP2 = True
        ErrorListP2.append(
            "Line " + BinConversion(str(bin(Program_Counter_Pass2))[2:], 1) + ' : OpCode does not take arguments')

    else:

        if line[0][-1] == ':':
            bX, X = Check_CLA_STP(line[1:], X)

            if bX:      # To check if 'CLA' and 'STP' have been entered with some arguments in front of a label
                ErrorFlagP2 = True
                ErrorListP2.append('Line' + BinConversion(str(bin(Program_Counter_Pass2))[2:],
                                                          1) + ' : Invalid OpCode or extra arguments')

        else:

            try:
                X += BinConversion(str(bin(Program_Counter_Pass2))[2:], 1) + ' '    # Convert program counter to 8 bit binary
                X += BinConversion(str(bin(OpCode_list[line[0]]))[2:], 2) + ' '     # Convert OpCode to 4 bit binary corresponding to position in OpCode_list

                if RepresentsInt(line[1]):
                    X += BinConversion(str(bin(int(line[1])))[2:], 1)       # Convert integer value to 8 bit binary

                else:

                    for sym in Symbol_Table:

                        if sym['name'] == line[1]:
                            X += BinConversion(str(bin(sym['VariableAdd']))[2:], 1)     # Convert symbol address to 8 bit binary
                            FoundSym = True

                    if not FoundSym:    # Flag error if symbol not found in table i.e. symbol had not been declared
                        X = ''
                        ErrorFlagP2 = True
                        ErrorListP2.append("'" + str(line[1]) + "' not found in symbol table")

            except KeyError:    # Flag error if any invalid OpCode is entered
                X = ''
                ErrorFlagP2 = True
                ErrorListP2.append("Line" + BinConversion(str(bin(Program_Counter_Pass2))[2:], 1) + " : Invalid OpCode")

    return X


"""
######################### PASSES #########################
"""


# First Pass
def PassOne(text):  # First Pass
    """
    :param text: A string containing the contents of the input file split into lines at '\n'
    :return: 1 -> if 'STP' found in text
             2 -> if 'STP' not found in text
    """
    global Program_Counter
    STP_found = 0   # To flag the presence of 'STP' in code

    # Remove empty lines
    for i in text:
        if i == '':
            text.remove(i)

    # Remove commented lines
    for j in text:
        if j.startswith('//') or j.startswith(';'):
            text.remove(j)

    for line in text:
        flag = True
        Found = False
        l = line.split(" ")     # Split line of code at ' '<whitespace>

        if len(l) != 0:

            for i in range(len(l)):

                # Remove blank spaces in the line
                if l[i] == ' ':
                    l.remove(i)

                # Remove comments placed at the end of the lines
                if l[i].startswith('//') or l[i].startswith(';'):
                    l = l[:i]
                    break

            # print(l)
            Lines.append(l)     # List to store list of lines after removing unnecessary additions and whitespaces

            if len(l) == 2:     # For instructions like 'ADD 10' , 'SUB I' , 'L1: STP' etc..
                v = lineCheck(l)    # Check label Vs. symbol

                if v == 2:      # If symbol

                    for i in Symbol_Table:      # Check if symbol is already in table

                        if l[1] == i['name']:
                            flag = False

                    if flag:    # If symbol not already present in table then add it
                        Symbol_Table.append({'name': l[1], 'isUsed': True, 'isFound': False, 'VariableAdd': -1})

                if v == 1:
                    Label_name = l[0][:len(l[0]) - 1]

                    for i in Symbol_Table:

                        if i['name'] == Label_name:      # Check if label is already present in table

                            if not i['isFound']:        # if label has not been found yet, now it has
                                i['isFound'] = True
                                i['VariableAdd'] = Program_Counter      # Address of label is value of program counter
                                Found = True

                            else:       # label cannot be already found, that means it has been declared multiple times
                                ErrorFlag = True    #  Flag error on multiple declaration of the same label
                                ErrorList.append('Line ' + str(Program_Counter) + ' : Label cannot be declared again')

                    if not Found:       # Add found label to table
                        Symbol_Table.append(
                            {'name': Label_name, 'isUsed': False, 'isFound': True, 'VariableAdd': Program_Counter})

                    if l[1] == 'STP':
                        STP_found = 1       # 'STP' is necessary to compile code otherwise it is an error

            elif len(l) == 3:       # For instructions with labels like 'L1: DSP B" etc..

                if l[0][-1] == ':':
                    Label_name = l[0][:len(l[0]) - 1]

                    for i in Symbol_Table:

                        if i['name'] == Label_name:     # Check if label is already present in table

                            if not i['isFound']:        # if label has not been found yet, now it has
                                i['isFound'] = True
                                i['VariableAdd'] = Program_Counter      # Address of label is value of program counter
                                Found = True

                            else:       # label cannot be already found, that means it has been declared multiple times
                                ErrorFlag = True    #  Flag error on multiple declaration of the same label
                                ErrorList.append('Line ' + str(Program_Counter) + ' : Label cannot be declared again')

                    if not Found:       # Add found label to table
                        Symbol_Table.append(
                            {'name': Label_name, 'isUsed': False, 'isFound': True, 'VariableAdd': Program_Counter})

                    if l[1] == 'STP':
                        STP_found = 1       # 'STP' is necessary to compile code otherwise it is an error

            elif len(l) == 1:       # For instructions like 'CLA' and 'STP'

                if l[0] == 'CLA':
                    pass

                elif l[0] == 'STP':
                    STP_found = 1       # 'STP' is necessary to compile code otherwise it is an error

                else:
                    ErrorFlag = True    # Flag error if any invalid OpCode is entered
                    ErrorList.append('Line' + str(Program_Counter) + ' : Invalid command')

            else:
                ErrorFlag = True    # Flag error if any invalid OpCode or OpCode with invalid arguments is entered
                ErrorList.append('Line' + str(Program_Counter) + ' : Extra/Invalid arguments')

            Program_Counter += 1    # Increment program counter after parsing one line

    #   Variable address of any argument of the nature of character is the ASCII value of its first element
    for i in Symbol_Table:

        if i['name'].isalpha() and i['isFound'] == False:
            i['isFound'] = True
            i['VariableAdd'] = ord(i['name'][0])

    for i in Symbol_Table:

        if not i['isFound']:
            i['isFound'] = True
            i['VariableAdd'] = Program_Counter
            Program_Counter += 1

    #   Variable address of any argument of nature integer is itself
    for i in Symbol_Table:

        try:
            z = int(i['name'])
            i['VariableAdd'] = z

        except ValueError:
            pass

    return STP_found


# Second Pass
def PassTwo():
    """
    :return: nothing
    """
    global Program_Counter_Pass2
    global ErrorFlagP2

    for l in Lines:
        X = ''

        if len(l) == 1:
            bX, X = Check_CLA_STP(l, X)     # Check if OpCode for a line of len = 1, is one of 'CLA' and 'STP' and store binary values in X

            if bX:      # If bX is true, invalid OpCode has been entered
                ErrorFlagP2 = True      # Flag error for invalid OpCode
                ErrorListP2.append(
                    "Line " + BinConversion(str(bin(Program_Counter_Pass2))[2:], 1) + " : Invalid OpCode")

        elif len(l) == 2:       # Convert into binary values and store in X
            X = Check_Pass2(l, X)

        elif len(l) == 3:       # Convert into binary values and store in X

            if l[0][-1] == ':':
                X = Check_Pass2(l[1:], X)

            else:
                ErrorFlagP2 = True      # Flag error if OpCode with invalid/extra arguments is entered in front of a label
                ErrorListP2.append("Line " + BinConversion(str(bin(Program_Counter_Pass2))[2:],
                                                           1) + " : Invalid OpCode or extra arguments")

        else:
            ErrorFlagP2 = True      # Flag error if more than 12 bit arguments is entered as it is a 12 bit assembler
            ErrorListP2.append(
                "Line" + BinConversion(str(bin(Program_Counter_Pass2))[2:], 1) + " : More than allowed arguments")

        Final_Output.append(X)      # Append binary value of each line into list on each pass
        Program_Counter_Pass2 += 1  # Increment program counter


"""
######################### MAIN CODE #########################
"""

FileName = input("Input file name: ")       # get name of file with assembly code

try:
    Inp_File = open(FileName, 'r')

except NameError:       # Flag error if wrong file name entered
    print("No such file found, try again")

text = Inp_File.read()      # Read file
text = text.split('\n')     # Split at every new line

if PassOne(text) == 0:
    ErrorFlag = True        # Flag error if 'STP' not found in Pass One
    ErrorList.append("Stop command 'STP' not found")

else:
    VariableAdd_Counter = 0

    for i in Symbol_Table:

        if not i['isFound']:
            ErrorFlag = True        # Flag error if a symbol is used but not defined
            ErrorList.append('Error- ' + i['name'] + " symbol address not defined")

        elif not i['isUsed']:
            ErrorFlag = True        # Falg error if a symbol is defined but not used
            ErrorList.append('Error-' + i['name'] + " symbol defined but not used")

        elif i['VariableAdd'] == -1:

            if VariableAdd_Counter == 0:
                VariableAdd_Counter += 1

            elif VariableAdd_Counter >= 1:
                ErrorFlag = True        # Flag error if multiple symbols have not been declared
                ErrorList.append("Error- more than one symbol with variable address missing")

        if i['VariableAdd'] >= 256:
            ErrorFlag = True        # Flag error if argument exceeds 256 bits
            ErrorList.append("Address exceeds memory limit of 256 bits")

Symbol_File = open('SymbolTable.txt', 'w')      # Open file to write Symbol Table
print(Symbol_Table)     # Print symbol table

for i in Symbol_Table:      # Write contents of symbol table into file
    Symbol_File.write(i['name'] + ' ' + str(i['VariableAdd']) + '\n')

Symbol_File.close()     # Close symbol table file

Output_File = open("Output.txt", 'w')       # Open file to write errors
Error_File = open("Errors.txt", 'w')        # Open file to write Final Output

if ErrorFlag:

    for err in ErrorList:
        print(err)      # Print any errors found in pass one
        Error_File.write(err + '\n')    # Write pass one errors in file

else:
    PassTwo()       # Call PassTwo() if no errors in Pass One

    if len(ErrorListP2) > 0:

        for err in ErrorListP2:
            print(err)      # Print any errors found in pass two
            Error_File.write(err + '\n')    # Write pass two errors in file

    else:

        for i in Final_Output:

            if i != '':
                print(i)        # Print final output
                Output_File.write(i + '\n')     # Write final output in file

Error_File.close()      # Close error file
Output_File.close()     # Close Output file
Inp_File.close()        # Close Input file
