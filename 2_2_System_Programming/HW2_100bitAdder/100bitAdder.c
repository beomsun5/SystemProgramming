#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct number_100bit{
  uint64_t num1;              // Upper 36bits
  uint64_t num2;              // Lower 64bits
}num_100bit;


// From 25-digit hexadecimal value, get the number with the 100 bits
// by splitting it into the 36-bit sized integer and the 64-bit sized integer.
void make_100b(char* hex100b, num_100bit* num){
  uint64_t* num_64bit = (uint64_t*) num;
  for (int i = 0; i < 25; i++){
    if (i == 9) num_64bit += 1;
    if ((hex100b[i] >= 'A') & (hex100b[i] <= 'F')){
      *num_64bit = *num_64bit * 16 + hex100b[i] - 'A' + 10;
    }
    else if((hex100b[i] >= 'a') & (hex100b[i] <= 'f')){
      *num_64bit = *num_64bit * 16 + hex100b[i] - 'a' + 10;
    }
    else if((hex100b[i] >= '0') & (hex100b[i] <= '9')){
      *num_64bit = *num_64bit * 16 + hex100b[i] - '0';
    }
  }
}

// 'Add' Function for two 100-bit value
num_100bit* add_100b(num_100bit* op1, num_100bit* op2){
  int carry = 0;
  num_100bit* result = malloc(sizeof(num_100bit));
  result->num2 = op1->num2 + op2->num2;
  // If there is any overflow while performing the sum of the values,
  // Set the carry into 1
  if ((result->num2 < op1->num2) | (result->num2 < op2->num2)){
    carry = 1;
  }
  result->num1 = op1->num1 + op2->num1 + carry;
  result->num1 = result->num1 & 0x0000000FFFFFFFFF;
  return result;
}

int main(void){
  num_100bit data1;
  num_100bit data2;
  make_100b("FFFFFFFFFFFFFFFFFFFFFFFFF", &data1);
  make_100b("0000000000000000000000001", &data2);
  num_100bit* resultNum = add_100b(&data1, &data2);
  printf("The result of 100bit + 100bit : ");
  printf("0x%09llX%016llX\n", resultNum->num1, resultNum->num2);
  return 0;
}