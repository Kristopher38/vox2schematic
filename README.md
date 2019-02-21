# vox2schematic
Converts MagicaVoxel's .vox and .png volume slices files to .schematic files

## Required libraries
- pillow
- nbt
- py-vox-io

```
pip install pillow
pip install nbt
pip install py-vox-io
```

## Usage
```
python vox2schematic.py [-h] [-o OUTPUT] [-f {png,vox}]
                        [-d WIDTH LENGTH HEIGHT] [-b BLOCKID]
                        filename
```

Examples:
```
python vox2schematic.py teapot.vox
python vox2schematic.py teapot.png -d 126 80 61
```

Notes:
- You need to specify dimensions if you want to use .png volume slices format. You can just copy-paste them directly from MagicaVoxel without changing their order. If you're converting from .vox format, this option can be skipped.
- Currently script uses only one type of block when converting to .schematic, which can be specified with option -b BLOCKID. Support for multiple block types based on color palette is not yet supported.
- For explanation of the rest of CLI options, refer to `python vox2schematic.py -h`