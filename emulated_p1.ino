// Emulates a P1 energy sensor

int counter = 0;

void setup() {
  Serial.begin(9600);     

}

void loop() {

  counter++;
  
  Serial.println("/ISk5\x02ME382-1004");
  //Serial.println("");
  Serial.println("0-0:96.1.1(XXXXXXXXXXXXXXMYSERIALXXXXXXXXXXXXXX)");
  Serial.println("1-0:1.8.1(00608.400*kWh)");
  Serial.println("1-0:1.8.2(00490.342*kWh)");
  Serial.println("1-0:2.8.1(00000.001*kWh)");
  Serial.print("1-0:2.8.2(");
  Serial.print(counter);
  Serial.println(".000*kWh)");
  
  Serial.println("0-0:96.14.0(0001)");
  Serial.println("1-0:1.7.0(0001.51*kW)");
  Serial.println("1-0:2.7.0(0000.00*kW)");
  Serial.println("0-0:17.0.0(0999.00*kW)");
  Serial.println("0-0:96.3.10(1)");
  Serial.println("0-0:96.13.1()");
  Serial.println("0-0:96.13.0()");
  Serial.println("0-1:24.1.0(3)");
  Serial.println("0-1:96.1.0(3238303131303031323332313337343132)");
  Serial.println("0-1:24.3.0(130810180000)(00)(60)(1)(0-1:24.2.1)(m3)");
  Serial.println("(00947.680)");
  Serial.println("0-1:24.4.0(1)");
  Serial.println("!");
  delay(10000);
}
