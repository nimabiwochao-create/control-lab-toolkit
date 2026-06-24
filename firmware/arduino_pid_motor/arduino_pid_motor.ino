/*
  Arduino PID motor speed loop.

  Hardware assumptions:
  - PWM motor driver input on pin 5
  - Hall or encoder pulse input on pin 2
  - Serial monitor at 115200 baud

  This sketch mirrors the Python simulation structure: sample speed, filter it,
  update the PID controller, write PWM, and stream telemetry.
*/

const byte PWM_PIN = 5;
const byte SENSOR_PIN = 2;

volatile unsigned long pulseCount = 0;

const float TARGET_RPM = 1200.0;
const float SAMPLE_TIME_S = 0.02;
const float PULSES_PER_REV = 20.0;

float kp = 0.0009;
float ki = 0.0020;
float kd = 0.00004;
float integral = 0.0;
float previousError = 0.0;
float filteredRpm = 0.0;

unsigned long previousMicros = 0;
unsigned long previousPulseCount = 0;

void countPulse() {
  pulseCount++;
}

void setup() {
  pinMode(PWM_PIN, OUTPUT);
  pinMode(SENSOR_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(SENSOR_PIN), countPulse, RISING);
  Serial.begin(115200);
  previousMicros = micros();
}

void loop() {
  unsigned long now = micros();
  float elapsed = (now - previousMicros) / 1000000.0;
  if (elapsed < SAMPLE_TIME_S) {
    return;
  }

  noInterrupts();
  unsigned long pulses = pulseCount;
  interrupts();

  unsigned long deltaPulses = pulses - previousPulseCount;
  previousPulseCount = pulses;
  previousMicros = now;

  float rpm = (deltaPulses / PULSES_PER_REV) * (60.0 / elapsed);
  filteredRpm = 0.25 * rpm + 0.75 * filteredRpm;

  float error = TARGET_RPM - filteredRpm;
  float proposedIntegral = integral + error * elapsed;
  float derivative = (error - previousError) / elapsed;
  float command = kp * error + ki * proposedIntegral + kd * derivative;
  command = constrain(command, 0.0, 1.0);

  bool saturatedHigh = command >= 1.0 && error > 0.0;
  bool saturatedLow = command <= 0.0 && error < 0.0;
  if (!saturatedHigh && !saturatedLow) {
    integral = proposedIntegral;
  }
  previousError = error;

  int pwm = round(command * 255.0);
  analogWrite(PWM_PIN, pwm);

  Serial.print("target=");
  Serial.print(TARGET_RPM);
  Serial.print(",rpm=");
  Serial.print(filteredRpm);
  Serial.print(",pwm=");
  Serial.println(pwm);
}

