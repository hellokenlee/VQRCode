# -*- coding: utf-8 -*-
__author__="KenLee"

#	Libraries
import pickle
import ssim

from PIL import Image
from math import sqrt

##	VQRPatch 类	##
#
#
class VQRPatch(object):
	#使用一个int来表示编号为0~511的patch
	#其中这个int的二进制编码(0b876543210)则为对应的9个位置的黑白颜色
	#	[8] [7] [6]
	#	[5] [4] [3]
	#	[2] [1] [0]
	#其中白色是0，黑色是1
	#所以：0(0b000000000)~511(0b111111111)表示
	#	|   |		|███|
	#	|   |	~	|███|	（全白～全黑）
	#	|   | 		|███|
	#   比如：
	#	███
	#	█ █
	#	███ 对应的二进制为0b111101111=496 所以编号为495
	#维持一个二维矩阵存n×n个编号，组成一幅细分后的二维码图


	#	校准图案中心位置表(Alignment Pattern Locations Table)
	#From http://www.thonky.com/qr-code-tutorial/alignment-pattern-locations
	APLT=[
		[],						#version 0
		[],				
		[6,18],
		[6,22],
		[6,26],
		[6,30],					#version 5
		[6,34],
		[6,22,38],
		[6,24,42],
		[6,26,46],
		[6,28,50],				#version 10
		[6,30,54],
		[6,32,58],
		[6,34,62],
		[6,26,46,66],
		[6,26,48,70],			#version 15
		[6,26,50,74],
		[6,30,54,78],
		[6,30,56,82],
		[6,30,58,86],
		[6,34,62,90],			#version 20
		[6,28,50,72,94],
		[6,26,50,74,98],
		[6,30,54,78,102],
		[6,28,54,80,106],
		[6,32,58,84,110],		#version 25
		[6,30,58,86,114],
		[6,34,62,90,118],
		[6,26,50,74,98,122],
		[6,30,54,78,102,126],
		[6,26,52,78,104,130],	#version 30
		[6,30,56,82,108,134],
		[6,34,60,86,112,138],
		[6,30,58,86,114,142],
		[6,34,62,90,118,146],
		[6,30,54,78,102,126,150],#version 35
		[6,24,50,76,102,128,154],
		[6,28,54,80,106,132,158],
		[6,32,58,84,110,136,162],
		[6,26,54,82,110,138,166],
		[6,30,58,86,114,142,170],#version 40
	]	
	Rval=None
	#	构造函数
	def __init__(self,mat=None):
		self.Length=0
		self.Img=None
		self.Mat=mat
		if mat!=None:
			self.setMat(mat)
		pass

	#	设置编号二维矩阵
	def setMat(self, mat):
		#	计算边长
		self.Length=len(mat)
		self.Mat=mat
		self.Img=None
		pass

	#	生成图像
	def makeImage(self):
		#图片对象
		self.Img=Image.new("1",(self.Length*3,self.Length*3))

		for r in range(self.Length):
			#对于每一行编号处理
			for c in range(self.Length):
				#对于每一个编号处理
				sn=self.Mat[r][c]
				if(sn>511):
					print("[Error] In VQRPatch: Serial Number List Overflow!")
					return -1
				bStr=bin(sn)[2:]
				#补全9位
				while len(bStr)<9:
					bStr='0'+bStr
				#写入像素数据
				startPointX=c*3
				startPointY=r*3
				bIndex=0
				for y in range(3):
					for x in range(3):
						if bStr[bIndex]=='0':
							#white
							self.Img.putpixel((startPointX+x,startPointY+y),1)
						else:
							#black
							self.Img.putpixel((startPointX+x,startPointY+y),0)
						bIndex=bIndex+1
		pass

	def resizeImage(self,length):
		if self.Img==None:
			self.makeImage()
		print("[VQRPatch] Resize to %sx%s" %(length,length))
		self.Img=self.Img.resize((length,length))
		pass

	#	保存到文件
	def saveImage(self,filepath):
		if self.Img==None:
			self.makeImage()
		print("[VQRPatch] Save Image to %s" %(filepath))
		self.Img.save(filepath)
		pass

	def addQRModules(self,Vdat):
		modules=Vdat.CodeMat
		##	增加位置探测图形(Position Detection Pattern)	##
		#左上角
		startPointR=0
		startPointC=0
		for r in range(8):
			for c in range(8):
				if modules[startPointR+r][startPointC+c]==1:
					#black
					self.Mat[startPointR+r][startPointC+c]=511
				else:
					#white
					self.Mat[startPointR+r][startPointC+c]=0
		#右上角
		startPointR=0
		startPointC=self.Length-1
		for r in range(8):
			for c in range(8):
				if modules[startPointR+r][startPointC-c]==1:
					#black
					self.Mat[startPointR+r][startPointC-c]=511
				else:
					#white
					self.Mat[startPointR+r][startPointC-c]=0
		#左下角
		startPointR=self.Length-1
		startPointC=0
		for r in range(8):
			for c in range(8):
				if modules[startPointR-r][startPointC+c]==1:
					#black
					self.Mat[startPointR-r][startPointC+c]=511
				else:
					#white
					self.Mat[startPointR-r][startPointC+c]=0


		##	增加对齐图形(Timing Pattern)	##
		r=6
		for c in range(self.Length):
			if modules[r][c]==1:
				#black
				self.Mat[r][c]=511
			else:
				#white
				self.Mat[r][c]=0
		c=6
		for r in range(self.Length):
			if modules[r][c]==1:
				#black
				self.Mat[r][c]=511
			else:
				#white
				self.Mat[r][c]=0
		##	增加校准图形(Alignment Patterns)	##
		v=Vdat.Version
		APL=VQRPatch.APLT[v]
		for centerR in APL:
			for centerC in APL:
				# foreach Alignment Patterns center(5*5)
				for r in range(-2,3):
					for c in range(-2,3):
						if modules[centerR+r][centerC+c]==1:
							#black
							self.Mat[centerR+r][centerC+c]=511
						else:
							#white
							self.Mat[centerR+r][centerC+c]=0
		##	格式信息(Formation Information)	##
		#左上
		r=8
		for c in range(9):
			if modules[r][c]==1:
				#black
				self.Mat[r][c]=511
			else:
				#white
				self.Mat[r][c]=0
		c=8
		for r in range(9):
			if modules[r][c]==1:
				#black
				self.Mat[r][c]=511
			else:
				#white
				self.Mat[r][c]=0
		#右上
		r=8
		for c in range(self.Length-8,self.Length):
			if modules[r][c]==1:
				#black
				self.Mat[r][c]=511
			else:
				#white
				self.Mat[r][c]=0
		#左下
		c=8
		for r in range(self.Length-8,self.Length):
			if modules[r][c]==1:
				#black
				self.Mat[r][c]=511
			else:
				#white
				self.Mat[r][c]=0

		##	版本信息(Version Information)	##
		#右上
		for r in range(0,7):
			for c in range(self.Length-11, self.Length-8):
				if modules[r][c]==1:
					#black
					self.Mat[r][c]=511
				else:
					#white
					self.Mat[r][c]=0
		#左下
		for r in range(self.Length-11,self.Length-8):
			for c in range(0,7):
				if modules[r][c]==1:
					#black
					self.Mat[r][c]=511
				else:
					#white
					self.Mat[r][c]=0
		pass

	#	静态方法，求一个编号为sn的patch的可靠性，即P={pi=(Ipi,Cpi,ri)|i=0..512}中的ri
	@staticmethod
	def getReliability(SerialNumber):
		if VQRPatch.Rval==None:
			#	first access, read database file
			f=open("./PatchReliability.dat","rb")
			VQRPatch.Rval= pickle.load(f)
			f.close()
			print("[VQRPatch] Done Loading Reliability Data")
		return VQRPatch.Rval[SerialNumber]
		pass

	#	静态方法，求一个知道sn的patch的中心方块颜色
	@staticmethod
	def getCenterColor(SerialNumber):
		bStr=bin(SerialNumber)[2:]
		if(len(bStr)<5):
			return 0
		else:
			return int(bStr[-5])



# 	生成所有521个Patches并保存为PNG图片【预处理使用】
def genAllPatches(dirpath,size):
	for i in range(512):
		li=[[i]]
		vp=VQRPatch(li)
		vp.makeImage()
		vp.resizeImage(size)
		vp.saveImage(dirpath+str(i)+".png")
	pass

def genPatchesSSIM():
	size=512
	ssimMap=[]
	genAllPatches("./patches/",3)
	for i in range(size):
		imA=Image.open("./patches/"+str(i)+".png")
		row=[]
		for j in range(size):
			imB=Image.open("./patches/"+str(j)+".png")
			simVal=ssim.compute_ssim(imA,imB)
			print("(%s %s): %s" %(i,j,simVal))
			row.append(simVal)
		ssimMap.append(row)

	f=open("./PatchSSIM.dat","wb")
	pickle.dump(ssimMap,f)
	f.close()
	pass

def main():
	# genPatchesSSIM()
	pass

if __name__=="__main__":
	main()
