# VisioWords
A word cloud visualizer implemented in Python and PyGame

## Installation
VisioWords needs [PyGame](https://bitbucket.org/pygame/pygame) to work. It can be easily installed using PIP with `pip install pygame`. 

## Usage
Modify the `config.txt`, and run `python visiowords.py`.
When the image is ready, hit <kbd>CTRL</kbd>/<kbd>CMD</kbd>+<kbd>S</kbd> to save the image. The filename will be created from the input filename and the images width and height, existing images will be overwritten.

## Example
The example uses some dummy text (from [Blind Text Generator](http://www.blindtextgenerator.com)) using a mask
![Example using a mask](example_mask.png)

or without a mask

![Example without a mask](example.png)

## TODO
- [ ] Allow repetition of words (to fill masks)
- [ ] Add more shortcuts
- [ ] Allow alternative input format

