/**
 * M5STACK Button Handling Header
 * T051: Button handling interface definitions
 */

#ifndef BUTTONS_H
#define BUTTONS_H

// Button state structure
struct ButtonState {
    bool isPressed;
    bool wasLongPressed;
    bool wasDoubleClicked;
    unsigned long pressedTime;
    unsigned long lastPressTime;
    bool lastState;
    unsigned long lastDebounceTime;
};

// Global button states
extern ButtonState buttonA;
extern ButtonState buttonB;
extern ButtonState buttonC;

// Function declarations
void initButtons();
void updateButtonStates();
void processButton(ButtonState* button, bool currentState);

// Button state queries
bool isButtonPressed(ButtonState* button);
bool wasButtonClicked(ButtonState* button);
bool wasButtonLongPressed(ButtonState* button);
bool wasButtonDoubleClicked(ButtonState* button);
unsigned long getButtonPressDuration(ButtonState* button);

// Specific button functions
bool isButtonAPressed();
bool isButtonBPressed();
bool isButtonCPressed();

bool wasButtonAClicked();
bool wasButtonBClicked();
bool wasButtonCClicked();

bool wasButtonALongPressed();
bool wasButtonBLongPressed();
bool wasButtonCLongPressed();

bool wasButtonADoubleClicked();
bool wasButtonBDoubleClicked();
bool wasButtonCDoubleClicked();

unsigned long getButtonAPressDuration();
unsigned long getButtonBPressDuration();
unsigned long getButtonCPressDuration();

#endif // BUTTONS_H