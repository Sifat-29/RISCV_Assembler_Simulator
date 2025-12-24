import sys

"""
BONUS PART:
MUL-> [1111111][rs2->5 bits][rs1->5 bits][001][rd->5 bits][0110011] (Rtype) done
RST->  00000000000000000000000000000000 (reset all registers to zero) (Unique) done
HALT-> 11111111111111111111111111111111 (Unique) done 
RVRS-> [111111111111][rs1->5 bits][funct3->111][rd->5bits][opcode->1111111] (Itype)
"""

# Dictionary containing all register names and addresses as strings
registerAddress = {"zero" : "00000",
                   "ra" : "00001",
                   "sp" : "00010",
                   "gp" : "00011",
                   "tp" : "00100",
                   "t0" : "00101",
                   "t1" : "00110",
                   "t2" : "00111",
                   "s0" : "01000",
                   "s1" : "01001",
                   "a0" : "01010",
                   "a1" : "01011",
                   "a2" : "01100",
                   "a3" : "01101",
                   "a4" : "01110",
                   "a5" : "01111",
                   "a6" : "10000",
                   "a7" : "10001",
                   "s2" : "10010",
                   "s3" : "10011",
                   "s4" : "10100",
                   "s5" : "10101",
                   "s6" : "10110",
                   "s7" : "10111",
                   "s8" : "11000",
                   "s9" : "11001",
                   "s10" : "11010",
                   "s11" : "11011",
                   "t3" : "11100",
                   "t4" : "11101",
                   "t5" : "11110",
                   "t6" : "11111"}

# Dictionary containing instruction codes as strings
instructions = {"R-Type" : {"add" : {"opcode" : "0110011", 
                                     "funct3" : "000", 
                                     "funct7" : "0000000"},
                            "sub" : {"opcode" : "0110011", 
                                     "funct3" : "000", 
                                     "funct7" : "0100000"},
                            "slt" : {"opcode" : "0110011", 
                                     "funct3" : "010", 
                                     "funct7" : "0000000"},
                            "srl" : {"opcode" : "0110011", 
                                     "funct3" : "101", 
                                     "funct7" : "0000000"},
                            "or" : {"opcode"  : "0110011", 
                                     "funct3" : "110", 
                                     "funct7" : "0000000"},
                            "and" : {"opcode" : "0110011", 
                                     "funct3" : "111", 
                                     "funct7" : "0000000"},
                            "mul" : {"opcode" : "0110011", 
                                     "funct3" : "001", 
                                     "funct7" : "1111111"}
                            },
                "I-Type" : {"addi" : {"opcode" : "0010011", 
                                      "funct3" : "000"},
                            "lw" : {"opcode" : "0000011", 
                                     "funct3" : "010"},
                            "jalr" : {"opcode" : "1100111", 
                                     "funct3" : "000"}
                            },

                "S-Type" : {"sw" : {"opcode" : "0100011", 
                                    "funct3" : "010"}
                           },

                "B-Type" : {"beq" : {"opcode" : "1100011", 
                                    "funct3" : "000"},
                            "bne" : {"opcode" : "1100011", 
                                    "funct3" : "001"},
                            "blt" : {"opcode" : "1100011", 
                                    "funct3" : "100"}
                            },

                "J-Type" : {"jal" : {"opcode" : "1101111"}
                            }
                }

# Main Function
def main():
    inputFile = sys.argv[1]
    outputFile = sys.argv[2]
    inputInstructions, labels = inputTextFile(rf"{inputFile}")
    
    outputString = ""
    pc = 0
    for number, instruction in list(inputInstructions.items()):
        flag = True     # resetting flag for each instruction
        if instruction != -1:
            binary, flag = process(instruction, labels, pc)
            if (flag):
                outputString += binary
            else:
                outputString = f"Error in instruction {number}\n"    
                break
        else:
            outputString = f"Error in instruction {number}\n"
            break
        pc += 4

    if (flag):     
        with open(rf"{outputFile}", "w") as f:
            f.write(outputString[:-1])
    else:
        print(outputString)

#_____________________________________________________________________________________________________
# Functions

