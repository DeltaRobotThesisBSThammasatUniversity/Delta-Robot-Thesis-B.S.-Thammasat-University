  //  https://github.com/ivanseidel/DueTimer/blob/master/TimerCounter.md
  //  http://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-11057-32-bit-Cortex-M3-Microcontroller-SAM3X-SAM3A_Datasheet.pdf
  //  https://forum.arduino.cc/t/due-pinout-diagram/129258
#include <Encoder.h>
Encoder EncMotor1(40, 41); //เชื่อมต่อกับ encoder 1 
Encoder EncMotor2(44, 45); //เชื่อมต่อกับ encoder 2 
Encoder EncMotor3(48, 49); //เชื่อมต่อกับ encoder 3

volatile int c;
volatile long count1;
volatile long count2;
volatile long count3;

// long PickCount1;
// long PickCount2;
// long PickCount3;

volatile long EndCount1;
volatile long EndCount2;
volatile long EndCount3;

volatile long PickCount1;
volatile long PickCount2;
volatile long PickCount3;


long countReq1 = 36477;
long countReq2 = 35063;
long countReq3 = 38274;

volatile bool Safety = false;

void TC7_Handler() {
  TC2->TC_CHANNEL[1].TC_SR; //Read and clear status register so that the interrupt handler fires again and again
}
void TC6_Handler() {
  TC2->TC_CHANNEL[0].TC_SR; //Read and clear status register so that the interrupt handler fires again and again
}
void TC8_Handler() {
  TC2->TC_CHANNEL[2].TC_SR; //Read and clear status register so that the interrupt handler fires again and again
}

