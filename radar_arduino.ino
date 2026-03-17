#include <Servo.h>

Servo myServo;

// Pin definitions
const int trigPin = 10;
const int echoPin = 11;
const int servoPin = 9;

void setup() {
  Serial.begin(9600);       // start serial communication with PC
  myServo.attach(servoPin); // attach servo to pin 9
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
  // Sweep left to right (0° to 180°)
  for (int angle = 0; angle <= 180; angle += 2) {
    myServo.write(angle);
    delay(30);                        // wait for servo to reach position
    int dist = measureDistance();
    Serial.print(180 - angle);        // mirror angle (servo is mounted upside down)
    Serial.print(",");
    Serial.println(dist);
  }

  // Sweep right to left (180° to 0°)
  for (int angle = 180; angle >= 0; angle -= 2) {
    myServo.write(angle);
    delay(30);                        // wait for servo to reach position
    int dist = measureDistance();
    Serial.print(180 - angle);        // mirror angle (servo is mounted upside down)
    Serial.print(",");
    Serial.println(dist);
  }
}

int measureDistance() {
  // Send ultrasonic pulse
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Measure how long the echo takes to return
  long duration = pulseIn(echoPin, HIGH);

  // Convert duration to distance in cm (speed of sound = 0.034 cm/us, divide by 2 for round trip)
  int distance = duration * 0.034 / 2;

  return distance;
}
