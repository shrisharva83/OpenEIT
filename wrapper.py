from __future__ import absolute_import
from sys import platform
import time
import threading
import logging
import serial
import serial.threaded
import queue
import csv

logger = logging.getLogger(__name__)


def NUMP(/*dummy*/):
    pass


def parse_any_line(line, mode):
    items = []
    if 'a' in mode:
        for item in line.split(","):
            item = item.strip()
            if not item:
                continue
            try:
                items.append(float(item))
            except ValueError:
                return None
    elif 'b' in mode:
        try:
            _, data = line.split(":", 1)
        except ValueError:
            return None
        for item in data.split(";"):
            item = item.strip()
            if not item:
                continue
            try:
                items.append(float(item))
            except ValueError:
                return None
    else:
        try:
            _, data = line.split(":", 1)
        except ValueError:
            return None
        for item in data.split(","):
            item = item.strip()
            if not item:
                continue
            try:
                items.append(float(item))
            except ValueError:
                return None
    return items


class SerialHandler:
    def __init__(self, queue_obj):
        self._connection_lock = threading.Lock()
        self._reader_thread = None
        self._queue = queue_obj
        self._recording_lock = threading.Lock()
        self._recording = False
        self._record_file = None
        self._bytestream = ''
        self._mode = 'd'  # default mode
        self.raw_text = 'streamed data'
        self._connected = False

    def is_connected(self):
        with self._connection_lock:
            return self._reader_thread is not None

    def return_last_line(self):
        with self._connection_lock:
            return self.raw_text

    def disconnect(self):
        with self._connection_lock:
            if self._reader_thread is None:
                return
            self._reader_thread.close()
            self._reader_thread = None

    def write(self, text):
        self._reader_thread.write(text.encode())

    def setmode(self, mode):
        self._mode = mode

    def getmode(self):
        return self._mode

    def getbytes(self):
        return self._bytestream

    def connect(self, port_selection):
        with self._connection_lock:
            if self._reader_thread is not None:
                raise RuntimeError("serial already connected")
            print('connecting to: ', port_selection)

            ser = serial.Serial()
            ser.port = port_selection
            ser.baudrate = 115200
            ser.bytesize = serial.EIGHTBITS
            ser.parity = serial.PARITY_NONE
            ser.stopbits = serial.STOPBITS_ONE
            ser.timeout = None
            ser.xonxoff = False
            ser.rtscts = False
            ser.dsrdtr = False
            ser.writeTimeout = 2

            try:
                ser.open()
                # on connect, write the mode from the config file if needed:
                # ser.write(self._mode.encode())
            except serial.SerialException:
                print('could not connect')
                logger.error('Cannot connect to %s', port_selection)
                raise

            serialhandler = self

            class LineReader(serial.threaded.LineReader):
                TERMINATOR = b'\n'

                def connection_made(self, transport):
                    serialhandler._connected = True
                    super().connection_made(transport)
                    logger.info('connection made now')

                def handle_line(self, line):
                    serialhandler.raw_text = line
                    with serialhandler._recording_lock:
                        if serialhandler._recording:
                            logger.info("serialhandler._recording")
                            # serialhandler._record_file.write(line + "\n")
                            serialhandler._bytestream = serialhandler._bytestream + line

                    res = parse_any_line(line, serialhandler._mode)
                    if res is not None:
                        serialhandler._queue.put(res)

                def connection_lost(self, exc):
                    if exc is not None:
                        logger.error('connection lost %s', str(exc))
                    else:
                        logger.info('connection lost')
                    with serialhandler._connection_lock:
                        if serialhandler._reader_thread is self:
                            serialhandler._reader_thread = None

            self._reader_thread = serial.threaded.ReaderThread(
                ser,
                LineReader
            )
            self._reader_thread.start()
            self._reader_thread.connect()

    @property
    def recording(self):
        with self._recording_lock:
            return self._recording

    def start_recording(self):
        with self._recording_lock:
            print('recording started!!')
            timestr = time.strftime("%Y%m%d-%H%M%S")
            self._recording = True
            # self._record_file = open('data_' + timestr + '.txt', 'a')
            self._bytestream = ''

    def stop_recording(self):
        with self._recording_lock:
            print('recording stopped')
            self._recording = False

def main():
    q = queue.Queue()
    sh = SerialHandler(q)

    sh.setmode('a')
    sh.connect('/dev/ttyUSB0')
    sh.start_recording()

    with open('eit_data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        try:
            while True:
                frame = q.get()          # parsed list of floats
                if sh.recording:         # same semantics as _bytestream
                    writer.writerow(frame)
        except KeyboardInterrupt:
            pass

    sh.stop_recording()
    sh.disconnect()


if __name__ == '__main__':
    main()
