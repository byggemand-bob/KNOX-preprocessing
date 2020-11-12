import os
import fitz
import argparse
import concurrent.futures as cf

__zoom = 3
__verbose = False

def convert(file: str, out_dir: str):
    mat = fitz.Matrix(__zoom, __zoom)

    # Open image and get page count
    doc = fitz.open(file)
    number_of_pages = doc.pageCount

    # Convert each page to an image
    for x in range(number_of_pages):
        page = doc.loadPage(x)
        pix = page.getPixmap(matrix=mat)
        outputName = os.path.basename(file).replace(".pdf", "") + "_page" + str(x+1) + ".png"
        pix.writePNG(os.path.join(out_dir, outputName))

    if __verbose is True:
        print("  Converted " + file)

def convert_dir(in_dir: str, out_dir: str):
    

    # Go through every file in the input dir and append to list.
    files = []
    out_dirs = []
    for file in os.listdir(in_dir,):
        if file.endswith(".pdf"):
            files.append(os.path.join(in_dir,file))
            out_dirs.append(out_dir)

    with cf.ProcessPoolExecutor() as executor:
        executor.map(convert, files, out_dirs)



if __name__ == "__main__":
    # Setup command-line arguments
    parser = argparse.ArgumentParser(description="Convert pdf files to png images.")
    parser.add_argument("in_dir", metavar="IN_DIR", type=str, help="Path the input folder.")
    parser.add_argument("out_dir", metavar="OUT_DIR", type=str, help="Path to output folder.")
    parser.add_argument("-z", "--zoom", metavar="N", type=int, default=3, help="Zoom of the PDF conversion.")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Print more information.")
    args = parser.parse_args()

    __zoom = args.zoom
    __verbose = args.verbose

    # Make sure that input dir exists
    if not os.path.exists(args.in_dir):
        raise OSError("Directory not found.")

    # Make sure that output exists. If not, create the dir.
    if not os.path.exists(args.out_dir):
        os.mkdir(args.out_dir)

    # Print the number of files to be converted.
    num_files = len([f for f in os.listdir(args.in_dir)if os.path.isfile(os.path.join(args.in_dir, f))])
    if __verbose is True:
        print("Converting " + str(num_files) + " PDF's")

    # Convert all pdfs.
    convert_dir(args.in_dir, args.out_dir)
    
    # Print number of files created.
    num_files = len([f for f in os.listdir(args.out_dir)if os.path.isfile(os.path.join(args.out_dir, f))])
    if __verbose is True:
        print("Created " + str(num_files) + " PNG's")
    exit()
