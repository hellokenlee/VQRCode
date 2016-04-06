# -*- coding: utf-8 -*-	
__author__="KenLee"

#	Libiaries
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
	#	构造函数
	def __init__(self, text, imagePath, qrVersion=5):
		print("[VQRCode] Initializing...")
		self.Vimg = VQRImage(imagePath)
		self.Vdat = VQRData(text,qrVersion)
		#边长n
		self.Length = self.Vdat.Length
		self.Beta=100
		self.Wsmooth=0.2
		#生成半色调图
		#self.Vimg.cvHalftone()
		self.Vimg.setHalftoneImage("./res/baby-cv-ht.png")
		#生成Imp图
		#self.Vimg.cvImpMap()
		self.Vimg.setImportanceImage("./res/baby-cv-imp.png")
		#根据imp图生成权重图(n*n)
		self.weightsMap=self.Vimg.genWeightsMap(self.Length)
		#根据半色调图生成patch中心颜色图(n*n)
		self.centerColorMap=self.Vimg.genCenterColorMap(self.Length)

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
		for r in vPatch.Length:
			for c in vPatch.Length:
				R=0
				if self.centerColorMap[r][c]==VQRPatch.getCenterColor(vPatch.Mat[r][c]):
					R=VQRPatch.getReliability(vPatch.Mat[r][c])
				expw=exp(-self.weightsMap[r][c])
				ER=ER+expw*(1.0-R)
		return ER

	#	给定一个Patch组P‘， 算出他的相似性能量值EG(P')；
	def regularizationEneryCalc(self):
		pass

	def penalizationEneryCalc(self):
		pass
	def graphCutOptimaze(self):
		pass

	def trivalOptimaze(self):
		pass

def main():
	vc=VQRCode("hellokenlee","./pics/baby.png")
	# print("weightsMap:")
	# for line in vc.weightsMap:
	# 	print(line)
	# print("CCMap:")
	# for line in vc.centerColorMap:
	# 	print(line)
	vc.saveWMapsAsImage("./res/bwmap.png")
	vc.saveCCMapAsImage("./res/ccmap.png")

	pass

if __name__=="__main__":
	main()
