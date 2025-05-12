import math
import numpy as np

class Graph :

	def __init__(self):
		self.points = []
		self.lines = []
	
	def NewPoint(self, x, y) :
		self.points.append(Point(x, y))
	
	def AddPoint(self, point) :
		assert type(point) == Point
		self.points.append(point)
	
	def NewLine(self, point1, point2) :
		line = Line(point1, point2)
		print(f"created {line}")
		self.lines.append(line)
	
	def AddLine(self, line) :
		assert type(line) == Line
		self.lines.append(line)
	
	def GetLenPoints(self) :
		return len(self.points)
	
	def GetLenLines(self) :
		return len(self.lines)
	
	def GetPoint(self, index) :
		assert type(index) == int
		return self.points[index]
	
	def GetLine(self, index) :
		assert type(index) == int
		return self.lines[index]
	
	def RemovePointAt(self, index) :
		assert type(index) == int
		return self.points.pop(index)
	
	def RemoveLineAt(self, index) :
		assert type(index) == int
		self.lines[index].DetachFromPoints()
		return self.lines.pop(index)
	
	def RemovePoint(self, point) :
		assert type(point) == Point
		assert len(point.attachedLines) == 0
		return self.points.remove(point)
	
	def RemoveLine(self, line) :
		assert type(line) == Line
		line.DetachFromPoints()
		print(f"removed {line}")
		return self.lines.remove(line)
	


	def ApplyMatrixTransform(self, matrix) :

		for point in self.points :
			print(f"before matrix : {point.x}, {point.y}")
			vector = [point.x, point.y, 1]
			result = np.matmul(matrix, vector)
			print(result)
			point.x = int(result[0] / result[2])
			point.y = int(result[1] / result[2])
			print(f"after matrix : {point.x}, {point.y}")
	

	

	
	

class Point :

	def __init__(self, x = 0, y = 0) :
		assert type(x) == int and type(y) == int

		self.x = x
		self.y = y

		self.attachedLines = []
	
	def ToArray(self) :
		return [self.x, self.y]
	
	def ToTuple(self) :
		return (self.x, self.y)
	
	def AttachLine(self, line) :
		#print(f"attempt to connect point {self} to line {line}")
		#print(f"	this point is currently attached to {self.attachedLines}")

		assert type(line) == Line
		assert line not in self.attachedLines, "this line is already attached to this point"

		self.attachedLines.append(line)
	
	def DetachLine(self, line) :
		assert type(line) == Line
		assert line in self.attachedLines, "this line is not attached to this point"

		#print(f"detached point {self} from line {line}")
		self.attachedLines.remove(line)
		#print(f"	this point is still attached to {self.attachedLines}")
	

	def GetAngleBetweenAttachedLines(self, indexLine1, indexLine2) :
		assert type(indexLine1) == int and type(indexLine2) == int

		line1 = self.attachedLines[indexLine1]
		line2 = self.attachedLines[indexLine2]

		opposite1 = line1.GetOppositePoint(self)
		opposite2 = line2.GetOppositePoint(self)

		vec1x, vec1y = SubstractCoords(opposite1, self)
		vec2x, vec2y = SubstractCoords(opposite2, self)

		angle1 = math.atan2(vec1y, vec1x)
		angle2 = math.atan2(vec2y, vec2x)

		angleDiff = abs(angle1 - angle2)

		if angleDiff > math.pi :
			angleDiff -= math.pi

		return angleDiff	
	

""" Hold references to two points, and provide them with a reference to itself. Always detach it when not needed anymore """
class Line :

	def __init__(self, point1, point2):
		
		""" doesn't care about direction, is only in the range 0 - pi/2 """
		self.angle = 0
		self.length = 0
		self.attached = False

		self.AttachToPoints(point1, point2)

		
	
	def __del__(self) :
		# this causes an error sometimes, not sure why but is unnecessary anyways
		# self.DetachFromPoints()
		pass

	def RattachToPoints(self, point1, point2) :
		self.DetachFromPoints()
		self.AttachToPoints(point1, point2)
	
	def AttachToPoints(self, point1, point2) :
		assert type(point1) == Point and type(point2) == Point
		assert not self.attached, "this line is already attached to points"
		assert point1 != point2, "a line cannot be attached at both ends to the same point"

		self.point1 = point1
		self.point2 = point2

		self.CalculateDir()
		self.CalculateLength()

		point1.AttachLine(self)
		point2.AttachLine(self)

		self.attached = True
	
	def DetachFromPoints(self) :
		if self.point1 == None or self.point2 == None : return
		if not self.attached : return

		self.point1.DetachLine(self)
		self.point2.DetachLine(self)
		self.point1 = None
		self.point2 = None
		self.attached = False
	
	def CalculateDir(self) :

		deltaX = abs(self.point1.x - self.point2.x)
		deltaY = abs(self.point1.y - self.point2.y)

		if (deltaX == 0) :
			self.angle = math.pi/2
			return
		
		self.angle = math.atan(deltaY/deltaX)
	
	def CalculateLength(self) :
		self.length = math.sqrt((self.point1.x - self.point2.x)**2 + (self.point1.y - self.point2.y)**2)
	

	def GetOppositePoint(self, point) :
		assert type(point) == Point
		if self.point1 == point :
			return self.point2
		elif self.point2 == point :
			return self.point1
		else :
			raise RuntimeError("this point doesn't belong to the line")
	
	""" lack of proper term but used for offset check for colinearity """
	def GetElevation(self) :
		return self.point1.y * math.cos(self.angle) - self.point1.x * math.sin(self.angle)




