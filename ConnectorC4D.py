"""
2015 gupon.jp

Connector for C4D Python Generator  
"""

import c4d, math, itertools, random
from c4d.modules import mograph as mo

#userdata id
ID_SPLINE_TYPE = 2
ID_SPLINE_CLOSED = 4
ID_SPLINE_INTERPOLATION = 5
ID_SPLINE_SUB = 6
ID_SPLINE_ANGLE = 8
ID_SPLINE_MAXIMUMLENGTH = 9
ID_USE_SCREEN_DIST = 10	

ID_USE_MAXSEG = 15
ID_MAXSEG_NUM = 13

ID_USE_CENTER = 19
ID_CENTER_OBJ = 18


class Point:
	def __init__(self, p):
		self.world = p
		self.screen = c4d.Vector(0)
	
	def calc2D(self, bd):
		self.screen = bd.WS(self.world)
		self.screen.z = 0

class PointGroup:
	def __init__(self):
		self.points = []
	
	def AddPoint(self, point):
		self.points.append(Point(point))
	 
	def Make2DPoints(self):
		bd = doc.GetRenderBaseDraw()
		for point in self.points:
			point.calc2D(bd) 
	
	def MakeCombsWith(self, target):
		combs = []
		for pA in self.points:
			for pB in target.points:
				combs.append([pA, pB])
		return combs
	
	def MakeCombsInOrder(self):
		combs = []
		for i,pA in enumerate(self.points):
			if i == len(self.points)-1:
				combs.append([pA, self.points[0]])
			else:
				combs.append([pA, self.points[i+1]])
		return combs
	
	def GetPoint(self, index):
		return self.points[index]
	
	def GetAllPoints(self):
		return self.points
	
	def GetNumPoints(self):
		return len(self.points)
		

def SetSplineGUI():
	UD = op.GetUserDataContainer()
	intermediatePoints = op[c4d.ID_USERDATA, ID_SPLINE_INTERPOLATION]
	for id, bc in UD:
		if id[1].id == ID_SPLINE_SUB:
			if intermediatePoints == c4d.SPLINEOBJECT_INTERPOLATION_NATURAL \
			or intermediatePoints == c4d.SPLINEOBJECT_INTERPOLATION_UNIFORM:
				bc[c4d.DESC_HIDE] = False
			else:
				bc[c4d.DESC_HIDE] = True
		
		if id[1].id == ID_SPLINE_ANGLE:
			if intermediatePoints == c4d.SPLINEOBJECT_INTERPOLATION_ADAPTIVE \
			or intermediatePoints == c4d.SPLINEOBJECT_INTERPOLATION_SUBDIV:
				bc[c4d.DESC_HIDE] = False
			else:
				bc[c4d.DESC_HIDE] = True
		
		if id[1].id == ID_SPLINE_MAXIMUMLENGTH:
			if intermediatePoints == c4d.SPLINEOBJECT_INTERPOLATION_SUBDIV:
				bc[c4d.DESC_HIDE] = False
			else:
				bc[c4d.DESC_HIDE] = True
		
		
		if id[1].id == ID_MAXSEG_NUM:
			bc[c4d.DESC_HIDE] = not op[c4d.ID_USERDATA, ID_USE_MAXSEG]
		
		if id[1].id == ID_CENTER_OBJ:
			bc[c4d.DESC_HIDE] = not op[c4d.ID_USERDATA, ID_USE_CENTER]
		
		op.SetUserDataContainer(id, bc)

def SetSplineAttributes(obj):
	obj[c4d.SPLINEOBJECT_TYPE] = op[c4d.ID_USERDATA, ID_SPLINE_TYPE]
	obj[c4d.SPLINEOBJECT_CLOSED] = op[c4d.ID_USERDATA, ID_SPLINE_CLOSED]
	obj[c4d.SPLINEOBJECT_INTERPOLATION] = op[c4d.ID_USERDATA, ID_SPLINE_INTERPOLATION]
	obj[c4d.SPLINEOBJECT_SUB] = op[c4d.ID_USERDATA, ID_SPLINE_SUB]
	obj[c4d.SPLINEOBJECT_ANGLE] = op[c4d.ID_USERDATA, ID_SPLINE_ANGLE]
	obj[c4d.SPLINEOBJECT_MAXIMUMLENGTH] = op[c4d.ID_USERDATA, ID_SPLINE_MAXIMUMLENGTH]
	obj.Message(c4d.MSG_UPDATE)


