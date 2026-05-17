/*
  Copyright (C) 2025 OpenDLV

  OpenDLV IO logger. Version 1.0
  Non-connected version.
*/

#define SECRET_SSID "yourhotspotname"
#define SECRET_PASS "yourhotspotpass"
#define CLOUD_KEY "yourkey"

// GNSS
#include <Arduino_MKRGPS.h>

// IMU
#include <Arduino.h>
#include <Adafruit_BNO08x.h>

// SD card
#include <SPI.h>
#include <SdFat.h>

// WiFi
#include <WiFiNINA.h>
#include <utility/wifi_drv.h>

bool const enableLog = true;
bool const enableDataPush = true;

int const imuResetPin = 6;
Adafruit_BNO08x bno08x(imuResetPin);
sh2_SensorValue_t sensorValue;

int const chipSelect = 4;
SdFat sd;
SdFile file;
bool requestNewFile = false;

char ssid[] = SECRET_SSID;
char pass[] = SECRET_PASS;
int status = WL_IDLE_STATUS;
char server[] = "opendlv.io";
WiFiClient client;

int pingDtSec = 5;
int pingDtSecCount = 0;

void imuSubscribe() {
  if (!bno08x.enableReport(SH2_ACCELEROMETER, 10000)) { // 100 Hz = 10000 us || 80Hz = 12500 us
    Serial.println("Could not enable IMU accelerometer stream.");
  }
  if (!bno08x.enableReport(SH2_GYROSCOPE_CALIBRATED, 50000)) { // 20 Hz
    Serial.println("Could not enable IMU gyroscope stream.");
  }
  if (!bno08x.enableReport(SH2_ROTATION_VECTOR, 100000)) {  // 10 Hz
    Serial.println("Could not enable IMU rotation stream.");
  }
}

void setup() {

  Serial.begin(9600);
  delay(1000);
  Serial.println("Logger starting...");

  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Failed to initialize WiFi module.");
    while (true) {
      delay(10);
    }
  }

  WiFiDrv::pinMode(26, OUTPUT); // RGB LED, red
  WiFiDrv::pinMode(25, OUTPUT); // RGB LED, green
  WiFiDrv::pinMode(27, OUTPUT); // RGB LED, blue

  // Yellow light during setup.
  WiFiDrv::analogWrite(26, 255);
  WiFiDrv::analogWrite(25, 255);
  WiFiDrv::analogWrite(27, 0);

  String fv = WiFi.firmwareVersion();

  Serial.print("Firmware version: ");
  Serial.println(fv);

  if (fv < WIFI_FIRMWARE_LATEST_VERSION) {
    Serial.println("Please upgrade the firmware using the Arduino IDE Tools menu.");
    while (true) {
      delay(10);
    }
  }

  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, pass);
    delay(10000);
  }
  long rssi = WiFi.RSSI();
  Serial.print("Connected. Signal strength (RSSI): ");
  Serial.print(rssi);
  Serial.println(" dBm");

  client.connect(server, 80);

  delay(200);
  if (!sd.begin(chipSelect, SPI_FULL_SPEED)) {
    Serial.println("Failed to initialize SD card.");
    sd.initErrorHalt();
    while (true) {
      delay(10);
    }
  }


  if (enableDataPush) {
    char remoteFiles[256][18];
    int remoteFilesSize[256];
    int remoteFileCount = 0;

    if (client.connect(server, 80)) {
      client.println("GET /" + String(CLOUD_KEY) + "/logs HTTP/1.1");
      client.println("Host: opendlv.io");
      client.println("Connection: close");
      client.println();
    }
    delay(2000);
    {
      char sizeStr[32];
      int i = 0;
      int j = 0;
      while (client.available()) {
        char c = client.read();
        if (i < 17) {
          remoteFiles[j][i] = c;
        } else if (i > 17) {
          sizeStr[i-18] = c;
        }
        if (c == '\n') {
          if (String(remoteFiles[j], 3) == "ts_") {
            remoteFilesSize[j] = String(sizeStr, i-18).toInt();
            j++;
          }
          i = 0;
          continue;
        }
        i++;
      }
      remoteFileCount = j;
    }

    SdFile root;
    SdFile file;
    char fileName[18];
    int const bufferSize = 1024;
    char sendBuffer[bufferSize];
    root.open("/");
    while (file.openNext(&root, O_READ)) {
      file.getName(fileName, sizeof(fileName));
      String fn(fileName);
      if (!file.isDir() && fn.substring(0, 3) == "ts_" && fn.substring(13, 17) == ".log") {

        Serial.print("Local file '");
        Serial.print(fileName);
        Serial.print("' ");

        bool corrupt = false;
        bool skip = false;
        for (int i = 0; i < remoteFileCount; i++) {
          String remoteFile = String(remoteFiles[i], 17);
          int remoteSize = remoteFilesSize[i];
          if (remoteFile == fileName) {
            Serial.print("was found remotely ");
            if (remoteSize == file.fileSize()) {
              Serial.println("with the correct size. Skipping.");
              skip = true;
            } else {
              Serial.println("but with the wrong size. Uploading.");
              corrupt = true;
            }
            break;
          }
        }
        if (skip) {
          continue;
        }
        if (!corrupt) {
          Serial.println("was not found remotely. Uploading.");
        }

        // Green light during setup.
        WiFiDrv::analogWrite(26, 0);
        WiFiDrv::analogWrite(25, 255);
        WiFiDrv::analogWrite(27, 0);

        int p = 0;
        int c = 0;
        int s = 0;
        int offset = 0;
        while (true) {
          s = file.read(sendBuffer, bufferSize);
          if (s < 1) {
            break;
          }
          if (client.connect(server, 80)) {
            client.println("POST /" + String(CLOUD_KEY) + "/log/" + fileName + "?p=" + String(p) + "&c=" + String(c) + "&s=" + String(s) + " HTTP/1.1");
            client.println("Host: opendlv.io");
            client.println("Content-Type: application/octet-stream");
            client.println("Content-Length: " + String(s));
            client.println("Connection: close");
            client.println();
            client.println(String(sendBuffer, s));
          }
          p += s;
          c++;
        }
        Serial.println("done");

        // Yellow light during setup.
        WiFiDrv::analogWrite(26, 255);
        WiFiDrv::analogWrite(25, 255);
        WiFiDrv::analogWrite(27, 0);
      }
      file.close();
    }
    root.close();
  }

  delay(200);
  if (!GPS.begin(GPS_MODE_SHIELD)) {
    Serial.println("Failed to initialize GPS.");
    while (true) {
      delay(10);
    }
  }

  delay(200);
  if (!bno08x.begin_I2C()) {
    Serial.println("Failed to initialize IMU.");
    while (true) {
      delay(10);
    }
  }

  delay(200);
  imuSubscribe();

  Serial.println("Ready! Waiting for data...");
  delay(100);

  // Blue light until logging data.
  WiFiDrv::analogWrite(26, 0);
  WiFiDrv::analogWrite(25, 0);
  WiFiDrv::analogWrite(27, 255);
}

