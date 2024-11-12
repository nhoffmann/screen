# Screen

The goal is to control a bunch of LED matrix connected to ESP32 board via network commands. The system should be modular, in the way that it allows adding and removing boards to the control software. How the control software makes use of the boards, is not defined. Ideally, the LED matrix should be refreshable 25 times per second, so we can show smooth animations and even video.

## board

The code on the ESP32 board code is currently written in micropython.

The board currently used: ESP32 DevKitC V2 ESP32-WROOM-32

### Naive implementation:

* Listen for pixel data on a TCP socket
* The pixel data is a list of rgb tuples, e.g. `[(1, 127, 255), (0, 0, 0), (1, 127, 255), (0, 0, 0)]`. This is also the format that neopixel expects.
* The pixel data is encoded as json string 
* When pixel data is received, it is unpacked and decodeed and written to the connected LED strip/matrix

### Problems

With the current board we can smoothly support LED matrixes/strips of 256 pixels at a framerate of 25 pixel.
Doubling the amount of pixels already leads to problems like memory allocation errors on the board.

This is not the time yet for optimising. However, I experimented with a few ideas already, just to see what is feasible.

#### Idea: Compress the pixeldata sent over the network

Encoded the pixel data as a hex string, e.g. `007FFF000000007FFF000000`. This way we have a fixed length, less overhead from the naive json encoding and thus it signifcantly reduces the size of the pixel data we are sending over the network. But comes with the problem that we need to unpack the hex values on the ESP32 board.
At least in python this is not feasible, because it is just to slow. Unpacking a pixel array of 256 pixels takes about 0.2 seconds. While this technically works, it leads to a lot of dropped frames, because we cannot unpack the hexstring in the time to run 25 fps, which means a new frame every 0.04 seconds.

#### Idea: Use a beefier development board

TODO: Investigate whether a development board with more RAM will solve the problem for larger pixel array

#### Idea: Run the board on Rust instead of micropython

This is certainly a whole other can of worms. 

## controller

The "screen" is defined as a continous pixel screen over all available (registered) LED boards.

* The controller keeps track of the available boards
* The controller knows about the position of every board
* The controller provides functionality to draw pixel data onto the screen. After drawing the pixel data it provides functionality to send the appropriate pixel data to the connected boards