void setup() {

  Serial.begin(250000);

  pinMode(54, OUTPUT); //Direction for motor 1 [HIGH == ccw],[LOW == cw]
  pinMode(55, OUTPUT); //Direction for motor 2 
  pinMode(56, OUTPUT); //Direction for motor 3

  pinMode(9, OUTPUT);
  digitalWrite(9,LOW);

  pinMode(6, OUTPUT);
  digitalWrite(6,LOW);

  pinMode(7, OUTPUT);
  digitalWrite(7,LOW);



  //Safety switch
  pinMode(30, INPUT_PULLUP); //Switch motor1 บน (sw1u)
  pinMode(31, INPUT_PULLUP); //Switch motor1 ล่าง (sw1d)              
  
  pinMode(34, INPUT_PULLUP); //Switch motor2 บน (sw2u)
  pinMode(35, INPUT_PULLUP); //Switch motor2 ล่าง (sw2d)

  pinMode(38, INPUT_PULLUP); //Switch motor3 บน (sw3u)
  pinMode(39, INPUT_PULLUP); //Switch motor3 ล่าง (sw3d)

  attachInterrupt(digitalPinToInterrupt(30), StopAllSystem, HIGH);
  attachInterrupt(digitalPinToInterrupt(31), StopAllSystem, HIGH);

  attachInterrupt(digitalPinToInterrupt(34), StopAllSystem, HIGH);
  attachInterrupt(digitalPinToInterrupt(35), StopAllSystem, HIGH);

  attachInterrupt(digitalPinToInterrupt(38), StopAllSystem, HIGH);
  attachInterrupt(digitalPinToInterrupt(39), StopAllSystem, HIGH);


  PWM->PWM_DIS = PWM_DIS_CHID0
               | PWM_DIS_CHID1
               | PWM_DIS_CHID2;

  PWM->PWM_SCM = PWM_SCM_SYNC0
               | PWM_SCM_SYNC1
               | PWM_SCM_SYNC2
               | PWM_SCM_UPDM_MODE2;
  //  https://github.com/ivanseidel/DueTimer/blob/master/TimerCounter.md
  //  http://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-11057-32-bit-Cortex-M3-Microcontroller-SAM3X-SAM3A_Datasheet.pdf
  //  https://forum.arduino.cc/t/due-pinout-diagram/129258
  
// PWM motor1 เป็น pin 3 == TIOA7 [1] digital pin 
  PMC->PMC_PCER1 |= PMC_PCER1_PID34; // ?
  PIOC->PIO_PDR |= PIO_PDR_P28; // PIO C - P 28 คือ port pin สำหรับการใช้ interrupt [1] 
  PIOC->PIO_ABSR |= PIO_PC28B_TIOA7; //PC 28 B คือ  I/O Lines และ Peripheral [3] page 858-859
  TC2->TC_CHANNEL[1].TC_CMR = TC_CMR_TCCLKS_TIMER_CLOCK1  // MCK/2
                            | TC_CMR_WAVE               // Waveform mode
                            | TC_CMR_WAVSEL_UP_RC        // UP mode with automatic trigger on RC Compare
                            | TC_CMR_ACPA_CLEAR          // Clear PIN2 on RA compare match
                            | TC_CMR_ACPC_SET;  
  
  // PWM motor2 เป็น pin 5 == TIOA6 [1] digital pin 
  PMC->PMC_PCER1 |= PMC_PCER1_PID33;
  PIOC->PIO_PDR |= PIO_PDR_P25;
  PIOC->PIO_ABSR |= PIO_PC25B_TIOA6;
  TC2->TC_CHANNEL[0].TC_CMR = TC_CMR_TCCLKS_TIMER_CLOCK1 
                            | TC_CMR_WAVE              
                            | TC_CMR_WAVSEL_UP_RC      
                            | TC_CMR_ACPA_CLEAR         
                            | TC_CMR_ACPC_SET;

  
  // PWM motor3 เป็น pin 11 == TIOA8 [1] digital pin 
  PMC->PMC_PCER1 |=PMC_PCER1_PID35;
  PIOD->PIO_PDR |= PIO_PDR_P7;
  PIOD->PIO_ABSR |= PIO_PD7B_TIOA8;
  TC2->TC_CHANNEL[2].TC_CMR = TC_CMR_TCCLKS_TIMER_CLOCK1  
                            | TC_CMR_WAVE               
                            | TC_CMR_WAVSEL_UP_RC        
                            | TC_CMR_ACPA_CLEAR         
                            | TC_CMR_ACPC_SET;

 // Set the priority levels for the interrupts
  // NVIC_SetPriority(TC6_IRQn, 15);
  // NVIC_SetPriority(TC7_IRQn, 15);
  // NVIC_SetPriority(TC8_IRQn, 15);

  NVIC_SetPriority((IRQn_Type)digitalPinToInterrupt(30), 0);
  NVIC_SetPriority((IRQn_Type)digitalPinToInterrupt(31), 0);

  NVIC_SetPriority((IRQn_Type)digitalPinToInterrupt(34), 0);
  NVIC_SetPriority((IRQn_Type)digitalPinToInterrupt(35), 0);

  NVIC_SetPriority((IRQn_Type)digitalPinToInterrupt(38), 0);
  NVIC_SetPriority((IRQn_Type)digitalPinToInterrupt(39), 0);

  // Enable the interrupts for the timer channels
  NVIC_EnableIRQ(TC6_IRQn);
  NVIC_EnableIRQ(TC7_IRQn);
  NVIC_EnableIRQ(TC8_IRQn);

}