def DistanceBetweenPoints(point1, point2) :
	assert type(point1) == Point and type(point2) == Point

	return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def SubstractCoords(point1, point2) :

	return point1.x - point2.x, point1.y - point2.y


def AreLineColinear(line1, line2, directionThreshold = 0.1, offsetThreshold = 5) :

	assert type(line1) == Line
	assert type(line2) == Line

	if abs(line1.angle - line2.angle) > directionThreshold :
		return False

	if abs(line1.GetElevation() - line2.GetElevation()) > offsetThreshold :
		return False
	
	return True

def GetClosestPointsOfLines(line1, line2) :

	assert type(line1) == Line
	assert type(line2) == Line


	dist1 = DistanceBetweenPoints(line1.point1, line2.point1)
	dist2 = DistanceBetweenPoints(line1.point1, line2.point2)
	dist3 = DistanceBetweenPoints(line1.point2, line2.point1)
	dist4 = DistanceBetweenPoints(line1.point2, line2.point2)

	best = min([dist1, dist2, dist3, dist4])

	if best == dist1 : return line1.point1, line2.point1
	if best == dist2 : return line1.point1, line2.point2
	if best == dist3 : return line1.point2, line2.point1
	if best == dist4 : return line1.point2, line2.point2

	raise RuntimeError("no closest points found, this shouldn't be possible")












""" ////// Line Filtering Functions /////// """



""" Remove useless lines that form a 180 """
def Remove180Turns(graph, angleThreshold = math.pi/8) :
	assert type(graph) == Graph

	i = 0
	while i < graph.GetLenPoints() :

		point = graph.GetPoint(i)

		assert type(point) == Point

		if len(point.attachedLines) != 2 :
			i += 1
			continue


		angle = point.GetAngleBetweenAttachedLines(0, 1)

		if angle < angleThreshold :

			line1 = point.attachedLines[0]
			line2 = point.attachedLines[1]

			oppositePoint1 = line1.GetOppositePoint(point)
			oppositePoint2 = line2.GetOppositePoint(point)
			
			if len(oppositePoint2.attachedLines) == 1 :
				graph.RemoveLine(line2)
				#graph.RemovePoint(oppositePoint2)
			elif len(oppositePoint1.attachedLines) == 1 :
				graph.RemoveLine(line1)
				#graph.RemovePoint(oppositePoint1)
			else :
				graph.RemoveLine(line2)

		i += 1


""" Merge connected lines that goes about in the same direction """
def MergeByAngle(graph, angleThreshold = 0.1) :

	assert type(graph) == Graph

	i = 0
	while i < graph.GetLenPoints() :

		point = graph.GetPoint(i)

		if len(point.attachedLines) != 2 :
			i += 1
			continue

		line1 = point.attachedLines[0]
		line2 = point.attachedLines[1]


		if point.GetAngleBetweenAttachedLines(0, 1) >= 180 - angleThreshold :
			print("angular merge")

			print(f"{line1.point1} - {line1.point2} and {line2.point1} - {line2.point2}")
			oppositePoint1 = line1.GetOppositePoint(point)
			oppositePoint2 = line2.GetOppositePoint(point)
			
			graph.RemoveLine(line1)
			graph.RemoveLine(line2)

			graph.NewLine(oppositePoint1, oppositePoint2)

			graph.RemovePoint(point)

			continue

		i += 1

	return graph




""" Remove all line segments that are outside the length limits """
def DeleteSegmentsByLength(graph, minLength = 10, maxLength = 1000) :
	assert type(graph) == Graph

	i = 0
	while i < graph.GetLenLines() :
		
		line = graph.GetLine(i)

		assert type(line) == Line


		if line.length < minLength or line.length > maxLength :

			graph.RemoveLineAt(i)

			continue

		i += 1


