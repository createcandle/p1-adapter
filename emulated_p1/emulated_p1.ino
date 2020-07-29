// Emulates a P1 energy sensor

int counter = 0;

void setup() {
  Serial.begin(9600);     

}

void loop() {

  counter++;

  Serial.println("/Ene5\\T210-D ESMR5.0");
  Serial.println("");
  Serial.println("1-3:0.2.8(50)");
  Serial.println("0-0:1.0.0(191013204921S)");
  Serial.println("0-0:96.1.1(4530303438303030303131393037363138)");
  Serial.println("1-0:1.8.1(005491.102*kWh)");
  Serial.println("1-0:1.8.2(003602.765*kWh)");
  Serial.println("1-0:2.8.1(003355.937*kWh)");
  Serial.println("1-0:2.8.2(008025.525*kWh)");
  Serial.println("0-0:96.14.0(0001)");
  Serial.println("1-0:1.7.0(02.721*kW)");
  Serial.println("1-0:2.7.0(00.000*kW)");
  Serial.println("0-0:96.7.21(00577)");
  Serial.println("0-0:96.7.9(00010)");
  Serial.println("1-0:99.97.0(3)(0-0:96.7.19)(180508115740S)(0000013974*s)(180403130035S)(0000001)");
  Serial.println("1-0:32.32.0(00005)");
  Serial.println("1-0:52.32.0(00004)");
  Serial.println("1-0:72.32.0(00004)");
  Serial.println("1-0:32.36.0(00000)");
  Serial.println("1-0:52.36.0(00000)");
  Serial.println("1-0:72.36.0(00000)");
  Serial.println("0-0:96.13.0()");
  Serial.println("1-0:32.7.0(232.0*V)");
  Serial.println("1-0:52.7.0(235.0*V)");
  Serial.println("1-0:72.7.0(235.0*V)");
  Serial.println("1-0:31.7.0(008*A)");
  Serial.println("1-0:51.7.0(002*A)");
  Serial.println("1-0:71.7.0(001*A)");
  Serial.println("1-0:21.7.0(01.924*kW)");
  Serial.println("1-0:41.7.0(00.552*kW)");
  Serial.println("1-0:61.7.0(00.244*kW)");
  Serial.println("1-0:22.7.0(00.000*kW)");
  Serial.println("1-0:42.7.0(00.000*kW)");
  Serial.println("1-0:62.7.0(00.000*kW)");
  Serial.println("!521");

  delay(5000);

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
  
  delay(5000);  

}
