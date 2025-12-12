USB
The socket address for USB connections is 172.2X.1YZ.51:8080 where XYZ are the last three digits of the camera's serial number.

The camera's serial number can be obtained in any of the following ways:

Reading the sticker inside the camera's battery enclosure
Camera UI: Preferences >> About >> Camera Info
Bluetooth Low Energy: By reading directly from Hardware Info
For example, if the camera's serial number is C0000123456789, the IP address for USB connections would be 172.27.189.51.

Alternatively, the IP address can be discovered via mDNS as the camera registers the _gopro-web service.

MITZ GoPros:
- "172.29.197.51" (deployed in setup)
- "172.25.190.51"