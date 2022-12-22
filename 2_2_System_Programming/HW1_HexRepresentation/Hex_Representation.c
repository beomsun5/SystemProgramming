#include <stdio.h>

// Showing 0x00~0xff in binary representation
int main(void){
  for (int i = 0; i <= 0xff; i++){
    printf("Current Value : %d\n", i);
    for (int j = 7; j >= 0; j--){
      int temp = i >> j;
      printf("%d", temp & 1);
    }
    printf("\n");
  }
  return 0;
}