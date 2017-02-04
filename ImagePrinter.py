import numpy
def print01(image):
    im = numpy.array(image)
    for row in im:
        for pixel in row:
            if pixel>100:
                print("  ", end="")
            else:
                print("**", end="")
        print()