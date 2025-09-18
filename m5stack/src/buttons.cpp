/**
 * M5STACK Button Handling Module
 * T051: Advanced button handling with debouncing and long press support
 */

#include "buttons.h"
#include <M5Core2.h>

// Button state tracking
ButtonState buttonA = {false, false, false, 0, 0};
ButtonState buttonB = {false, false, false, 0, 0};
ButtonState buttonC = {false, false, false, 0, 0};

// Configuration
const unsigned long DEBOUNCE_DELAY = 50;  // 50ms debounce
const unsigned long LONG_PRESS_TIME = 1000;  // 1 second for long press
const unsigned long DOUBLE_CLICK_TIME = 400;  // 400ms for double click

// Function implementations
void initButtons() {
    // Initialize button states
    buttonA = {false, false, false, 0, 0};
    buttonB = {false, false, false, 0, 0};
    buttonC = {false, false, false, 0, 0};
}

void updateButtonStates() {
    // Update M5Stack button states
    M5.update();
    
    // Process each button
    processButton(&buttonA, M5.BtnA.isPressed());
    processButton(&buttonB, M5.BtnB.isPressed());
    processButton(&buttonC, M5.BtnC.isPressed());
}

void processButton(ButtonState* button, bool currentState) {
    unsigned long currentTime = millis();
    
    // Debounce check
    if (currentState != button->lastState) {
        button->lastDebounceTime = currentTime;
    }
    
    if ((currentTime - button->lastDebounceTime) > DEBOUNCE_DELAY) {
        // Button state has been stable for debounce period
        bool previousPressed = button->isPressed;
        button->isPressed = currentState;
        
        // Detect press events
        if (button->isPressed && !previousPressed) {
            // Button just pressed
            button->pressedTime = currentTime;
            
            // Check for double click
            if (currentTime - button->lastPressTime < DOUBLE_CLICK_TIME) {
                button->wasDoubleClicked = true;
            } else {
                button->wasDoubleClicked = false;
            }
            
            button->lastPressTime = currentTime;
        }
        
        // Detect release events
        if (!button->isPressed && previousPressed) {
            // Button just released
            unsigned long pressDuration = currentTime - button->pressedTime;
            
            if (pressDuration >= LONG_PRESS_TIME) {
                button->wasLongPressed = true;
            } else {
                button->wasLongPressed = false;
            }
        }
    }
    
    button->lastState = currentState;
}

bool isButtonPressed(ButtonState* button) {
    return button->isPressed;
}

bool wasButtonClicked(ButtonState* button) {
    if (!button->isPressed && button->lastState && !button->wasLongPressed) {
        button->lastState = false;  // Clear the click
        return true;
    }
    return false;
}

bool wasButtonLongPressed(ButtonState* button) {
    if (button->wasLongPressed) {
        button->wasLongPressed = false;  // Clear the flag
        return true;
    }
    return false;
}

bool wasButtonDoubleClicked(ButtonState* button) {
    if (button->wasDoubleClicked) {
        button->wasDoubleClicked = false;  // Clear the flag
        return true;
    }
    return false;
}

// Specific button functions
bool isButtonAPressed() { return isButtonPressed(&buttonA); }
bool isButtonBPressed() { return isButtonPressed(&buttonB); }
bool isButtonCPressed() { return isButtonPressed(&buttonC); }

bool wasButtonAClicked() { return wasButtonClicked(&buttonA); }
bool wasButtonBClicked() { return wasButtonClicked(&buttonB); }
bool wasButtonCClicked() { return wasButtonClicked(&buttonC); }

bool wasButtonALongPressed() { return wasButtonLongPressed(&buttonA); }
bool wasButtonBLongPressed() { return wasButtonLongPressed(&buttonB); }
bool wasButtonCLongPressed() { return wasButtonLongPressed(&buttonC); }

bool wasButtonADoubleClicked() { return wasButtonDoubleClicked(&buttonA); }
bool wasButtonBDoubleClicked() { return wasButtonDoubleClicked(&buttonB); }
bool wasButtonCDoubleClicked() { return wasButtonDoubleClicked(&buttonC); }

// Get button press duration
unsigned long getButtonPressDuration(ButtonState* button) {
    if (button->isPressed) {
        return millis() - button->pressedTime;
    }
    return 0;
}

unsigned long getButtonAPressDuration() { return getButtonPressDuration(&buttonA); }
unsigned long getButtonBPressDuration() { return getButtonPressDuration(&buttonB); }
unsigned long getButtonCPressDuration() { return getButtonPressDuration(&buttonC); }