unsigned long tsSecFirst = 0;
unsigned long tsSec = 0;
unsigned long tsUs = 0;

unsigned long syncUs = 0;

bool gotGps = false;
bool gotImu = false;

int imuFloatCount = 0;

byte buffer[2 * 512];
int bufferOffset = 0;

void loop() {
  unsigned long ts = 0;

  while (client.read() != -1);

  if (enableLog && GPS.available()) {

    syncUs = micros();

    tsSec = GPS.getTime();
    tsUs = 0; // The Arduino_MKRGPS library is missing GPS.getTimeUs(), but samples always seem to arrive at us=0.

    byte const id = 0;
    float latitude = GPS.latitude();
    float longitude = GPS.longitude();
    float altitude = GPS.altitude();
    float speed = GPS.speed();
    byte satellites = GPS.satellites();
    memcpy(&buffer[bufferOffset + 0], &id, 1);
    memcpy(&buffer[bufferOffset + 1], &tsSec, 4);
    memcpy(&buffer[bufferOffset + 5], &latitude, 4);
    memcpy(&buffer[bufferOffset + 9], &longitude, 4);
    memcpy(&buffer[bufferOffset + 13], &altitude, 4);
    memcpy(&buffer[bufferOffset + 17], &speed, 4);
    memcpy(&buffer[bufferOffset + 21], &satellites, 1);
    bufferOffset += 22;

    if (tsSecFirst == 0) {
      tsSecFirst = tsSec;
    }

    if (!file || requestNewFile) {
      if (file) {
        file.close();
      }
      String p1 = "ts_";
      String p2 = ".log";
      String name = p1 + tsSec + p2;
      file.open(name.c_str(), O_WRITE | O_CREAT | O_EXCL);

      Serial.print("Created file ");
      Serial.println(name);
    }

    if (gotGps && !gotImu) {
      Serial.println("WARNING: Did not get IMU data. Restarting.");
      bno08x.hardwareReset();
    }

    if (!gotGps) {
      Serial.println("Got GPS data!");
      gotGps = true;

        // No light when logging data.
      WiFiDrv::analogWrite(26, 0);
      WiFiDrv::analogWrite(25, 0);
      WiFiDrv::analogWrite(27, 0);
    }

    unsigned long uptime = tsSec - tsSecFirst;
    float imuFloatRate = imuFloatCount / uptime;
    float imuDataRate = imuFloatRate * 4;
    uint32_t currentFileSize = file.fileSize(); // bytes
    Serial.print("IMU data rate: ");
    Serial.print(imuDataRate);
    Serial.println(" bytes/s");
    // For 100 / 20 / 10 -> 1800 bytes/s

    if (pingDtSecCount == 0) {
      String status = String(tsSec) + "," + String(latitude, 7) + "," + String(longitude, 7) + "," + String(satellites) + "," + String(imuDataRate) + "," + String(currentFileSize);
      if (!client.connected()) {
        client.stop();
        client.connect(server, 80);
      }
      if (client.connected()) {
        client.println("POST /" + String(CLOUD_KEY) + "/ping HTTP/1.1");
        client.println("Host: opendlv.io");
        client.println("Content-Type: text/plain");
        client.println("Content-Length: " + String(status.length()));
        client.println("Connection: keep-alive");
        client.println();
        client.println(status);
      }
    }
    pingDtSecCount++;
    if (pingDtSecCount == pingDtSec) {
      pingDtSecCount = 0;
    }
  }

  if (bno08x.wasReset()) {
    imuSubscribe();
  }

  if (bno08x.getSensorEvent(&sensorValue)) {
    unsigned long nowUs = micros();
    unsigned long sinceSyncUs = nowUs - syncUs; // Tested safe for overflow.

    unsigned long tsSec2 = tsSec + (sinceSyncUs + tsUs) / 1000000;
    unsigned long tsUs2 = (sinceSyncUs + tsUs) % 1000000;

    if (file) {
      if (!gotImu) {
        Serial.println("Got IMU data!");
        gotImu = true;
      }

      switch (sensorValue.sensorId) {

        case SH2_ACCELEROMETER:
        {
          byte const id = 1;
          memcpy(&buffer[bufferOffset + 0], &id, 1);
          memcpy(&buffer[bufferOffset + 1], &tsSec2, 4);
          memcpy(&buffer[bufferOffset + 5], &tsUs2, 4);
          memcpy(&buffer[bufferOffset + 9], &sensorValue.un.accelerometer.x, 4);
          memcpy(&buffer[bufferOffset + 13], &sensorValue.un.accelerometer.y, 4);
          memcpy(&buffer[bufferOffset + 17], &sensorValue.un.accelerometer.z, 4);
          bufferOffset += 21;

          imuFloatCount += 3;

          break;
        }
        case SH2_GYROSCOPE_CALIBRATED:
        {
          byte const id = 2;
          memcpy(&buffer[bufferOffset + 0], &id, 1);
          memcpy(&buffer[bufferOffset + 1], &tsSec2, 4);
          memcpy(&buffer[bufferOffset + 5], &tsUs2, 4);
          memcpy(&buffer[bufferOffset + 9], &sensorValue.un.gyroscope.x, 4);
          memcpy(&buffer[bufferOffset + 13], &sensorValue.un.gyroscope.y, 4);
          memcpy(&buffer[bufferOffset + 17], &sensorValue.un.gyroscope.z, 4);
          bufferOffset += 21;

          imuFloatCount += 3;

          break;
        }
        case SH2_ROTATION_VECTOR:
        {
          byte const id = 3;
          memcpy(&buffer[bufferOffset + 0], &id, 1);
          memcpy(&buffer[bufferOffset + 1], &tsSec2, 4);
          memcpy(&buffer[bufferOffset + 5], &tsUs2, 4);
          memcpy(&buffer[bufferOffset + 9], &sensorValue.un.rotationVector.i, 4);
          memcpy(&buffer[bufferOffset + 13], &sensorValue.un.rotationVector.j, 4);
          memcpy(&buffer[bufferOffset + 17], &sensorValue.un.rotationVector.k, 4);
          memcpy(&buffer[bufferOffset + 21], &sensorValue.un.rotationVector.real, 4);
          bufferOffset += 25;

          imuFloatCount += 4;

          break;
        }
      }
    }
  }

  if (bufferOffset > 512) {
   file.write(&buffer[0], bufferOffset);
   file.flush();
   bufferOffset = 0;
  }
}
