#include <stdio.h>
#include <stdlib.h>
#include <time.h>


// Defining the training data

float train[][2]={
{0,0},
{1,2},
{2,4},
{3,6},
{4,8},
};

float rand_float(void){
    // we normalize the random number from rand
    return (float) rand()/ (float) RAND_MAX;
}


//We are going to solve for y=w*x
int main(){
    //initialize the random number generator with the current time
    srand(time(0));
    // we start with a random number 
    float w = rand_float();
    printf("%f\n",w);

    // we check how good the weight is for the data
    return 0;
}