# Function to read inputs from txt file
def inputTextFile(location):
    instructions = {}
    labels = {}
    with open(rf"{location}", "r") as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]

    instructionNumber = 1
    for line in lines:
        if line == "halt":
            instructionNumber += 1
            instructions[instructionNumber] = "halt"
        elif line == "rst":
            instructions[instructionNumber] = "rst"
            instructionNumber += 1
        elif line[0:4] == "rvrs":
            instructions[instructionNumber] = [line.split(" ")[0]] + line.split(" ")[1].split(",")
            instructionNumber += 1
        else:
            if len(line.split(":")) == 2:
                labels[line.split(":")[0]] = (instructionNumber-1)*4
                i = line.split(":")[1].strip()
                instructions[instructionNumber] = i.split(" ")[:1] + i.split(" ")[1].split(",")
            elif len(line.split(" ")) > 1:
                instructions[instructionNumber] = line.split(" ")[:1] + line.split(" ")[1].split(",")
            else:
                instructions[instructionNumber] = -1
            instructionNumber += 1

    return instructions, labels

# Funtcion which first identifies type of instruction and then hands it over to specific type function
def process(instruction, labels, pc):
    if instruction == "halt":
        return "11111111111111111111111111111111\n", True
    elif instruction == "rst":
        return "00000000000000000000000000000000\n", True
    elif (instruction[0] in set(instructions["R-Type"].keys())):
        return processRType(instruction, pc)
    elif (instruction[0] in set(instructions["I-Type"].keys())):
        return processIType(instruction, pc)
    elif (instruction[0] in set(instructions["S-Type"].keys())):
        return processSType(instruction, pc)
    elif (instruction[0] in set(instructions["B-Type"].keys())):
        return processBType(instruction, labels, pc)
    elif (instruction[0] in set(instructions["J-Type"].keys())):
        return processJType(instruction, labels, pc)
    elif (instruction[0] == "rvrs"):
        return processRVRS(instruction)
    else:
        return "", False

# Different processes
def processRType(instructionList, pc): # Sifat
    if (len(instructionList) != 4 or instructionList[1] not in set(registerAddress.keys()) or instructionList[2] not in set(registerAddress.keys()) or instructionList[3] not in set(registerAddress.keys())):
        return "", False
    
    instruction = instructionList[0]
    rd = instructionList[1]
    rs1 = instructionList[2]
    rs2 = instructionList[3]
    opcode = instructions["R-Type"][instruction]["opcode"]
    funct3 = instructions["R-Type"][instruction]["funct3"]
    funct7 = instructions["R-Type"][instruction]["funct7"]
    return funct7 + registerAddress[rs2] + registerAddress[rs1] + funct3 + registerAddress[rd] + opcode + "\n", True

def processIType(instructionList, pc): # Saksham
    if len(instructionList) != 3 and len(instructionList) != 4:
        return "", False 
    
    instruction = instructionList[0]
    rd = instructionList[1]
    if len(instructionList) == 3:
        immediate = instructionList[2].split("(")[0]
        rs1 = instructionList[2].split("(")[1][:-1]
    else:
        rs1 = instructionList[2]
        immediate = instructionList[3]

    if (rd not in registerAddress.keys()) or (rs1 not in registerAddress.keys()):
        return "", False
    
    # convert immediate to integer
    try:
        immediate = int(immediate)
    except ValueError:
        return "", False  # invalid immediate value
    
    # immediate range
    if not (-2048 <= immediate <= 2047):
        return "", False

    signedImmediate = format(immediate, f'012b') if immediate>=0 else format((1 << 12) + immediate, f'012b')
    
    return (signedImmediate + registerAddress[rs1] + instructions["I-Type"][instruction]["funct3"] + registerAddress[rd] + instructions["I-Type"][instruction]["opcode"] + "\n",
            True)

