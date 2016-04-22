# -*- coding: utf-8 -*-	
__author__="KenLee"

#	Libiaries
import numpy as np
import ssim
import pickle
import maxflow

from maxflow import fastmin
from VQRImage import VQRImage
from VQRData import VQRData
from VQRPatch import VQRPatch
from PIL import Image
from math import exp


##	VQRCode 类	##
#data:
#	VQRImage vimg;
#	VQRData vdt;
#	
class VQRCode(object):
	pSSIMMap=None
	#	构造函数
	def __init__(self, text, imagePath, qrVersion=5):
		print("[VQRCode] Initializing...")
		self.Vimg = VQRImage(imagePath)
		self.Vdat = VQRData(text,qrVersion)
		#边长n
		self.Length = self.Vdat.Length
		self.Beta=10
		self.Lamda=0.3
		self.Wsmooth=0.2
		#生成半色调
		self.Vimg.cvHalftone()
		#self.Vimg.setHalftoneImage("./res/starbucks-cv-ht.png")
		#生成Imp图
		self.Vimg.cvImpMap()
		#self.Vimg.setImportanceImage("./res/starbucks-cv-imp.png")
		#根据imp图生成权重图(n*n)
		self.weightsMap=self.Vimg.genWeightsMap(self.Length)
		#根据半色调图生成patch中心颜色图(n*n)
		self.centerColorMap=self.Vimg.genCenterColorMap(self.Length)
		#加载Patches的相似性矩阵
		if VQRCode.pSSIMMap==None:
			f=open("./SSIMVal.dat","rb")
			VQRCode.pSSIMMap=pickle.load(f)
			f.close()
		self.Vimg.save()
		pass

	#	[DEBUG USE]保存权重图（aka Wmi in paper）成图像文件
	def saveWMapsAsImage(self,filepath):
		wimg=Image.new("L",(self.Length,self.Length))
		for r in range(self.Length):
			for c in range(self.Length):
				pixel=int(self.weightsMap[r][c]*255)
				wimg.putpixel((c,r),pixel)
		wimg.save(filepath)
		pass

	#	[DEBUG USE]保中心颜色图（aka Cmi in paper）成图像文件
	def saveCCMapAsImage(self,filepath):
		ccimg=Image.new("1",(self.Length,self.Length))
		for r in range(self.Length):
			for c in range(self.Length):
					if self.centerColorMap[r][c]==1:
						#black
						ccimg.putpixel((c,r),0)
					else:
						#white
						ccimg.putpixel((c,r),255)
		ccimg.save(filepath)
		pass

	#	给定一个Patch组P'，算出他的可靠性能量值ER(P')；假设二维码是n×n个modules，那么patch的长度就是(n×n)
	def reliabilityEneryCalc(self,vPatch):
		#	长度检查
		if vPatch.Length!=self.Vdat.Length:
			print("[ERROR] In ReliabilityEnery Calculation: Patches' sizes don't match QRCode's size!")
			return -1
		ER=0
		for r in range(vPatch.Length):
			for c in range(vPatch.Length):
				R=0
				if self.centerColorMap[r][c]==VQRPatch.getCenterColor(vPatch.Mat[r][c]):
					R=VQRPatch.getReliability(vPatch.Mat[r][c])
				expw=exp(-self.weightsMap[r][c])
				ER=ER+expw*(1.0-R)
		return ER

	#	给定一个Patch组P‘， 算出他的相似性能量值EG(P')；
	def regularizationEneryCalc(self,vPatch):
		EG=0
		pass

	#	给定一个Patches组P'，算出他的惩罚能量值EC(P')
	def penalizationEneryCalc(self,vPatch):
		EC=0
		for r in range(self.Length):
			for c in range(self.Length):
				R=0
				if self.centerColorMap[r][c]==VQRPatch.getCenterColor(vPatch.Mat[r][c]):
					R=1
				EC=EC+self.Beta*R
		return EC
	
	#	图割算法最小化能量
	def graphCutOptimaze(self):
		#	初始化D
		print("[VQRCode] GCO: Initializing D Matrix...")
		D= np.zeros((self.Length, self.Length, 512))
		for l in range(512):
			for r in range(self.Length):
				for c in range(self.Length):
					#对第r行c列的patch赋予标签l的unary cost
					##可靠性 ER
					ER=0.0
					if self.centerColorMap[r][c]==VQRPatch.getCenterColor(l):
						ER=VQRPatch.getReliability(l)
					ER=1.0-ER
					ER=ER*exp(-self.weightsMap[r][c])
					##相似性 EG
					#
					startX=c*3
					startY=r*3
					binStr=""
					for y in range(3):
						for x in range(3):
							if self.Vimg.HalftoneImg.getpixel((startX+x,startY+y))==0:
								#black
								binStr=binStr+'1'
							else:
								#white
								binStr=binStr+'0'
					sn=int(binStr,2)
					EG=VQRCode.pSSIMMap[sn][l]
					##惩罚性
					EC=0
					if self.centerColorMap[r][c]!=VQRPatch.getCenterColor(l):
						EC=1
					EC=EC*self.Beta
					
					D[r][c][l]=self.Lamda*ER+EG+EC
					print("ER=%s   EG=%s   EC=%s   D=%s" %(ER,EG,EC,D[r][c][l]) )
		#	初始化V
		print("[VQRCode] GCO: Initializing V Matrix...")
		V=np.zeros((512,512))
		for r in range(512):
			for c in range(512):
				V[r][c]=self.Wsmooth * VQRCode.pSSIMMap[r][c]
		#	solve
		print("[VQRCode] Running Graph Cut for D=(%sx%sx%s) V=(%sx%s)" %(D.shape[0],D.shape[1],D.shape[2],V.shape[0],V.shape[1]))
		res =fastmin.aexpansion_grid(D,V)
		print(res.tolist())
		return res.tolist()
		pass

	#	朴素算法求相似Patch(不保证可靠性)
	def trivalOptimaze(self):
		modules=self.Vdat.CodeMat
		pMat=[]
		for r in range(self.Length):
			row=[]
			for c in range(self.Length):
				#计算半色调图中的Patch序号
				startX=c*3
				startY=r*3
				bStr=""
				for y in range(3):
					for x in range(3):
						pixel=self.Vimg.HalftoneImg.getpixel((startX+x,startY+y))
						if pixel==255:
							#white
							bStr=bStr+'0'
						else:
							#black
							bStr=bStr+'1'
				sn=int(bStr,2)
				ssimMax=0
				snMax=0
				for i in range(512):
					if VQRPatch.getCenterColor(i)==int(self.Vdat.CodeMat[r][c]):
						if ssimMax<VQRCode.pSSIMMap[sn][i]:
							snMax=i
							ssimMax=VQRCode.pSSIMMap[sn][i]
				#print("ssimMax=%s  sn=%s snMax=%s codeM=%s sncc=%s" %(ssimMax, sn,snMax,self.Vdat.CodeMat[r][c],VQRPatch.getCenterColor(snMax)))
				#根据Imp map优化
				if r<6 or c <6 or r>self.Length-6 or c>self.Length-6:
					if r<1 or self.weightsMap[r-1][c]==0:
						if r>self.Length-2 or self.weightsMap[r+1][c]==0:
							if c<1 or self.weightsMap[r][c-1]==0:
								if c>self.Length-2 or self.weightsMap[r][c+1]==0:
									if self.Vdat.CodeMat[r][c]==1:
										snMax=511
									if self.Vdat.CodeMat[r][c]==0:
										snMax=0
				row.append(snMax)
			pMat.append(row)
		return pMat
	
	# 
	def saveQRImage(self,filepath):
		self.Vdat.saveImage(filepath)
		pass

def main():
	vc=VQRCode("http://www.sysu.edu.cn/","./pics/lena.jpg",6)
	vc.saveQRImage("./res/Hqr.png")
	vpli=vc.trivalOptimaze()
	#vpli=vc.graphCutOptimaze()
	vp = VQRPatch(vpli)
	vp.saveImage("./res/Hvqr-temp.png")
	vp.addQRModules(vc.Vdat)
	vp.makeImage()
	vp.resizeImage(vp.Length*3*3)
	vp.saveImage("./res/Hvqr.png")


	pass

if __name__=="__main__":
	main()