void loop(){
  if (Serial.available() > 0){
    int c = Serial.parseInt();
  
  // if (Serial.available()){  // ตรวจสอบว่าที่ช่อง Serial นั้นมีการรับสัญญาณเข้ามาไหม
  //   String command = Serial.readString(); // อ่านค่าที่รับจาก python มาเป็น str
    //Serial.println(command); // print คำสั่งที่รับมาก python ออกมาดู
    // c = command.toInt(); // เปลี่ยนชนิดของคำสั่งเป็น int เพื่อที่จะตรวจสอบเงื่อนไขการเลือกใช้คำสั่ง void
    if (c == 999){
      Reset();
      while(1){
        count1 = EncMotor1.read();
        count2 = EncMotor2.read();
        count3 = EncMotor3.read();
        
        bool conditionZero1 = count1 >= countReq1;
        bool conditionZero2 = count2 >= countReq2;
        bool conditionZero3 = count3 >= countReq3;
    
        if (conditionZero1){
          TC2->TC_CHANNEL[1].TC_RC = 0;
          TC2->TC_CHANNEL[1].TC_RA = (0.5)*(42000000/20000);
          TC2->TC_CHANNEL[1].TC_IER = TC_IER_CPCS | TC_IER_CPAS;
          TC2->TC_CHANNEL[1].TC_CCR = TC_CCR_SWTRG | TC_CCR_CLKEN;
          conditionZero1 = true;
        }
        if (conditionZero2){
          TC2->TC_CHANNEL[0].TC_RC = 0;
          TC2->TC_CHANNEL[0].TC_RA = (0.5)*(42000000/20000);
          TC2->TC_CHANNEL[0].TC_IER = TC_IER_CPCS | TC_IER_CPAS;
          TC2->TC_CHANNEL[0].TC_CCR = TC_CCR_SWTRG | TC_CCR_CLKEN;
          conditionZero2 = true;
        }
        if (conditionZero3){
          TC2->TC_CHANNEL[2].TC_RC = 0;
          TC2->TC_CHANNEL[2].TC_RA = (0.5)*(42000000/20000);
          TC2->TC_CHANNEL[2].TC_IER = TC_IER_CPCS | TC_IER_CPAS;
          TC2->TC_CHANNEL[2].TC_CCR = TC_CCR_SWTRG | TC_CCR_CLKEN;
          conditionZero3 = true;
        }
        if (conditionZero1 && conditionZero2 && conditionZero3 ){
          conditionZero1 = false;
          conditionZero2 = false;
          conditionZero3 = false;
          EncMotor1.write(0);
          EncMotor2.write(0);
          EncMotor3.write(0);
          attachInterrupt(digitalPinToInterrupt(30), StopAllMotor, HIGH);
          attachInterrupt(digitalPinToInterrupt(34), StopAllMotor, HIGH);
          attachInterrupt(digitalPinToInterrupt(38), StopAllMotor, HIGH);
          break;
        }
      }
      Serial.println(900);
    }
    if (c == 888){
      Operate();
    }
    if (c == 777 ){
      OperateMulti();

    }
  } 
}

void StopAllMotor(){

    TC2->TC_CHANNEL[1].TC_RC = 0;
    TC2->TC_CHANNEL[1].TC_RA = (0.5)*(42000000/20000);
    TC2->TC_CHANNEL[1].TC_IER = TC_IER_CPCS | TC_IER_CPAS;
    TC2->TC_CHANNEL[1].TC_CCR = TC_CCR_SWTRG | TC_CCR_CLKEN;
  
    TC2->TC_CHANNEL[0].TC_RC = 0;
    TC2->TC_CHANNEL[0].TC_RA = (0.5)*(42000000/20000);
    TC2->TC_CHANNEL[0].TC_IER = TC_IER_CPCS | TC_IER_CPAS;
    TC2->TC_CHANNEL[0].TC_CCR = TC_CCR_SWTRG | TC_CCR_CLKEN;
  
    TC2->TC_CHANNEL[2].TC_RC = 0;
    TC2->TC_CHANNEL[2].TC_RA = (0.5)*(42000000/20000);
    TC2->TC_CHANNEL[2].TC_IER = TC_IER_CPCS | TC_IER_CPAS;
    TC2->TC_CHANNEL[2].TC_CCR = TC_CCR_SWTRG | TC_CCR_CLKEN;
}

