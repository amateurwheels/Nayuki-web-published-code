# 
# Fit motion displacements
# 
# Reads a TSV file with motion vectors, performs analysis, and writes to standard output.
# Requires NumPy library.
# 
# Copyright (c) 2020 Project Nayuki
# All rights reserved. Contact Nayuki for licensing.
# https://www.nayuki.io/page/go-train-acceleration-analyzed-by-video
# 

import math, numpy, pathlib, sys


def main(args):
	if len(args) != 1:
		sys.exit("Usage: python fit-motion-displacements.py motion-vectors.tsv")
	
	# Read TSV file data into ndarray
	data = []
	with pathlib.Path(args[0]).open("rt", encoding="UTF-8", newline=None) as fin:
		for (i, line) in enumerate(fin):
			line = line.rstrip("\n")
			parts = line.split("\t")
			if len(parts) != 4:
				raise ValueError("Expected 4 columns")
			if i > 0:
				data.append(tuple(int(part) for part in parts))
	data = numpy.array(data, dtype=numpy.int32)
	
	# Construct and initialize matrix of appropriate dimensions
	mintime = numpy.min(data[:, 0:2])
	maxtime = numpy.max(data[:, 0:2])
	if mintime < 0:
	    raise ValueError("Minimum time must be non-negative")
	matrix = numpy.zeros(shape=(data.shape[0] + 1, maxtime + 1), dtype=numpy.float64)
	matrix[-1, 0] = 1
	for (i, row) in enumerate(data):
		matrix[i, row[0]] = -1
		matrix[i, row[1]] = +1
	
	# Solve for x and y vectors
	vectorx = numpy.concatenate((data[:, 2], [0]))
	vectory = numpy.concatenate((data[:, 3], [0]))
	solutionx = numpy.linalg.lstsq(matrix, vectorx)[0]
	solutiony = numpy.linalg.lstsq(matrix, vectory)[0]
	solutionx -= solutionx[0]
	solutiony -= solutiony[0]
	
	# Print results
	print("Frame", "Displacement x (pixels)", "Displacement y (pixels)", "Displacement magnitude (pixels)", sep="\t")
	for i in range(solutionx.size):
		x = solutionx[i]
		y = solutiony[i]
		print(i, x, y, math.hypot(x, y), sep="\t")


if __name__ == "__main__":
	main(sys.argv[1 : ])