def GetPointsFromObjects(targetList):
	step = op[c4d.ID_USERDATA, 12]
	# add every points to list
	pointGroups = []
	baseMg = op.GetMg()
	for target in targetList:
		if target != None :
			group = PointGroup()
			moData = mo.GeGetMoData(target)
			if moData==None:
				group.AddPoint(target.GetMg().off * ~baseMg)
			else:
				if not moData.GetCount():
					continue
				moList = moData.GetArray(c4d.MODATA_MATRIX)
				clonerMg =  target.GetMg()
				for i,data in enumerate(moList):
					if i % step == 0:
						group.AddPoint(data.off * clonerMg * ~baseMg)
					
			pointGroups.append(group)
					
	return pointGroups
	

def SetCombinations(pointGroups, obj):
	bd = doc.GetRenderBaseDraw()
	maxDist = op[c4d.ID_USERDATA, 1]
	excludeSame = op[c4d.ID_USERDATA, 11]
	maxSegNum = op[c4d.ID_USERDATA, 13]
	useMaxSeg = op[c4d.ID_USERDATA, 15]
	useCenter = op[c4d.ID_USERDATA, ID_USE_CENTER]
	
	useScreenDist = op[c4d.ID_USERDATA, 10]
	if useScreenDist:
		for group in pointGroups:
			group.Make2DPoints()
		
		frame = bd.GetSafeFrame()
		baseLength = frame["cr"] - frame["cl"]
		maxDist = baseLength * maxDist/1000
	
	_combs = []
	inOrder = False
#	if inOrder:
#		for group in pointGroups:
#			_combs = _combs + group.MakeCombsInOrder()
	
	if useCenter:
		target = op[c4d.ID_USERDATA, ID_CENTER_OBJ]
		if target:
			pA = Point(target.GetMg().off * ~op.GetMg())
			
			for group in pointGroups:
				for pB in group.GetAllPoints():
					_combs.append([pA, pB])
		else:
			print "no target found"
			return
	
	else:
		if excludeSame:
			numGroups = len(pointGroups)
			for i in range(numGroups-1):
				groupA = pointGroups[i]
				for j in range(i+1, numGroups):
					groupB = pointGroups[j]
					_combs = _combs + groupA.MakeCombsWith(groupB)
		else:
			allPoints = []
			for group in pointGroups:
				allPoints = allPoints + group.GetAllPoints()
			
			numPoints = len(allPoints)
			for i in range(numPoints-1):
				for j in range(i+1, numPoints):
					_combs.append([allPoints[i], allPoints[j]])
	
	combs = []
	for comb in _combs:
		v0 = comb[0].screen if useScreenDist else comb[0].world
		v1 = comb[1].screen if useScreenDist else comb[1].world
		
		if c4d.Vector(v1 - v0).GetLength() < maxDist:
			combs.append(comb)
	
	random.shuffle(combs)
	obj.ResizeObject(len(combs) * 2)
	
	for i, comb in enumerate(combs):
		a = comb[0].world
		b = comb[1].world
		
		addP = True
		if useMaxSeg:
			if maxSegNum:
				acnt = 0
				bcnt = 0
				
				for p in obj.GetAllPoints():
					if p == a: acnt += 1
					if p == b: bcnt += 1
					if acnt >= maxSegNum or bcnt >= maxSegNum:
						addP = False
						break
			else:
				addP = False
			
		
		if addP:
			obj.SetPoint(i * 2 + 0, a)
			obj.SetPoint(i * 2 + 1, b)
	
	obj.MakeVariableTag(c4d.Tsegment, len(combs))
	
	for i in range(len(combs)):
		obj.SetSegment(i, 2, False)


def main():
	random.seed(100)
	obj = c4d.BaseObject(c4d.Ospline)
	
	targetListData = op[c4d.ID_USERDATA, 3]
	numTargets = targetListData.GetObjectCount()
	
	if numTargets < 1:
		return obj
	
	targetList = []
	for i in range(numTargets):
		targetList.append(targetListData.ObjectFromIndex(doc, i))
	
	pointGroups = GetPointsFromObjects(targetList)
	
	if len(pointGroups) < 1:
		return obj
	
	SetCombinations(pointGroups, obj)
	
	SetSplineGUI()
	SetSplineAttributes(obj)
	
	return obj