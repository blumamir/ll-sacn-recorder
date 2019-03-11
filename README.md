This is a python3 script, that listen for sACN packets, aggregate them into frames, and write the frames to a givin file.

# Install
You need to have python 3 installed on your computer.
the project uses pipenv for dependency management. you can install pipenv with `pip install pipenv`
To check that pipenv is intall and found in PATH, run `pipenv --version`.
Then run pipenv shell to enter the venv.

# Usage
`python ./capture.py --help` will show help about how to run the program.
You need to use config file in json format that describe which univere numbers are expected, how many pixels are hold, and to which stip id, and pixel in pixel within the strip they should be map.
The script will wait for a full frame (e.g. for all the universes in the config file to be received), and then write the frame to the `out_file` (as specify as command line argument).
The frame will always hold exactly `number_of_strings` * `pixels_per_string` pixels, with 3 channels each.
Channels are written to the file in the order they are found in the sACN packet. That means that if you want to change RGB order (according to the order of the physical LEDs), you need to configure the sending application appropriately.
If you don't need all strings, or all pixels in a string, just don't configure them in the `config.json` file, and they will not be updated (will just always contain `0`)