def processSType(instructionList, pc): # Yash
    # 4 args in the list
    if len(instructionList) != 3:
        return "", False  
    
    instruction = instructionList[0]
    ra = instructionList[1]  # destination register
    immediate = instructionList[2].split("(")[0]
    sp = instructionList[2].split("(")[1][:-1]  # base register (rs1)

    # check if registers are valid
    if (ra not in registerAddress.keys()) or (sp not in registerAddress.keys()):
        return "", False
    
    # convert immediate to integer
    try:
        immediate = int(immediate)
    except ValueError:
        return "", False  # invalid immediate value
    
    # immediate range
    if not (-2048 <= immediate <= 2047):
        return "", False

    # extract upper 7 bits of immediate (bits 11:5)
    immediate_upper = (immediate >> 5) & 0x7F

    # extract lower 5 bits of immediate (bits 4:0)
    immediate_lower = immediate & 0x1F

    opcode = instructions["S-Type"][instruction]["opcode"]
    funct3 = instructions["S-Type"][instruction]["funct3"]
    

    return (
        format(immediate_upper, '07b') +    # imm[11:5]
        registerAddress[ra] +               # ra
        registerAddress[sp] +               # sp
        funct3 +    
        format(immediate_lower, '05b') +    # imm[4:0]
        opcode +                        
        '\n',  
        True
    )

def processBType(instructionList, labels, pc): # Sanchit
    if (len(instructionList) != 4 or instructionList[1] not in set(registerAddress.keys()) or instructionList[2] not in set(registerAddress.keys())):
        return "", False
    
    instruction = instructionList[0]
    rs1 = instructionList[1]
    rs2 = instructionList[2]
    imm_label = instructionList[3]
    
    # immediate value 
    if imm_label in labels:
        imm = labels[imm_label]  # assuming labels store the immediate value directly
        imm = int((imm-pc)/2)
    else:
        try:
            imm = int(int(imm_label)/2)
        except ValueError:
            return "", False
    
    # immediate to 12-bit binary
    imm_binary = format(imm, '012b') if imm >= 0 else format(imm & 0x1FFF, '012b')

    imm_12 = imm_binary[0]  # imm[12]
    imm_10_5 = imm_binary[-10:-4]  # imm[10:5]
    imm_4_1 = imm_binary[-4:]  # imm[4:1]
    imm_11 = imm_binary[-11]  # imm[11]
    
    imm_12_10_5 = imm_12 + imm_10_5  # imm[12|10:5]
    imm_4_1_11 = imm_4_1 + imm_11  # imm[4:1|11]
    
    opcode = instructions["B-Type"][instruction]["opcode"]
    funct3 = instructions["B-Type"][instruction]["funct3"]
    
    return (  imm_12_10_5 
            + registerAddress[rs2] 
            + registerAddress[rs1] 
            + funct3 
            + imm_4_1_11 
            + opcode
            + "\n", True
    )

def processJType(instructionList, labels, pc): # Yash
    # 3 args in the list
    if len(instructionList) != 3:
        return "", False
    
    # check if register is valid
    if (instructionList[1] not in registerAddress.keys()):
        return "", False


    instruction = instructionList[0]
    ra = instructionList[1]  # destination register
    if (instructionList[2] in labels.keys()):
        immediate = labels[instructionList[2]]
        immediate = int((int(immediate)-pc)/2)

    else:
        immediate = instructionList[2]
        immediate = int((int(immediate))/2)

    # immediate value
    try:
        # value out of range
        if not (-(2)**20 <= immediate <= 2**20-1):
            int("")
    except ValueError:
        return "", False
    
    signedImmediate = format(immediate, f'020b') if immediate>=0 else format((1 << 20) + immediate, f'020b')

    imm_20 = signedImmediate[0]
    imm_10_1 = signedImmediate[-10:]
    imm_11 = signedImmediate[-11]
    imm_19_12 = signedImmediate[-19:-11]

    return (
        imm_20 + imm_10_1 + imm_11 + imm_19_12 + registerAddress[ra]
        + instructions["J-Type"][instruction]["opcode"] + '\n',
        True
    )

def processRVRS(intsructionList):
    
    return (
        "111111111111" + registerAddress[intsructionList[2]] + "111" + registerAddress[intsructionList[1]] + "1111111" + "\n",
        True
    )

if __name__ == "__main__":
    main()