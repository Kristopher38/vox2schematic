from PIL import Image
from nbt.nbt import *
from io import BytesIO
from os import path
from argparse import ArgumentParser
from pyvox.pyvox.parser import VoxParser

formats = ['png', 'vox']

# prepend data with 4 bytes of data length and wrap it around BytesIO stream
# to be usable with NBT library in TAG_Byte_Array constructor as buffer parameter
def list_to_byte_array(blockdata):
	return BytesIO(len(blockdata).to_bytes(4, byteorder='big') + bytearray(blockdata))

def init_parser():
	parser = ArgumentParser(description='Converts various voxel formats to minecraft .schematic files')
	parser.add_argument('filename', help='File to convert')
	parser.add_argument('-o', '--output', help='Filename of the resulting file, defaults to filename.schematic')
	parser.add_argument('-f', '--format', help='Input file format, possible values are "png" for 2d PNG slice (requires dimensions to be specified with -d) and "vox". Redundant if file has a valid extension', choices=formats)
	parser.add_argument('-d', '--dimensions', help='Dimensions specified as "width length height" (You can just copy-paste it from MagicaVoxel)', nargs=3, type=int, metavar=('WIDTH', 'LENGTH', 'HEIGHT'))
	parser.add_argument('-b', '--blockid', help='Block id to use when converting to .schematic, defaults to 1 (stone)', type=int, default=1)
	return parser

def parse_args(parser):
	args = parser.parse_args()
	
	# deduce format from filename
	if args.format is None:
		extension = path.splitext(path.basename(args.filename))[1]
		if len(extension) > 0:
			# get rid of the dot in the extension
			extension = extension[1:]
			if extension in formats:
				args.format = extension
			else:
				parser.error('Wrong input file extension. Change your input file extension or specify format explicitly with -f')
		else:
			parser.error('Could not deduce format from filename because file extension is missing. Specify extension explicitly with -f')
			
	# force specifying dimensions for png format
	if args.format == 'png' and args.dimensions is None:
		parser.error('PNG format requires dimensions to be specified with -d')
		
	# deduce output filename from input filename
	if args.output is None:
		args.output = "{filename}.schematic".format(filename=path.splitext(path.basename(args.filename))[0])
	return args
	
def png_handler(args):
	model = Image.open(args.filename)
	sizex, sizey = model.size
	blocks = []
	for y in range(0, sizey):
		for x in range(0, sizex):
			rgb = model.getpixel((x, y))
			if rgb[3] != 0:
				blocks.append(args.blockid)
			else:
				blocks.append(0)

	blocks = list(reversed(blocks))
	blocks_ext = [0 for i in range(0, len(blocks))]
	width, length, height = args.dimensions
	return (width, length, height, blocks, blocks_ext)
	
def vox_handler(args):
	model = VoxParser(args.filename).parse()
	
	length, width, height = model.models[0].size

	blocks = [0]*(width*length*height)
		
	for z, x, y, c in model.models[0].voxels:
		blocks[(y*length + z)*width + x] = args.blockid
	
	blocks_ext = [0 for i in range(0, len(blocks))]
	return (width, length, height, blocks, blocks_ext)

def write_schematic(args, w, l, h, blocks, data):
	nbtfile = NBTFile()
	nbtfile.name = "Schematic"
	nbtfile.tags.append(TAG_Short(name="Width", value=w))
	nbtfile.tags.append(TAG_Short(name="Length", value=l))
	nbtfile.tags.append(TAG_Short(name="Height", value=h))
	nbtfile.tags.append(TAG_String(name="Materials", value="Alpha"))
	nbtfile.tags.append(TAG_Byte_Array(name="Blocks", buffer=list_to_byte_array(blocks)))
	nbtfile.tags.append(TAG_Byte_Array(name="Data", buffer=list_to_byte_array(data)))
	nbtfile.tags.append(TAG_List(name="Entities", type=TAG_Compound))
	nbtfile.tags.append(TAG_List(name="TileEntities", type=TAG_Compound))
	nbtfile.write_file(args.output)

handlers = {'png': png_handler, 'vox': vox_handler}

def main():
	parser = init_parser()
	args = parse_args(parser)
	
	w, l, h, blocks, data = handlers[args.format](args)
	write_schematic(args, w, l, h, blocks, data)

if __name__ == "__main__":
	main()