""" if two lines are colinear enough, and have free ends, join them """
def BridgeGaps(graph, directionThreshold = 0.1, offsetThreshold = 5) :
	assert type(graph) == Graph

	i = 0
	while i < graph.GetLenLines() - 1 :
		
		line = graph.GetLine(i)

		assert type(line) == Line

		if len(line.point1.attachedLines) > 1 and len(line.point2.attachedLines) > 1 :
			i += 1
			continue


		for j in range(i + 1, graph.GetLenLines()) :
			
			secondLine = graph.GetLine(j)

			assert type(secondLine) == Line

			if AreLineColinear(line, secondLine, directionThreshold, offsetThreshold) :

				point1, point2 = GetClosestPointsOfLines(line, secondLine)

				if len(point1.attachedLines) > 1 or len(point2.attachedLines) > 1 :
					continue

				graph.NewLine(point1, point2)

				""" if we cannot connected anything more to our line we stop """
				if len(line.point1.attachedLines) > 1 and len(line.point2.attachedLines) > 1 :
					break

				continue

				""" extends the second line """
				otherPoint = secondLine.GetOppositePoint(point2)

				secondLine.DetachFromPoints()
				secondLine.AttachToPoints(otherPoint, point1)

				
		
		i += 1


# causes counfounded lines
def MergePointsByDistance(graph, threshold = 5) :
	
	assert type(graph) == Graph

	print(f"there are {graph.GetLenPoints()} points in the graph")

	i = 0
	while i < graph.GetLenPoints() - 1 :

		j = i + 1

		point1 = graph.GetPoint(i)
		assert type(point1) == Point

		while j < graph.GetLenPoints() :

			point2 = graph.GetPoint(j)
			assert type(point2) == Point

			if DistanceBetweenPoints(point1, point2) < threshold :

				# create a new point at the median point between the points
				#print(f"point distance merge")
				newPoint = Point((point1.x + point2.x) // 2, (point1.y + point2.y) // 2)
				graph.AddPoint(newPoint)

				# the points that are already connected to the new point, allows to avoid duplicates
				connected_points = []

				while len(point1.attachedLines) != 0 :
					line = point1.attachedLines[0]
					other = line.GetOppositePoint(point1)

					# verify it is not a line that was connecting the two points tagother, if yes it gets deleted
					if (other == point2) :
						graph.RemoveLine(line)
						continue

					# each line attached to a point should be unique so no need to check for duplicated
					connected_points.append(other)
					line.DetachFromPoints()
					line.AttachToPoints(newPoint, other)
				
				while len(point2.attachedLines) != 0 :
					line = point2.attachedLines[0]
					other = line.GetOppositePoint(point2)
					
					# verify an identical line was not created from the merging of point1 already
					if other not in connected_points :
						line.DetachFromPoints()
						line.AttachToPoints(newPoint, other)
					else :
						graph.RemoveLine(line)
				
				graph.RemovePoint(point1)
				graph.RemovePoint(point2)

				

				i -= 1 # prevents i from incrementing but cancelling the +1
				break # next main line
			
			j += 1
		
		i += 1
	
	print(f"there are {graph.GetLenPoints()} points in the graph after distance merge")



# ptsPerAngleDiff is in points per degree, and the lines with the lowest score are considered the best
def FindBestParallelLine(graph : Graph, line : Line, idealPerpendicularDistance = 15, ptsPerLengthDiff = 1, ptsPerAngleDiff = 1, ptsPerDistanceDiff = 1) :

	bestScore = math.inf
	bestLine = None
	for i in range(graph.GetLenLines()) :

		otherLine = graph.GetLine(i)

		if line == otherLine :
			continue

		score = 0

		perpendicularDistance = line.GetElevation() - otherLine.GetElevation()

		score += abs(perpendicularDistance) * ptsPerDistanceDiff

		score += abs(line.length - otherLine.length) * ptsPerLengthDiff

		score += (abs(line.angle - otherLine.angle) * 180 / math.pi) * ptsPerAngleDiff

		if score < bestScore :
			bestLine = otherLine
			bestScore = score
	
	return bestLine, bestScore





def CleanUnusedPoints(graph : Graph) :

	i = 0
	while i < graph.GetLenPoints() :

		if len(graph.GetPoint(i).attachedLines) == 0 :
			graph.RemovePointAt(i)
			continue

		i += 1
	







"""
DEBUG FUNCTIONS
"""

# check if there exist lines that are connected to the exact same points
def CheckForDuplicateLines(graph : Graph) :

	assert type(graph) == Graph

	found = False

	i = 0
	while i < graph.GetLenLines() - 1 :
		
		line1 = graph.GetLine(i)

		assert type(line1) == Line

		if not line1.attached :
			print(f"found not attached line : {line1}")
			i += 1
			continue

		for j in range(i + 1, graph.GetLenLines()) :

			line2 = graph.GetLine(j)

			assert type(line2) == Line

			if not line1.attached :
				print(f"found not attached line : {line2}")
				j += 1
				continue

			if (line2.point1 == line1.point1 and line2.point2 == line1.point2) or (line2.point1 == line1.point2 and line2.point2 == line1.point1) :
				print(f"found identical lines in the graph : {line1} and {line2}")
				found = True
			
			j += 1
		
		i += 1
	
	if found :
		raise ValueError("THERE ARE DUPLICATE LINES IN THE GRAPH")
	else :
		print("no duplicate lines found in the graph")
