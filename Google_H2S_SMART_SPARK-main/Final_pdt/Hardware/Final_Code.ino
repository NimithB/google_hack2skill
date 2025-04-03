#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <ESP8266HTTPClient.h>

// WiFi Configuration
const char* ssid = "AI;
const char* password = "123456789";

// Server URL to send data
const char* serverUrl = "http://172.19.193.46:5000/esp-data";

// Setup the WebServer and PWM driver
ESP8266WebServer server(80);
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// Button pin definitions
const int topButtonPin = 10;
const int bottomButtonPin = 0;
const int leftButtonPin = 12;
const int rightButtonPin = 13;
const int centerButtonPin = 14;

// Servo control constants
#define SERVOMIN 150
#define SERVOMAX 600

// Motor Driver SDA and SCL pins
#define MOTOR_DRIVER_SDA  4//d2
#define MOTOR_DRIVER_SCL  5//d1

// Variables for Braille display
String receivedSentence = "";
int currentCharIndex = 0;
int displayCount = 0; // Counter to track how many times the sentence has been displayed

uint16_t angleToPulse(int angle) {
  return map(angle, 0, 180, SERVOMIN, SERVOMAX);
}

// Braille alphabet patterns (A-Z and space)
const uint8_t brailleAlphabet[27][6] = {
  {0, 0, 0, 0, 0, 0}, // Blank state
  {0, 0, 0, 1, 0, 0}, // A
  {0, 0, 0, 1, 1, 0}, // B
  {1, 0, 0, 1, 0, 0}, // C
  {1, 1, 0, 1, 0, 0}, // D
  {0, 1, 0, 1, 0, 0}, // E
  {1, 0, 0, 1, 1, 0}, // F
  {1, 1, 0, 1, 1, 0}, // G
  {0, 1, 0, 1, 1, 0}, // H
  {1, 0, 0, 0, 1, 0}, // I
  {1, 1, 0, 0, 1, 0}, // J
  {0, 0, 0, 1, 0, 1}, // K
  {0, 0, 0, 1, 1, 1}, // L
  {1, 0, 0, 1, 0, 1}, // M
  {1, 1, 0, 1, 0, 1}, // N
  {0, 1, 0, 1, 0, 1}, // O
  {1, 0, 0, 1, 1, 1}, // P
  {1, 1, 0, 1, 1, 1}, // Q
  {0, 1, 0, 1, 1, 1}, // R
  {1, 0, 0, 0, 1, 1}, // S
  {1, 1, 0, 0, 1, 1}, // T
  {0, 0, 1, 1, 0, 1}, // U
  {0, 0, 1, 1, 1, 1}, // V
  {1, 1, 1, 0, 1, 0}, // W
  {1, 0, 1, 0, 0, 1}, // X
  {1, 1, 1, 1, 0, 1}, // Y
  {0, 1, 1, 1, 0, 1}  // Z
};

// Function to display the current character in Braille
void displayBraille(char letter) {
  Serial.print("Displaying letter: ");
  Serial.println(letter);

  uint8_t currentLetterIndex = 0;
  
  if (letter == ' ') {
    currentLetterIndex = 0; // Blank state for space
  } else if (letter >= 'A' && letter <= 'Z') {
    currentLetterIndex = letter - 'A' + 1;
  } else if (letter >= 'a' && letter <= 'z') {
    currentLetterIndex = letter - 'a' + 1;
  } else {
    return; // Ignore invalid characters
  }

  const uint8_t* pattern = brailleAlphabet[currentLetterIndex];
  
  // Update each servo based on Braille pattern
  for (uint8_t channel = 0; channel < 6; channel++) {
    pwm.setPWM(channel, 0, angleToPulse(pattern[channel] == 1 ? 0 : 90));
  }
}

// Function to reset all servos
void resetServos() {
  for (uint8_t channel = 0; channel < 6; channel++) {
    pwm.setPWM(channel, 0, angleToPulse(90));
  }
}

// WiFi connection setup
void connectToWiFi() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  Serial.println(WiFi.localIP());
}