void Reset(){
    digitalWrite(54,LOW);
    digitalWrite(55,LOW);
    digitalWrite(56,LOW);

    TC2->TC_CHANNEL[1].TC_RC = 42000000/20000;
    TC2->TC_CHANNEL[1].TC_RA = (0.5)*(42000000/20000);
    TC2->TC_CHANNEL[1].TC_IER = TC_IER_CPCS | TC_IER_CPAS;
    TC2->TC_CHANNEL[1].TC_CCR = TC_CCR_SWTRG | TC_CCR_CLKEN;
    
    TC2->TC_CHANNEL[0].TC_RC = 42000000/20000;
    TC2->TC_CHANNEL[0].TC_RA = (0.5)*(42000000/20000);
    TC2->TC_CHANNEL[0].TC_IER = TC_IER_CPCS | TC_IER_CPAS;
    TC2->TC_CHANNEL[0].TC_CCR = TC_CCR_SWTRG | TC_CCR_CLKEN;
    
    TC2->TC_CHANNEL[2].TC_RC = 42000000/20000;
    TC2->TC_CHANNEL[2].TC_RA = (0.5)*(42000000/20000);
    TC2->TC_CHANNEL[2].TC_IER = TC_IER_CPCS | TC_IER_CPAS;
    TC2->TC_CHANNEL[2].TC_CCR = TC_CCR_SWTRG | TC_CCR_CLKEN;

    attachInterrupt(digitalPinToInterrupt(30), SetZero1, RISING);
    attachInterrupt(digitalPinToInterrupt(34), SetZero2, RISING);
    attachInterrupt(digitalPinToInterrupt(38), SetZero3, RISING);

}

