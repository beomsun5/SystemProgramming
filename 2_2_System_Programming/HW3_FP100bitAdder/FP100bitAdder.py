import sys

class FloatingPoint:
  def __init__(self, inputVal):
    self.inputVal = inputVal
    self.fp_bitList = []
    self.signB = 0
    self.exp = 0
    self.mantisa = 0x0

  def setSignB(self, signB):
    self.signB = signB

  def getSignB(self):
    return self.signB

  def setExp(self, exp):
    self.exp = exp

  def getExp(self):
    return self.exp

  def setMantisa(self, mantisa):
    self.mantisa = mantisa

  def getMantisa(self):
    return self.mantisa

  # Get one hexadecimal number and break it into the 4-digit bits
  def changeToBit(self, value):
    valInDecimal = 0
    if ord('A') <= ord(value) <= ord('F'):
      valInDecimal = ord(value) - ord('A') + 10
    elif ord('a') <= ord(value) <= ord('f'):
      valInDecimal = ord(value) - ord('a') + 10
    elif ord('0') <= ord(value) <= ord('9'):
      valInDecimal = ord(value) - ord('0')
    for i in range(3, -1, -1):
      self.fp_bitList.append(((valInDecimal >> i) % 2))
  
  # Change the given input into the bit representation (1st Step)
  def hexToBin(self):
    for idx in range(len(self.inputVal)):
      self.changeToBit(self.inputVal[idx])
    self.setSignB(self.fp_bitList[0])
    # Initializing exponent
    for i in range(29):
      self.exp = (2 * self.exp) + self.fp_bitList[i+1]
    # Initializing mantisa
    temp = 0
    for i in range(70):
      temp = (2 * temp) + self.fp_bitList[i+30]
    self.mantisa = temp + 0x400000000000000000

  # Add two values (2nd Step)
  def __add__(self, fp):
    return self.getMantisa() + fp.getMantisa()
  def __invert__(self):
    return ~self.getMantisa()
  def __lshift__(self, bMove):
    return self.getMantisa() << bMove
  def __rshift__(self, bMove):
    return self.getMantisa() >> bMove

# Addition Function
def AddFP(f1, f2):
  resultFP = FloatingPoint("0")
  resultMantisa = 0
  '''
  Match exponents of each value
  and store round bit and sticky bit (temporary)
  '''
  rB = 0
  sB = 0
  dif = f1.getExp() - f2.getExp()
  print()
  print("Loading... Please Wait...", end="\n\n")
  if dif > 0: # (f1 exp > f2 exp)
    # Match the exponent
    f2.setExp(f1.getExp())
    # set round bit
    rB = (f2 >> (dif - 1)) & 0x01
    # set sticky bit
    i = dif - 2
    while i >= 0:
      sB = sB | ((f2 >> i) & 0x01)
      i -= 1
    # rShift
    f2.setMantisa(f2 >> dif)
  elif dif < 0: # (f1 exp < f2 exp)
    dif = -dif
    f1.setExp(f2.getExp())
    # set round bit
    rB = (f1 >> (dif - 1)) & 0x01
    # set sticky bit
    i = dif - 2
    while i >= 0:
      sB = sB | ((f1 >> i) & 0x01)
      i -= 1
    # rShift
    f1.setMantisa(f1 >> dif)
  '''
  FP Addition (P + P)
  '''
  if f1.getSignB() == f2.getSignB():
    resultMantisa = f1 + f2
    resultFP.setSignB(f1.getSignB())
    # Check Overflow
    if resultMantisa >= 0x800000000000000000:
      resultFP.setExp(fp1.getExp() + 1)
      resultFP.setMantisa(resultMantisa & 0x7FFFFFFFFFFFFFFFFF)
    else:
      resultFP.setMantisa(resultMantisa)
      resultFP.setExp(f1.getExp())
  else:
    '''
    FP Subtraction (P + N)
    '''
    pFP = FloatingPoint("0")
    nFP = FloatingPoint("0")
    if f1.getSignB() > f2.getSignB():
      nFP = f1
      pFP = f2
    else:
      nFP = f2
      pFP = f1
    resultFP.setExp(f1.getExp())
    # If absolute value of negative value is bigger than
    # that of positive value
    if nFP.getMantisa() > pFP.getMantisa():
      resultFP.setSignB(1)
      # nFP + (~pFP) -> 'int' + 'FloatingPoint' -> Incompatible
      resultMantisa = nFP.getMantisa() + (~pFP + 1)
      resultMantisa = resultMantisa & 0x7FFFFFFFFFFFFFFFFF
      resultFP.setMantisa(resultMantisa)
    # If absolute value of positive value is bigger than
    # that of negative value
    elif nFP.getMantisa() < pFP.getMantisa():
      resultFP.setSignB(0)
      resultMantisa = (~nFP + 1) + pFP.getMantisa()
      resultMantisa = resultMantisa & 0x7FFFFFFFFFFFFFFFFF
      resultFP.setMantisa(resultMantisa)
    # If the sum of two values is Zero
    elif nFP.getMantisa() == pFP.getMantisa():
      resultFP.setExp(0)
      resultFP.setMantisa(0)
    # After subtraction, carry is discarded
    # (If resultFP exponent value is less than fp1, fp2)
    # (left-shift mantisa until the hidden bit is found)
  if (resultFP.getExp() != 0 and resultFP.getMantisa() != 0):
    countlShamt = 0
    checkBit = (resultMantisa >> (70 - countlShamt)) & 0x01
    while (checkBit != 1):
      countlShamt += 1
      checkBit = (resultMantisa >> (70 - countlShamt)) & 0x01
    resultFP.setExp(resultFP.getExp() - countlShamt)
    resultFP.setMantisa(resultMantisa << countlShamt)
    # Round-To-Even (GRS)
    bg = (resultMantisa & 0x02) >> 1
    g = resultMantisa % 2
    if g == 1:
      if (bg != 0) or (rB != 0) or (sB != 0):
        resultMantisa += 1  
  # Check Exception
  e = checkException(resultFP)
  # Show the result (100 bit)
  showResult(e, resultFP)

def checkException(fp):
  if (fp.getExp() == 0) and (fp.getMantisa() == 0):
    return 0
  elif (fp.getExp() > 0x1FFFFFFF) and (fp.getMantisa() == 0):
    if fp.getSignBit() == 0:
      return 'INF'
    else:
      return '-INF'
  elif (fp.getExp() > 0x1FFFFFFF) and (fp.getMantisa() != 0):
    return 'NaN'
  else:
    return 1

def showResult(e, fp):
  print("Result : ", end="")
  if e == 0:
    for i in range(100):
      print(0, end="")
    print()
    return
  elif (e == 'INF') or (e == '-INF') or (e == 'NaN'):
    print(e)
    return
  elif e == 1:
    print(fp.getSignB(), end="")
    for i in range(29):
      print((fp.getExp() >> (28 - i)) & 0x01, end="")
    for i in range(70):
      print((fp >> (69 - i)) & 0x01, end="")
    print()
    return

while 1:
  fp_in1 = input("Input 1st number (25-digit Hexadecimal number) : ")
  if len(fp_in1) != 25:
    print("Inappropriate value for the input. Please try again.", end='\n\n')
  else:
    break
while 1:
  fp_in2 = input("Input 2nd number (25-digit Hexadecimal number) : ")
  if len(fp_in2) != 25:
    print("Inappropriate value for the input. Please try again.", end='\n\n')
  else:
    break
fp1 = FloatingPoint(fp_in1)
fp1.hexToBin()
fp2 = FloatingPoint(fp_in2)
fp2.hexToBin()
AddFP(fp1, fp2)