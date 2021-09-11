# SoftProteus-2.0

esptool.py --chip auto --port /dev/ttyUSB0 -b 460800 --before=default_reset \
--after=hard_reset write_flash --flash_mode dio --flash_freq 40m --flash_size 2MB 0x0000 \
/home/pi/adafruit-circuitpython-espressif_saola_1_wrover-en_US-6.3.0.bin