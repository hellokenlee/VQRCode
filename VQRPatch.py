# -*- coding: utf-8 -*-
__author__="KenLee"

#	Libraries
import pickle
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
		if(self.Img!=None):
			print("[VQRPatch] Resize to %sx%s" %(length,length))
			self.Img=self.Img.resize((length,length))
		pass

	#	保存到文件
	def saveImage(self,filepath):
		if(self.Img!=None):
			print("[VQRPatch] Save Image to %s" %(filepath))
			self.Img.save(filepath)
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
			return bStr[-5]

def main():
	print(VQRPatch.getCenterColor(16))
	print(VQRPatch.getReliability(495))
	li=[
		[5,128,470],
		[511,320,0],
		[111,112,113]
	]
	#li=[[11]]
	vp=VQRPatch(li)
	vp.makeImage()
	vp.resizeImage(270)
	vp.saveImage("./res/patch.png")
	pass

def genAllPatches():
	for i in range(512):
		li=[[i]]
		vp=VQRPatch(li)
		vp.makeImage()
		vp.resizeImage(90)
		vp.saveImage("./patches/"+str(i)+".png")
	pass

if __name__=="__main__":
	main()