void OperateMulti(){

  Serial.print(EncMotor1.read());
  Serial.print(",");
  Serial.print(EncMotor2.read());
  Serial.print(",");
  Serial.print(EncMotor3.read());
  Serial.print(",");
  Serial.println(777);

  
  float data_mpi[10];
  float data_dpi[10];
  float data_upi[10];
  float data_mpl[10];
  float data_dpl[10];
  float data_upl[10];

  while(1){
    if(Serial.available() >= sizeof(data_mpi) + sizeof(data_dpi) + sizeof(data_upi) ){ //  + sizeof(data_dpl) + sizeof(data_upl)) { // ตรวจสอบว่ามีข้อมูลเข้ามาหรือไม่
      byte data[sizeof(data_mpi) + sizeof(data_dpi) + sizeof(data_upi) ]; // + sizeof(data_mpl) + sizeof(data_dpl) + sizeof(data_upl)]; // ตัวแปร array สำหรับเก็บข้อมูลแบบ binary
      Serial.readBytes((char*) data, sizeof(data)); // อ่านข้อมูลแบบ binary จาก Serial Port
      memcpy(data_mpi, data, sizeof(data_mpi)); // แยกข้อมูล array data_mpi จากข้อมูลแบบ binary
      memcpy(data_dpi, data + sizeof(data_mpi), sizeof(data_dpi)); // แยกข้อมูล array data_dpi จากข้อมูลแบบ binary
      memcpy(data_upi, data + sizeof(data_mpi) + sizeof(data_dpi), sizeof(data_upi));
      

      // memcpy(data_mpl, data + sizeof(data_mpi) + sizeof(data_dpi) + sizeof(data_upi), sizeof(data_mpl));
      // memcpy(data_dpl, data + sizeof(data_mpi) + sizeof(data_dpi) + sizeof(data_upi) + sizeof(data_mpl), sizeof(data_dpl));
      // memcpy(data_upl, data + sizeof(data_mpi) + sizeof(data_dpi) + sizeof(data_upi) + sizeof(data_mpl) + sizeof(data_dpl), sizeof(data_upl));
      break;
    }
  }
  Serial.println(77);
  while(1){
    if(Serial.available() >= sizeof(data_mpl) + sizeof(data_dpl) + sizeof(data_upl) ){ //  + sizeof(data_dpl) + sizeof(data_upl)) { // ตรวจสอบว่ามีข้อมูลเข้ามาหรือไม่
      byte data[sizeof(data_mpl) + sizeof(data_dpl) + sizeof(data_upl) ]; // + sizeof(data_mpl) + sizeof(data_dpl) + sizeof(data_upl)]; // ตัวแปร array สำหรับเก็บข้อมูลแบบ binary
      Serial.readBytes((char*) data, sizeof(data)); // อ่านข้อมูลแบบ binary จาก Serial Port
      memcpy(data_mpl, data, sizeof(data_mpl)); // แยกข้อมูล array data_mpi จากข้อมูลแบบ binary
      memcpy(data_dpl, data + sizeof(data_mpl), sizeof(data_dpl)); // แยกข้อมูล array data_dpi จากข้อมูลแบบ binary
      memcpy(data_upl, data + sizeof(data_mpl) + sizeof(data_dpl), sizeof(data_upl));
      

      // memcpy(data_mpl, data + sizeof(data_mpi) + sizeof(data_dpi) + sizeof(data_upi), sizeof(data_mpl));
      // memcpy(data_dpl, data + sizeof(data_mpi) + sizeof(data_dpi) + sizeof(data_upi) + sizeof(data_mpl), sizeof(data_dpl));
      // memcpy(data_upl, data + sizeof(data_mpi) + sizeof(data_dpi) + sizeof(data_upi) + sizeof(data_mpl) + sizeof(data_dpl), sizeof(data_upl));
      break;
    }
  }
  
    RotateMotor(data_mpi[0] * 1000, data_mpi[1] * 1000, data_mpi[2] * 1000, data_mpi[3], data_mpi[4], data_mpi[5], data_mpi[6] * 1000, data_mpi[7], data_mpi[8], data_mpi[9]);
    StopAllMotor();
    RotateMotor(data_dpi[0] * 1000, data_dpi[1] * 1000, data_dpi[2] * 1000, data_dpi[3], data_dpi[4], data_dpi[5], data_dpi[6] * 1000, data_dpi[7], data_dpi[8], data_dpi[9]);
    StopAllMotor();
    digitalWrite(9,HIGH);
    delay(1000);
    RotateMotor(data_upi[0] * 1000, data_upi[1] * 1000, data_upi[2] * 1000, data_upi[3], data_upi[4], data_upi[5], data_upi[6] * 1000, data_upi[7], data_upi[8], data_upi[9]);
    StopAllMotor();
    RotateMotor(data_mpl[0] * 1000, data_mpl[1] * 1000, data_mpl[2] * 1000, data_mpl[3], data_mpl[4], data_mpl[5], data_mpl[6] * 1000, data_mpl[7], data_mpl[8], data_mpl[9]);
    StopAllMotor();
    RotateMotor(data_dpl[0] * 1000, data_dpl[1] * 1000, data_dpl[2] * 1000, data_dpl[3], data_dpl[4], data_dpl[5], data_dpl[6] * 1000, data_dpl[7], data_dpl[8], data_dpl[9]);
    StopAllMotor();
    digitalWrite(9,LOW);
    delay(10);
    RotateMotor(data_upl[0] * 1000, data_upl[1] * 1000, data_upl[2] * 1000, data_upl[3], data_upl[4], data_upl[5], data_upl[6] * 1000, data_upl[7], data_upl[8], data_upl[9]);
    StopAllMotor();


    Serial.print(EncMotor1.read());
    Serial.print(",");
    Serial.print(EncMotor2.read());
    Serial.print(",");
    Serial.print(EncMotor2.read());
    Serial.print(",");
    Serial.println("700");
    

}