// Handle incoming POST request
void handlePostRequest() {
  if (server.hasArg("plain")) {
    String body = server.arg("plain");
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, body);
    
    if (error) {
      Serial.println("Failed to parse JSON");
      server.send(400, "application/json", "{\"status\":\"error\"}");
      return;
    }

    receivedSentence = doc["text"].as<String>();
    currentCharIndex = 0; // Reset to the first character
    displayCount = 0; // Reset display counter
    Serial.println("Received Sentence: " + receivedSentence);

    if (!receivedSentence.isEmpty()) {
      displayBraille(receivedSentence[currentCharIndex]);
    }
    server.send(200, "application/json", "{\"status\":\"success\"}");
  } else {
    server.send(400, "application/json", "{\"status\":\"error\"}");
  }
}

// Function to send button press data to server
void sendButtonPress(const String& buttonName) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    WiFiClient client;
    http.begin(client, serverUrl);

    // Add HTTP header
    http.addHeader("Content-Type", "application/json");

    // Prepare JSON payload
    String jsonData = "{\"button\":\"" + buttonName + "\"}";
    //Serial.print(F("Sending data to server: "));
    //Serial.println(jsonData);

    // Send POST request
    int httpResponseCode = http.POST(jsonData);

    // Handle response
    if (httpResponseCode > 0) {
      String response = http.getString();
      //Serial.print(F("Response from server: "));
      Serial.println(response);
    } else {
      //Serial.print(F("Error in sending POST request. HTTP code: "));
      Serial.println(httpResponseCode);
    }

    http.end(); // Close the connection
  } else {
    Serial.println(F("WiFi not connected."));
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(topButtonPin, INPUT_PULLUP);
  pinMode(bottomButtonPin, INPUT_PULLUP);
  pinMode(leftButtonPin, INPUT_PULLUP);
  pinMode(rightButtonPin, INPUT_PULLUP);
  pinMode(centerButtonPin, INPUT_PULLUP);

  // Connect to WiFi
  connectToWiFi();

  // Initialize I2C and PWM driver
  Wire.begin(MOTOR_DRIVER_SDA, MOTOR_DRIVER_SCL);
  pwm.begin();
  pwm.setPWMFreq(50);  // Set PWM frequency
  resetServos();  // Reset servos to default position

  // Start HTTP server
  server.on("/send", HTTP_POST, handlePostRequest);
  server.begin();
  Serial.println("HTTP Server Started");
}
void loop() {
  server.handleClient();

  // Button press detection
  if (digitalRead(topButtonPin) == LOW) {
    sendButtonPress("TOP");
    Serial.println("TOP");
    delay(200);  // Debounce delay
  }
  if (digitalRead(bottomButtonPin) == LOW) {
    sendButtonPress("BOTTOM");
    Serial.println("BOTTOM");
    delay(200);
  }
  if (digitalRead(leftButtonPin) == LOW) {
    sendButtonPress("LEFT");
    Serial.println("LEFT");
    delay(200);
  }
  if (digitalRead(rightButtonPin) == LOW) {
    sendButtonPress("RIGHT");
    Serial.println("RIGHT");
    delay(200);
  }
  if (digitalRead(centerButtonPin) == LOW) {
    sendButtonPress("CENTER");
    Serial.println("CENTER");
    delay(200);
  }

  // Display the current character from the received sentence
  static unsigned long lastDisplayTime = 0; // Variable to store the last display time
  const unsigned long displayInterval = 3000; // Interval for displaying each character

  if (!receivedSentence.isEmpty() && displayCount < 3) {
    unsigned long currentMillis = millis(); // Get the current time

    // Check if it's time to display the next character
    if (currentMillis - lastDisplayTime >= displayInterval) {
      displayBraille(receivedSentence[currentCharIndex]);
      lastDisplayTime = currentMillis; // Update the last display time
      currentCharIndex++;
      if (currentCharIndex >= receivedSentence.length()) {
        currentCharIndex = 0;  // Reset to start
        displayCount++;  // Increment the display counter
      }
    }
  }
  if (displayCount >= 3) {
    Serial.println("Resetting to blank state...");
    resetServos();  // Reset servos to the blank state
    receivedSentence = "";  // Clear the received sentence
    displayCount = 0;  // Reset display counter
  }
}