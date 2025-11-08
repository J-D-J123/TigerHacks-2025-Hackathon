#include <SDL2/SDL.h>
#include <SDL2/SDL_ttf.h>
#include <stdio.h>
#include <stdbool.h>

#define WINDOW_WIDTH 800
#define WINDOW_HEIGHT 600
#define BUTTON_WIDTH 300
#define BUTTON_HEIGHT 60

typedef struct {
    SDL_Rect rect;
    const char* text;
    bool hovered;
} Button;

void drawButton(SDL_Renderer* renderer, TTF_Font* font, Button* button, SDL_Color textColor) {
    // Draw button background
    if (button->hovered) {
        SDL_SetRenderDrawColor(renderer, 100, 150, 255, 255);
    } else {
        SDL_SetRenderDrawColor(renderer, 70, 120, 200, 255);
    }
    SDL_RenderFillRect(renderer, &button->rect);
    
    // Draw button border
    SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);
    SDL_RenderDrawRect(renderer, &button->rect);
    
    // Render text
    SDL_Surface* surface = TTF_RenderText_Blended(font, button->text, textColor);
    SDL_Texture* texture = SDL_CreateTextureFromSurface(renderer, surface);
    
    SDL_Rect textRect;
    textRect.w = surface->w;
    textRect.h = surface->h;
    textRect.x = button->rect.x + (button->rect.w - textRect.w) / 2;
    textRect.y = button->rect.y + (button->rect.h - textRect.h) / 2;
    
    SDL_RenderCopy(renderer, texture, NULL, &textRect);
    
    SDL_FreeSurface(surface);
    SDL_DestroyTexture(texture);
}

int main(int argc, char* argv[]) {
    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        printf("SDL could not initialize! SDL_Error: %s\n", SDL_GetError());
        return 1;
    }
    
    if (TTF_Init() < 0) {
        printf("TTF could not initialize! TTF_Error: %s\n", TTF_GetError());
        return 1;
    }
    
    SDL_Window* window = SDL_CreateWindow("Game Menu", 
                                          SDL_WINDOWPOS_CENTERED, 
                                          SDL_WINDOWPOS_CENTERED,
                                          WINDOW_WIDTH, WINDOW_HEIGHT, 
                                          SDL_WINDOW_SHOWN);
    if (!window) {
        printf("Window could not be created! SDL_Error: %s\n", SDL_GetError());
        return 1;
    }
    
    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    TTF_Font* font = TTF_OpenFont("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28);
    TTF_Font* titleFont = TTF_OpenFont("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48);
    
    if (!font || !titleFont) {
        printf("Failed to load font! Using default.\n");
    }
    
    Button buttons[4];
    int startY = 200;
    int spacing = 80;
    
    for (int i = 0; i < 4; i++) {
        buttons[i].rect.x = (WINDOW_WIDTH - BUTTON_WIDTH) / 2;
        buttons[i].rect.y = startY + i * spacing;
        buttons[i].rect.w = BUTTON_WIDTH;
        buttons[i].rect.h = BUTTON_HEIGHT;
        buttons[i].hovered = false;
    }
    
    buttons[0].text = "PLAY";
    buttons[1].text = "OPTIONS";
    buttons[2].text = "CREDITS";
    buttons[3].text = "EXIT";
    
    SDL_Color white = {255, 255, 255, 255};
    bool running = true;
    SDL_Event event;
    
    while (running) {
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                running = false;
            }
            
            if (event.type == SDL_MOUSEMOTION) {
                int mx = event.motion.x;
                int my = event.motion.y;
                
                for (int i = 0; i < 4; i++) {
                    buttons[i].hovered = (mx >= buttons[i].rect.x && 
                                         mx <= buttons[i].rect.x + buttons[i].rect.w &&
                                         my >= buttons[i].rect.y && 
                                         my <= buttons[i].rect.y + buttons[i].rect.h);
                }
            }
            
            if (event.type == SDL_MOUSEBUTTONDOWN) {
                int mx = event.button.x;
                int my = event.button.y;
                
                for (int i = 0; i < 4; i++) {
                    if (mx >= buttons[i].rect.x && mx <= buttons[i].rect.x + buttons[i].rect.w &&
                        my >= buttons[i].rect.y && my <= buttons[i].rect.y + buttons[i].rect.h) {
                        if (i == 0) printf("Play clicked!\n");
                        else if (i == 1) printf("Options clicked!\n");
                        else if (i == 2) printf("Credits clicked!\n");
                        else if (i == 3) running = false;
                    }
                }
            }
        }
        
        // Clear screen with dark background
        SDL_SetRenderDrawColor(renderer, 20, 20, 40, 255);
        SDL_RenderClear(renderer);
        
        // Draw title
        if (titleFont) {
            SDL_Surface* titleSurface = TTF_RenderText_Blended(titleFont, "GAME MENU", white);
            SDL_Texture* titleTexture = SDL_CreateTextureFromSurface(renderer, titleSurface);
            SDL_Rect titleRect = {WINDOW_WIDTH/2 - titleSurface->w/2, 80, titleSurface->w, titleSurface->h};
            SDL_RenderCopy(renderer, titleTexture, NULL, &titleRect);
            SDL_FreeSurface(titleSurface);
            SDL_DestroyTexture(titleTexture);
        }
        
        // Draw buttons
        if (font) {
            for (int i = 0; i < 4; i++) {
                drawButton(renderer, font, &buttons[i], white);
            }
        }
        
        SDL_RenderPresent(renderer);
        SDL_Delay(16);
    }
    
    if (font) TTF_CloseFont(font);
    if (titleFont) TTF_CloseFont(titleFont);
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    TTF_Quit();
    SDL_Quit();
    
    return 0;
}