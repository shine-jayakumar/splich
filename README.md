# Splich (Split-Stitch)
![MIT License](https://img.shields.io/github/license/shine-jayakumar/Covid19-Exploratory-Analysis-With-SQL)

### Splits a file into parts or stitches them back

<p align="center">
<img src="https://github.com/shine-jayakumar/splich/blob/main/splich_logo.png"/>
</p>

Splich, because it can split or stitch, is a simple file splitting tool written in python that can split a file into parts, and stitch them back together.

**Table of Contents**
- [Features](#Features "Features")
- [Requirements](#Requirements "Requirements")
- [Options](#Options "Options")
- [Usage](#Usage "Usage")
- [Examples](#Examples "Examples")
- [License](#LICENSE "License")

## Features
- Split into specific number of parts
- Split into parts of specific size
- Automatically finds the split parts in the directory
- SHA256 hash verification included

## Requirements
- Python 3

## Options
Required arguments
| Argument | Description |
| ------ | ------ |
| filename | File to split or stitch |

Optional Arguments
| Option | Description |
| ------ | ------ |
| -sp, --split | split the file |
| -st, --stitch |  stitch the file |
| -p , --parts | number of parts to split in |
| -s , --size | size of each chunk |
| -hf , --hashfile | file containing hash of the original file |
| -o , --outfile | write stitched file to (default - same as the input file) |
| -vv, --verbose | verbose mode |
| -v, --version | show program's version number and exit |

## Usage
**To split a file into specific number of parts**
```
splich.py file --split --parts no_of_parts
```

**To split a file into parts of specific size**
```
splich.py file --split --size size_of_each_part
```

**To stitch a file**
```
splich.py original_filename --stitch
```

**To specify an output file to place stitched files to**
```
splich.py original_filename --stitch -o newfile
```

**To hash verify while stitching**
```
splich.py original_filename --stitch -hf hash_file_from_split
```

## Examples
```
splich.py ebook.pdf --split --size 100000
```
```
splich.py flask.pdf --split --parts 10
```
<img src="https://github.com/shine-jayakumar/splich/blob/main/splich_into_parts.JPG"/>

```
splich.py flask.pdf --stitch -o flask_stitched -hf flask_hash_05112022_1126 --verbose
```
<img src="https://github.com/shine-jayakumar/splich/blob/main/splich_stitch.JPG"/>

## LICENSE
[MIT](https://github.com/shine-jayakumar/splich/blob/main/LICENSE)