void Operate(){

  Serial.print(EncMotor1.read());
  Serial.print(",");
  Serial.print(EncMotor2.read());
  Serial.print(",");
  Serial.print(EncMotor3.read());
  Serial.print(",");
  Serial.println(888);

  float dataUse[10];
  // int num1;
  // int num2;
  // bool flag = false;
  while(1){
    if(Serial.available() >= sizeof(dataUse)) { // ตรวจสอบว่ามีข้อมูลเข้ามาหรือไม่
      byte data[sizeof(dataUse)]; // ตัวแปร array สำหรับเก็บข้อมูลแบบ binary
      Serial.readBytes((char*) data, sizeof(data)); // อ่านข้อมูลแบบ binary จาก Serial Port
      memcpy(dataUse, data, sizeof(dataUse)); // แยกข้อมูล array data_mpi จากข้อมูลแบบ binary

      break;
      // num1 = sizeof(dataUse) / sizeof(float);
      // num2 = sizeof(dataPlace) / sizeof(float);

      // if (num1 == 10 && num2 == 10){
      //   flag = true;
      //   break;
      // }
    }
  }
  
    RotateMotor(dataUse[0] * 1000, dataUse[1] * 1000, dataUse[2] * 1000, dataUse[3], dataUse[4], dataUse[5], dataUse[6] * 1000, dataUse[7], dataUse[8], dataUse[9]);
    StopAllMotor();
    Serial.print(EncMotor1.read());
    Serial.print(",");
    Serial.print(EncMotor2.read());
    Serial.print(",");
    Serial.print(EncMotor2.read());
    Serial.print(",");
    Serial.println("800");
    

}

void RotateMotor(float frequency1, float frequency2, float frequency3, float count1, float count2, float count3, float time, float dir1, float dir2, float dir3){
  
  float startTime;
  long count1OP;
  long count2OP;
  long count3OP;

  if (dir1 == 1){
    dir1 = HIGH;
  }
  else {
    if (dir1 == 0){
      dir1 = LOW;
    }
  }

  if (dir2 == 1){
    dir2 = HIGH;
  }
  else {
    if (dir2 == 0){
      dir2 = LOW;
    }
  }

  if (dir3 == 1){
    dir3 = HIGH;
  }
  else {
    if (dir3 == 0){
      dir3 = LOW;
    }
  }

  startTime = millis();
  
  digitalWrite(54,dir1);
  digitalWrite(55,dir2);
  digitalWrite(56,dir3);

  TC2->TC_CHANNEL[1].TC_RC = 42000000/frequency1;
  TC2->TC_CHANNEL[1].TC_RA = (0.5)*(42000000/frequency1);
  TC2->TC_CHANNEL[1].TC_IER = TC_IER_CPCS | TC_IER_CPAS;
  TC2->TC_CHANNEL[1].TC_CCR = TC_CCR_SWTRG | TC_CCR_CLKEN;

  TC2->TC_CHANNEL[0].TC_RC = 42000000/frequency2;
  TC2->TC_CHANNEL[0].TC_RA = (0.5)*(42000000/frequency2);
  TC2->TC_CHANNEL[0].TC_IER = TC_IER_CPCS | TC_IER_CPAS;
  TC2->TC_CHANNEL[0].TC_CCR = TC_CCR_SWTRG | TC_CCR_CLKEN;

  TC2->TC_CHANNEL[2].TC_RC = 42000000/frequency3;
  TC2->TC_CHANNEL[2].TC_RA = (0.5)*(42000000/frequency3);
  TC2->TC_CHANNEL[2].TC_IER = TC_IER_CPCS | TC_IER_CPAS;
  TC2->TC_CHANNEL[2].TC_CCR = TC_CCR_SWTRG | TC_CCR_CLKEN;

  while(1){
    if ((millis() - startTime) >= time){
      TC2->TC_CHANNEL[1].TC_RC = 0;
      TC2->TC_CHANNEL[1].TC_RA = (0.5)*(42000000/frequency1);
      TC2->TC_CHANNEL[1].TC_IER = TC_IER_CPCS | TC_IER_CPAS;
      TC2->TC_CHANNEL[1].TC_CCR = TC_CCR_SWTRG | TC_CCR_CLKEN;

      TC2->TC_CHANNEL[0].TC_RC = 0;
      TC2->TC_CHANNEL[0].TC_RA = (0.5)*(42000000/frequency2);
      TC2->TC_CHANNEL[0].TC_IER = TC_IER_CPCS | TC_IER_CPAS;
      TC2->TC_CHANNEL[0].TC_CCR = TC_CCR_SWTRG | TC_CCR_CLKEN;
      
      TC2->TC_CHANNEL[2].TC_RC = 0;
      TC2->TC_CHANNEL[2].TC_RA = (0.5)*(42000000/frequency3);
      TC2->TC_CHANNEL[2].TC_IER = TC_IER_CPCS | TC_IER_CPAS;
      TC2->TC_CHANNEL[2].TC_CCR = TC_CCR_SWTRG | TC_CCR_CLKEN;
      break;
    }
  }
}

