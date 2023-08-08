//const int ledPIN = PB1;  //esto es lo que viene en el ejemplo pero no funciona
const int analogip = PA7;//Initialize the analog input pin
int Val_Potentiometer = 0;    
bool reading = false;
unsigned long buff_mills;
int data_length = 0;
int buffer_out[4000];

// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin PB1 as an output.
  pinMode(PC14, OUTPUT);
  pinMode(analogip, INPUT);
  Serial.begin(1000000);
  Serial3.begin(9600);
  buff_mills = millis();
}

// the loop function runs over and over again forever
void loop() {
  delayMicroseconds(30);
  Val_Potentiometer = (analogRead(analogip)-2000);
    if (reading){
      if ((millis() - buff_mills) > 5){
        Serial.println("read done");
        Serial.println(data_length);      
        reading = false;
        digitalWrite(PC14, LOW);
        Serial3.println("*");
        for (int i = 0; i <= data_length; i++) {
          Serial3.println(buffer_out[i]);
        }
        data_length = 0;
        Serial3.println("#");
        Serial.println("sent");
    } else {
      buffer_out[data_length] = Val_Potentiometer;
      data_length = data_length + 1;
      //read_data
    }
    
  }

  if (Val_Potentiometer > 300 || Val_Potentiometer < -200){
    digitalWrite(PC14, HIGH);
    //Serial.println(Val_Potentiometer);
    buff_mills = millis();
    reading = true;
  }
}
