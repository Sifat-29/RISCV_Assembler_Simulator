import sys

"""
BONUS PART:
MUL-> [1111111][rs2->5 bits][rs1->5 bits][001][rd->5 bits][0110011] (Rtype) done
RST->  00000000000000000000000000000000 (reset all registers to zero) (Unique) done
HALT-> 11111111111111111111111111111111 (Unique) done 
RVRS-> [111111111111][rs1->5 bits][funct3->111][rd->5bits][opcode->1111111] done
"""

# Global variables and dictionaries
# Register values are in integers
registerValues = { "00000" : 0,
                   "00001" : 0,
                   "00010" : 380,
                   "00011" : 0,
                   "00100" : 0,
                   "00101" : 0,
                   "00110" : 0,
                   "00111" : 0,
                   "01000" : 0,
                   "01001" : 0,
                   "01010" : 0,
                   "01011" : 0,
                   "01100" : 0,
                   "01101" : 0,
                   "01110" : 0,
                   "01111" : 0,
                   "10000" : 0,
                   "10001" : 0,
                   "10010" : 0,
                   "10011" : 0,
                   "10100" : 0,
                   "10101" : 0,
                   "10110" : 0,
                   "10111" : 0,
                   "11000" : 0,
                   "11001" : 0,
                   "11010" : 0,
                   "11011" : 0,
                   "11100" : 0,
                   "11101" : 0,
                   "11110" : 0,
                   "11111" : 0}

# Memory keys are in integers and values as well
memoryValues = {(16384+i)*4:0 for i in range(32)}

# Main
def main():
    # Variables
    pc = 0 # Program Counter
    outputFileNameR = sys.argv[3]
    outputFileName = sys.argv[2]
    inputFileName = sys.argv[1]
    # outputFileNameR = r"CO Sim DEV\outputR.txt"
    # outputFileName = r"CO Sim DEV\outputBin.txt"
    # inputFileName = r"CO Sim DEV\input.txt"

    instructionsList = inputTextFile(rf"{inputFileName}")
    outputString = "" # Append output here
    decimalOutputString = ""

    while(True):
        flag = True #for error gen
        #print(f"pc is {pc}")
        registerValues["00000"] = 0
        if pc not in instructionsList.keys():
            flag = False
        else:
            updatedPC, flag = process(instructionsList[pc], pc)
        if flag == False:
            print(f"Error")
            break
        if updatedPC == pc:
            outputString += getCurrentRegisterState(updatedPC)
            decimalOutputString += getCurrentRegisterStateDecimal(updatedPC)
            break
        # Append cuurent instruction output after execution
        outputString += getCurrentRegisterState(updatedPC)
        decimalOutputString += getCurrentRegisterStateDecimal(updatedPC)
        #print(getCurrentRegisterStateDecimal(updatedPC)[:-1])
        pc = updatedPC
        
    simulatorBinHexTest(outputString, rf"{outputFileName}", "b")
    simulatorBinHexTest(decimalOutputString, rf"{outputFileNameR}", "d")
    #print("Success!")

    return


# Functions
def inputTextFile(location):
    instructions = {}
    with open(rf"{location}", "r") as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]

    for i in range(len(lines)):
        instructions[i] = lines[i]

    return instructions


def process(instruction, pc):
    opcode = instruction[-7:] # Opcode->last 7 bits+
    if opcode == "0110011":  # Rtype
        return processRtype(instruction, pc)
    elif opcode == "0100011": # Stype
        return processStype(instruction, pc)
    elif opcode == "1100011":  # Btype
        return processBtype(instruction, pc)
    elif opcode == "1101111":  # Jtype
        return processJtype(instruction, pc)
    elif opcode == "0000011":  # Itype
        return processItypeLW(instruction, pc)
    elif opcode == "0010011":  # Itype
        return processItypeADDI(instruction, pc)
    elif opcode == "1100111":  # Itype
        return processItypeJALR(instruction, pc)
    
    # BONUS
    elif instruction == "00000000000000000000000000000000": #Reset
        return reset(pc)
    elif instruction == "11111111111111111111111111111111": #halt
        return pc , True
    elif opcode == "1111111": #RVRS
        return RVRS(instruction, pc)

    else:
        return pc, False
    
