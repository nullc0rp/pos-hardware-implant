import asyncio
import wave
import sys
from bleak import BleakClient
from struct import *
from operator import *


recording = False
buffer_data = []
buffer_string = ""

mag_data_track_1 = {
    "0000000": " ",
    "0000001": " ",


    "0100010": "?",
    "1000010": "?",
    "0000101": "?",
    "0101101": "?",
    "1011001": "?",
    "1000000": "?",
    "0000011": "?",
    "1000100": "?",
    "0100001": "?",
    "1111110": "?",
    "0000101": "?",
    "0101101": "?",


    "0100000": "\"",
    "1100001": "#",
    "0010000": "$",
    "1010001": "%",
    "0110001": "&",
    "1110000": "'",
    "0001000": "(",
    "1001001": ")",
    "0101001": "*",
    "1101000": "+",
    "0011001": ",",
    "1011000": "-",
    "0111000": ".",
    "1111001": "/",
    "0000100": "0",
    "1000101": "1",
    "0100101": "2",
    "1100100": "3",
    "0010101": "4",
    "1010100": "5",
    "0110100": "6",
    "1110101": "7",
    "0001101": "8",
    "1001100": "9",
    "0101100": ":",
    "1101101": ";",
    "0011100": "<",
    "1011101": "=",
    "0111101": ">",
    "1111100": "?",
    "0000010": "@",
    "1000011": "A",
    "0100011": "B",
    "1100010": "C",
    "0010011": "D",
    "1010010": "E",
    "0110010": "F",
    "1110011": "G",
    "0001011": "H",
    "1001010": "I",
    "0101010": "J",
    "1101011": "K",
    "0011010": "L",
    "1011011": "M",
    "0111011": "N",
    "1111010": "O",
    "0000111": "P",
    "1000110": "Q",
    "0100110": "R",
    "1100111": "S",
    "0010110": "T",
    "1010111": "U",
    "0110111": "V",
    "1110110": "W",
    "0001110": "X",
    "1001111": "Y",
    "0101111": "Z",
    "1101110": "[",
    "0011111": "\\",
    "1011110": "]",
    "0111110": "^",
    "1111111": "_",
}

mag_data_track_2 = {
    "00000": " ",
    "00001": "0",
    "10000": "1",
    "01000": "2",
    "11001": "3",
    "00100": "4",
    "10101": "5",
    "01101": "6",
    "11100": "7",
    "00010": "8",
    "10011": "9",
    "01011": ":",
    "11010": ";",
    "00111": "<",
    "10110": "=",
    "01110": ">",
    "11111": "?"
}

