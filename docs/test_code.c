#include <stdio.h>
#define MAX 100

// Comentario de una linea
int main(void) {

    /* Comentario
       de varias lineas */

    int number = 10;
    float decimal = 15.65;
    char letter = 'A';

    int result = number + 20;
    result += 5;
    result++;
    result--;

    if (result >= 30 && result != 50) {
        printf("Resultado: %d\n", result);
    } else {
        printf("El resultado es menor\n");
    }

    while (number < MAX) {
        number = number + 1;
    }

    return 0;
}