void SetZero1(){
  EncMotor1.write(0);
  digitalWrite(54,HIGH);
  TC2->TC_CHANNEL[1].TC_RC = 42000000/20000;
  TC2->TC_CHANNEL[1].TC_RA = (0.5)*(42000000/20000);
  TC2->TC_CHANNEL[1].TC_IER = TC_IER_CPCS | TC_IER_CPAS;
  TC2->TC_CHANNEL[1].TC_CCR = TC_CCR_SWTRG | TC_CCR_CLKEN;

}

void SetZero2(){
  EncMotor2.write(0);
  digitalWrite(55,HIGH);
  TC2->TC_CHANNEL[0].TC_RC = 42000000/20000;
  TC2->TC_CHANNEL[0].TC_RA = (0.5)*(42000000/20000);
  TC2->TC_CHANNEL[0].TC_IER = TC_IER_CPCS | TC_IER_CPAS;
  TC2->TC_CHANNEL[0].TC_CCR = TC_CCR_SWTRG | TC_CCR_CLKEN;
}

void SetZero3(){
  EncMotor3.write(0);
  digitalWrite(56,HIGH);
  TC2->TC_CHANNEL[2].TC_RC = 42000000/20000;
  TC2->TC_CHANNEL[2].TC_RA = (0.5)*(42000000/20000);
  TC2->TC_CHANNEL[2].TC_IER = TC_IER_CPCS | TC_IER_CPAS;
  TC2->TC_CHANNEL[2].TC_CCR = TC_CCR_SWTRG | TC_CCR_CLKEN;

}

void StopAllSystem(){
  
  TC2->TC_CHANNEL[1].TC_RC = 0;
  TC2->TC_CHANNEL[1].TC_RA = (0.5)*(42000000/20000);
  TC2->TC_CHANNEL[1].TC_IER = TC_IER_CPCS | TC_IER_CPAS;
  TC2->TC_CHANNEL[1].TC_CCR = TC_CCR_SWTRG | TC_CCR_CLKEN;
  
  TC2->TC_CHANNEL[0].TC_RC = 0;
  TC2->TC_CHANNEL[0].TC_RA = (0.5)*(42000000/20000);
  TC2->TC_CHANNEL[0].TC_IER = TC_IER_CPCS | TC_IER_CPAS;
  TC2->TC_CHANNEL[0].TC_CCR = TC_CCR_SWTRG | TC_CCR_CLKEN;
  
  TC2->TC_CHANNEL[2].TC_RC = 0;
  TC2->TC_CHANNEL[2].TC_RA = (0.5)*(42000000/20000);
  TC2->TC_CHANNEL[2].TC_IER = TC_IER_CPCS | TC_IER_CPAS;
  TC2->TC_CHANNEL[2].TC_CCR = TC_CCR_SWTRG | TC_CCR_CLKEN;

  TC2->TC_CHANNEL[1].TC_CMR = 0;
  TC2->TC_CHANNEL[0].TC_CMR = 0;
  TC2->TC_CHANNEL[2].TC_CMR = 0;


}




