import socket
import sacn
import argparse
import json

# program options
parser = argparse.ArgumentParser(description='record sACN E1.31 led data, and store it to file')
parser.add_argument('config_file', type=str,
                    help='config file that describe which univers to map to which strip')
parser.add_argument('out_file', type=str,
                    help='file to write frames into')
parser.add_argument('-n, --pixels_per_string', dest='pixels_per_string', action='store', type=int,
                    default=1000, help='number of pixels on every string')
parser.add_argument('--number_of_strings', dest='number_of_strings', action='store', type=int,
                    default=8, help='number of strings in the controller')
parser.add_argument('--port', dest='port', action='store', type=int,
                    default=5568, help='port to listen for sACN data')
parser.add_argument('--ip', dest='ip', action='store', type=str,
                    default='127.0.0.1',
                    help='ip of interface to listen for sACN data')
args = parser.parse_args()

# initialize rgb_data to store universe data until a full frame is received
channels_per_pixel = 3
total_pixels = args.number_of_strings * args.pixels_per_string
total_channels = total_pixels * channels_per_pixel
rgb_data = bytearray([0] * total_channels)

# read config data into uni_to_range
uni_to_range = {}
with open(args.config_file) as json_file:
    json_data = json.loads(json_file.read())
    for uni, uni_config in json_data.items():
        start_index = (uni_config['string_id'] * args.pixels_per_string + uni_config['pixel_in_string']) * channels_per_pixel
        if uni_config['num_of_pixels'] > 170:
            raise ValueError("num_of_pixels too high for sACN. should be <= 170, recived: " + str(uni_config['num_of_pixels']))
        num_of_channels = uni_config['num_of_pixels'] * channels_per_pixel
        uni_to_range[int(uni)] = (start_index, num_of_channels)

# open udp recv socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
sock.bind((args.ip, args.port))

# handle write to file
f = open(args.out_file, "w+b")
recv_uni = {}
total_frames = 0

while True:
    raw_data, _= sock.recvfrom(1144)  # 1144 because the longest possible packet
    try:
        tmp_packet = sacn.DataPacket.make_data_packet(raw_data)
    except:  # try to make a DataPacket. If it fails just go over it
        continue

    if tmp_packet.universe in uni_to_range:
        arr_range = uni_to_range[tmp_packet.universe]
        rgb_data[arr_range[0] : arr_range[0] + arr_range[1]] = bytearray(tmp_packet.dmxData[0 : arr_range[1]])
        recv_uni[tmp_packet.universe] = True
        if len(recv_uni) == len(uni_to_range):
            f.write(rgb_data)
            total_frames += 1
            if total_frames % 100 == 0:
                print('wrote {} frames to file so far'.format(total_frames))
            recv_uni = {}
