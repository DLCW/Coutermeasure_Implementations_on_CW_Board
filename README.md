To compile and acquire power traces for a specific countermeasure, please follow the steps described hereafter:
1. Under /home/cwuser/chipwhisperer/hardware/victims/firmware/ copy the repository of the targeted countermeasure you want to assess.
2. Do a make to generate the corresponding ".hex" file.
3. Open the CWCapture software and select "Project/Example Scripts" tab and click the  "ChipWhisperer-Lite: SPA SimpleSerial on XMEGA" button.
5. Wait a bit until the scope and the target icons turn to the "COM" status in yellow.
6. Select the "Tools" tab and click the "CW-Lite XMEGA Programmer" button.
7. Select your ".hex" file in the appropriate folder.
8. Click on "Erase/Program/Verify Flash" button to load your implementation in the XMEGA device.
9. Close the CWCapture software.
10. Lunch the python script to start the acquisition.