def processRtype(instruction, pc):
    funct7 = instruction[0:7]
    rs2 = instruction[7:12]
    rs1 = instruction[12:17]
    funct3 = instruction[17:20]
    rd = instruction[20:25]

    # Updating register values
    if funct7 == "0000000" and funct3 == "000": # add
        registerValues[rd] = registerValues[rs1] + registerValues[rs2]

    elif funct7 == "0100000" and funct3 == "000": # sub
        registerValues[rd] = registerValues[rs1] - registerValues[rs2]

    elif funct7 == "0000000" and funct3 == "010": # slt
        if registerValues[rs2] > registerValues[rs1]: registerValues[rd] = 1

    elif funct7 == "0000000" and funct3 == "101": # srl
        registerValues[rd] = registerValues[rs1] >> abs(registerValues[rs2])

    elif funct7 == "0000000" and funct3 == "110": # or 
        registerValues[rd] = registerValues[rs1] | registerValues[rs2]

    elif funct7 == "0000000" and funct3 == "111": # and   
        registerValues[rd] = registerValues[rs1] & registerValues[rs2]

    elif funct7 == "1111111" and funct3 == "001": # mul
        registerValues[rd] = registerValues[rs1] * registerValues[rs2]

    else:
        return pc, False

    registerValues["00000"] = 0

    # Returning updated value of PC
    return pc + 1, True # RType: PC = PC + 4

def processStype(instruction, pc):
    imm = instruction[0:7] + instruction[20:25] 
    immValue = binaryToInt(imm)
    rs2 = instruction[7:12]
    rs1 = instruction[12:17]
    funct3 = instruction[17:20]

    # Updating memory
    address = (registerValues[rs1] + immValue)
    if address < 0 or funct3 != "010":
        return pc, False
    memoryValues[address] = registerValues[rs2]

    return pc + 1, True

