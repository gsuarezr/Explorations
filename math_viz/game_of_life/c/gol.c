#include <stdio.h>
#include <SDL3/SDL.h>
//#include <SDL3/SDL_video.h>

// This code is inspired by The VLOG of HirschDaniel https://www.youtube.com/watch?v=RD9IJ7LOK7E
// it was ported to SDL3, and upgraded 
Uint32 WHITE=0xfffffff; // White color
Uint32 GREEN=0xFF558285; // GREEN color
int SCREEN_WIDTH= 900;
int SCREEN_HEIGHT =600;
int SQUARE_SIZE=50; //Side length of each cell
int LINE_WIDTH=3;




int draw_grid(SDL_Surface* surface, int columns, int rows){

    for (int i=0; i<rows;i++){
        // I'm drawing rows here having x fixed and y increasing
        SDL_Rect line = (SDL_Rect) {0,i*SQUARE_SIZE,SCREEN_WIDTH,LINE_WIDTH};
        //  A line is a rectangle whose height approaches zero, and I make each 
        // line be the same have the same width as the screen
        SDL_FillSurfaceRect(surface, &line,GREEN);
    }
    for (int i=0; i<columns;i++){
        // I'm drawing columns here having y fixed and x increasing
        SDL_Rect line = (SDL_Rect) {i*SQUARE_SIZE,0,LINE_WIDTH,SCREEN_HEIGHT};
        //  A line is a rectangle whose width approaches zero, and I make each 
        // line be the same have the same heigh as the screen
        SDL_FillSurfaceRect(surface, &line,GREEN);
    }

}
int draw_cel(SDL_Surface* surface,int x_index, int y_index){
    // The minus one is there because we started numbering from zero when
    // creating the grid. This way the index correspond to location with
    // counting starting from 1
    int y_loc = (y_index-1) * SQUARE_SIZE;
    int x_loc = (x_index-1) * SQUARE_SIZE;
    SDL_Rect rect = (SDL_Rect) {x_loc,y_loc,SQUARE_SIZE,SQUARE_SIZE};
    SDL_FillSurfaceRect(surface,&rect,WHITE);
}
int main(){
    printf("Hello Game of life \n");
    SDL_Init(SDL_INIT_VIDEO);
    char* window_tile ="Conway's Game of Life";
    int columns= SCREEN_WIDTH/SQUARE_SIZE;
    int rows = SCREEN_HEIGHT/SQUARE_SIZE;
    SDL_Window* window =SDL_CreateWindow(window_tile,SCREEN_WIDTH,SCREEN_HEIGHT,0);
    SDL_Surface* surface =SDL_GetWindowSurface(window);
    int cell_x=10;
    int cell_y =4;
    draw_cel(surface,cell_x,cell_y);
    draw_grid(surface,columns,rows);
    SDL_UpdateWindowSurface(window);
    SDL_Delay(10000);
}