def parse_wav(filename, thresh):
  track = wave.open(filename)
  params = track.getparams()
  frames = track.getnframes()
  channels = track.getnchannels()

  if not channels == 1:
    sys.stderr.write("track must be mono!")
    sys.exit(False)

  sys.stderr.write("chanels: " + str(channels))
  sys.stderr.write("\nbits: " + str(track.getsampwidth() * 8))
  sys.stderr.write("\nsample rate: " + str(track.getframerate()))
  sys.stderr.write("\nnumber of frames: " + str(frames))
  sys.stderr.write("\n")

  n = 0
  max = 0
  samples = []

  # determine max sample and build sample list
  while n < frames:
    n += 1
    # make sample an absolute value to simplify things later on
    current = abs(unpack("h", track.readframes(1))[0])
    if current > max:
      max = current;
    samples.append(current)

  # set silence threshold
  silence = max / thresh
  sys.stderr.write("silence threshold: " + str(silence))
  sys.stderr.write("\n")

  # create a list of distances between peak values in numbers of samples
  # this gives you the flux transition frequency

  peak = 0
  ppeak = 0
  peaks = []

  n = 0
  while n < frames:
    ppeak = peak
    # skip to next data
    while n < frames and samples[n] <= silence:
      n = n + 1
    peak = 0
    # keep going until we drop back down to silence
    while n < frames and samples[n] > silence:
      if samples[n] > samples[peak]:
        peak = n
      n = n + 1
    # if we've found a peak, store distance
    if peak - ppeak > 0:
      peaks.append(peak - ppeak)

  sys.stderr.write("max: " + str(max))
  sys.stderr.write("\n")

  # read data - assuming first databyte is a zero
  # a one will be represented by two half-frequency peaks and a zero by a full frequency peak
  # ignore the first two peaks to be sure we're past leading crap
  zerobl = peaks[2]
  n = 2
  # allow some percentage deviation
  freq_thres = 60
  output = ''
  while n < len(peaks) - 1:
    if peaks[n] < ((zerobl / 2) + (freq_thres * (zerobl / 2) / 100)) and peaks[n] > (
            (zerobl / 2) - (freq_thres * (zerobl / 2) / 100)):
      if peaks[n + 1] < ((zerobl / 2) + (freq_thres * (zerobl / 2) / 100)) and peaks[n + 1] > (
              (zerobl / 2) - (freq_thres * (zerobl / 2) / 100)):
        output += '1'
        zerobl = peaks[n] * 2
        n = n + 1
    else:
      if peaks[n] < (zerobl + (freq_thres * zerobl / 100)) and peaks[n] > (zerobl - (freq_thres * zerobl / 100)):
        output += '0'
        zerobl = peaks[n]
    n = n + 1
  sys.stderr.write("number of bits: " + str(len(output)))
  sys.stderr.write("\n")
  print(output)

  # sentinel_found = False
  # while not sentinel_found and len(output) > 6:
  #     first_6 = output[:7]
  #     if first_6 == "1010001":
  #         sentinel_found = True
  #     else:
  #         output = output[1:]
  #
  # n = 7
  # chunks = [output[i:i + n] for i in range(0, len(output), n)]
  # print(chunks)
  # result_a = ""
  # for chunk in chunks:
  #     if len(chunk) > 6:
  #         result_a = result_a + mag_data_track_1[chunk]
  # print(result_a)

  sentinel_found = False
  while not sentinel_found and len(output) > 4:
    first_6 = output[:5]
    if first_6 == "11010":
      sentinel_found = True
    else:
      output = output[1:]

  n = 5
  chunks = [output[i:i + n] for i in range(0, len(output), n)]
  print(chunks)
  result_a = ""
  for chunk in chunks:
    if len(chunk) > 4:
      if chunk in mag_data_track_2.keys():
        result_a = result_a + mag_data_track_2[chunk]
      else:
        result_a = result_a + "?"

  print(result_a)


def create_wav_file(filename, integer_numbers, sample_width=2, sample_rate=44100):
  with wave.open(filename, 'w') as wav_file:
    wav_file.setnchannels(1)  # Mono audio
    wav_file.setsampwidth(sample_width)  # Sample width in bytes
    wav_file.setframerate(sample_rate)  # Sample rate in Hz

    # Convert integer numbers to bytes
    byte_data = bytearray()
    for number in integer_numbers:
      number_buff = number * 10
      byte_data.extend(number_buff.to_bytes(sample_width, 'little', signed=True))

    wav_file.writeframes(byte_data)

def callback_spp(handle, data):
  global recording
  global buffer_data
  global buffer_string
  if recording:
    buffer_string = buffer_string+data.decode('utf-8')
  if "*" in  data.decode('utf-8'):
    print("started")
    recording = True
  if "#" in  data.decode('utf-8'):
    print("ended")
    recording = False
    buffer_string = buffer_string.replace("*", "")
    buffer_string = buffer_string.replace("#", "")
    buffer_string = buffer_string.replace("\r", "")
    chunks = buffer_string.split('\n')
    for chunk in chunks:
      if chunk != "":
        buffer_data.append(int(chunk))
    buffer_string = ""
    print(buffer_data)
    print(len(buffer_data))


    #Creating wav file
    filename = 'output2.wav'
    counter = 1
    while counter < len(buffer_data) - 1:
      if buffer_data[counter] < 0 and buffer_data[counter - 1] > 0 and buffer_data[counter + 1] > 0:
        buffer_data[counter] = (buffer_data[counter - 1] + buffer_data[counter + 1]) // 2
      counter = counter + 1

    create_wav_file(filename, buffer_data[::-1])
    parse_wav(filename, 100 / 33)

    buffer_data = []


async def main(address):
  async with BleakClient(address) as client:
    if (not client.is_connected):
      raise "client not connected"

    name_bytes = await client.read_gatt_char("00002a27-0000-1000-8000-00805f9b34fb")
    name = bytearray.decode(name_bytes)
    print('name', name)

    await client.start_notify("0000ffe1-0000-1000-8000-00805f9b34fb", callback_spp)
    await asyncio.sleep(60000) #TODO: solve this hack

if __name__ == "__main__":
  address = "88:25:83:F0:15:57"
  print('address:', address)
  asyncio.run(main(address))