def processBtype(instruction, pc): # not implemented blt
    imm = instruction[0] + instruction[24] + instruction[1:7] + instruction[20:24]
    immValue = (binaryToInt(imm)//4)*2 # *2
    rs2 = instruction[7:12]
    rs1 = instruction[12:17]
    funct3 = instruction[17:20]
    if funct3 not in {"000","001"}:
        return pc, False

    # Checking for instruction and calculating new PC
    if funct3 == "000" and registerValues[rs1] == registerValues[rs2]: # beq
        pcUpdate = pc + immValue
    elif funct3 == "001" and registerValues[rs1] != registerValues[rs2]: # bne
        pcUpdate = pc + immValue
    else:
        pcUpdate = pc+1

    return pcUpdate, True

def processJtype(instruction, pc):
    imm = instruction[0] + instruction[12:20] + instruction[11]  + instruction[1:11]
    immValue = (binaryToInt(imm)//4)*2
    rd = instruction[20:25]

    # Updating register values
    registerValues[rd] = (pc + 1)*4
    registerValues["00000"] = 0

    # Returning updated value of PC
    return pc + immValue, True # IType immediate opertaion: PC = PC + sext({imm[20:1],1’b0}

def processItypeLW(instruction, pc):
    imm = instruction[0:12]
    immValue = binaryToInt(imm)
    rs1 = instruction[12:17]
    funct3 = instruction[17:20]
    if funct3 != "010":
        return pc, False
    rd = instruction[20:25]

    # Fetching value from memory and putting in register
    address = (registerValues[rs1] + immValue)
    if address < 0:
        return pc, False
    elif address not in memoryValues.keys():
        registerValues[rd] = 0
    else:
        registerValues[rd] = memoryValues[address]
    registerValues["00000"] = 0

    return pc + 1, True

def processItypeADDI(instruction, pc):
    imm = instruction[0:12]
    immValue = binaryToInt(imm)
    rs1 = instruction[12:17]
    funct3 = instruction[17:20]
    if funct3 != "000":
        return pc, False
    rd = instruction[20:25]

    # Updating register values
    registerValues[rd] = registerValues[rs1] + immValue
    registerValues["00000"] = 0

    # Returning updated value of PC
    return pc + 1, True # IType immediate opertaion: PC = PC + sext({imm[20:1],1’b0}

def processItypeJALR(instruction, pc):
    imm = instruction[0:12]
    immValue = binaryToInt(imm)
    rs1 = instruction[12:17]
    funct3 = instruction[17:20]
    if funct3 != "000":
        return pc, False
    rd = instruction[20:25]

    # Updating register values
    registerValues[rd] = (pc + 1)*4
    registerValues["00000"] = 0

    # Returning updated value of PC
    return (registerValues[rs1] + immValue)//4, True

#Bonus
def reset(pc):
    for key in list(registerValues.keys()):
        registerValues[key] = 0
    registerValues["00010"] = 380 # stack pointer

    return pc + 1, True

def RVRS(instruction, pc):
    # imm = instruction[0:12]
    # immValue = binaryToInt(imm)
    rs1 = instruction[12:17]
    funct3 = instruction[17:20]
    if funct3 != "111":
        return pc, False
    rd = instruction[20:25]
    immValueBinary = intToBinary32Bit(registerValues[rs1])[::-1]

    # Updating register values
    registerValues[rd] = binaryToInt(immValueBinary)
    registerValues["00000"] = 0

    # Returning updated value of PC
    return pc + 1, True # IType immediate opertaion: PC = PC + sext({imm[20:1],1’b0}

    
# Helper functions
def abs(x):
    if x < 0: return -x
    return x

def binaryToInt(x): # x is a string
    if x[0] == "0":
        return binaryStringToInt(x)
    else:
        s = ""
        for char in x:
            s += "1" if char == "0" else "0"
        return (-1)*(binaryToInt(s) + 1) 

def binaryStringToInt(x):
    s = 0
    power = 0
    for char in x[::-1]:
        s += int(char)*(2**(power))
        power += 1
    return s

def LSB0(x): # x is int, return is 32bit string
    return intToBinary32Bit(x)[:-1] + "0"

def intToBinary32Bit(n): # n is integer, return value is 32 bit binary string (sanchit)
    if n < 0:
        n = 2**32 + n 
    binary = []
    for i in range(32):
        binary.append(str(n % 2)) 
        n //= 2 
    binary.reverse()
    return ''.join(binary)

def binary0b(x):
    return "0b" + x

def formatHex(string):
    if len(string) == 4:
        temp = "000100"
    elif len(string) == 3:
        temp = "0001000"
    return "0x" + temp + string[2:].upper()

def getCurrentRegisterState(pc):
    ns = binary0b(intToBinary32Bit(pc*4))
    for value in list(registerValues.values()):
        ns += " " + binary0b(intToBinary32Bit(value))
    return ns + "\n"

def getCurrentRegisterStateDecimal(pc):
    ns = str(pc*4)
    for value in list(registerValues.values()):
        ns += " " + str(value)
    return ns + "\n"


#Testing Functions
#Write File
def simulatorBinHexTest(string, outputFileName, mode):
    ns = string
    for i in range(32):
        if mode == "b":
            ns += formatHex(hex(i*4)) + ":" + binary0b(intToBinary32Bit(memoryValues[(16384+i)*4])) + "\n"
        elif mode == "d":
            ns += formatHex(hex(i*4)) + ":" + str(memoryValues[(16384+i)*4]) + "\n"

    with open(rf"{outputFileName}", 'w') as f:
        f.write(ns)

if __name__ == "__main__":
    main()