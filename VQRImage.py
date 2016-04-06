# -*- coding: utf-8 -*-
__author__="KenLee"

#	libraries
from PIL import Image
from PIL import ImageOps
from PIL import ImageFilter
import os

##	VQRImage类 	##
# data:
#	string FilePath;
#	Image RGBImage;
#	Image HalftoneIamge;
#	Image ImportanceImage;
class VQRImage(object):
	#	构造函数
	def __init__(self, filepath=""):
		self.FilePath=filepath
		self.HalftoneImg=None
		self.RGBImg=None
		self.ImportanceImg=None
		if self.FilePath!="":
			print("[VQRImage] Set Image File as %s" %(self.FilePath))
			self.RGBImg=Image.open(self.FilePath)
		pass
	
	#	导入半色调图
	def setHalftoneImage(self,filepath):
		self.HalftoneImg=Image.open(filepath)
		pass

	#	导入Importance图
	def setImportanceImage(self,filepath):
		self.ImportanceImg=Image.open(filepath)
		pass

	#	重新指定文件路径
	def setImage(self,filepath):
		print("[VQRImage] Set Image File from %s" %(self.FilePath))
		self.FilePath=filepath
		self.RGBImg=Image.opne(FilePath)
		pass

	#	调整边长
	def resize(self,length):
		print("[VQRImage] Resize to %s x %s" %(length,length))
		self.RGBImg=self.crop2Square(self.RGBImg)
		self.RGBImg=self.RGBImg.resize((length,length))
		if(self.HalftoneImg!=None):
			self.HalftoneImg=self.crop2Square(self.HalftoneImg)
			self.HalftoneImg=self.HalftoneImg.resize((length,length))
		if(self.ImportanceImg!=None):
			self.ImportanceImg=self.crop2Square(self.ImportanceImg)
			self.ImportanceImg=self.ImportanceImg.resize((length,length))
		pass

	#	裁剪,取中心正方形
	def crop2Square(self,img):
		width=img.size[0]
		height=img.size[1]
		if width>height:
			left=int((width-height)/2)
			upper=0
			right=left+height
			lower=height
			box=(left, upper, right, lower)
			return img.crop(box)
		elif height>width:
			left=0
			upper=int((height-width)/2)
			right=width
			lower=upper+width
			box=(left, upper, right, lower)
			return img.crop(box)
		else:
			return img
		pass

	#	保存半色调图和importance图
	def save(self, HFfilepath="./res/hf.png",IMPfilepath="./res/imp.png"):
		if self.HalftoneImg!=None:
			print("[VQRImage] Save HFImage File to %s" %(HFfilepath))
			self.HalftoneImg.save(HFfilepath,"PNG")
		if self.ImportanceImg!=None:
			print("[VQRImage] Save IMPImage File to %s" %(IMPfilepath))
			self.ImportanceImg.save(IMPfilepath,"PNG")
		pass

	#	使用误差扩散半色调化(Floyod-Steinberg)
	def stdHalftone(self, threshold=0.5):
		print("[VQRImage] Processing Halftoning...")
		#	灰度化
		self.HalftoneImg=ImageOps.grayscale(self.RGBImg)
		#	误差分配规则 右 下 右下 左下
		#
		#       	*		7/16
		#	3/16	5/16	1/16
		#
		width=self.HalftoneImg.size[0]
		height=self.HalftoneImg.size[1]
		thresholdNum=threshold*255
		#	对每个像素进行操作
		for y in range(0,height):
			for x in range(0,width):
				oldpixel=self.HalftoneImg.getpixel((x,y))
				#	与阀值比较，二值化
				if oldpixel <thresholdNum:
					newpixel=0
				else:
					newpixel=255
				self.HalftoneImg.putpixel((x,y),newpixel)
				#	误差
				err=oldpixel-newpixel
				#print("(%s %s) %s %s %s" %(x,y,oldpixel,newpixel,err))
				#	右
				if x<width-1:
					self.HalftoneImg.putpixel((x+1,y),int(self.HalftoneImg.getpixel((x+1,y))+err*7/16))
				#	左下
				if x>0 and y<height-1:
					self.HalftoneImg.putpixel((x-1,y+1),int(self.HalftoneImg.getpixel((x-1,y+1))+err*3/16))
				#	下
				if y<height-1:
					self.HalftoneImg.putpixel((x,y+1),int(self.HalftoneImg.getpixel((x,y+1))+err*5/16))
				#	右下
				if x<width-1 and y<height-1:
					self.HalftoneImg.putpixel((x+1,y+1),int(self.HalftoneImg.getpixel((x+1,y+1))+err/16))
		self.HalftoneImg=self.HalftoneImg.filter(ImageFilter.MedianFilter(3))
		pass

	#	使用Structure-aware半调化(Jianghao Chang)
	def cvHalftone(self):
		print("[VQRImage] Processing Halftoning...")
		os.system("./cvHalftone %s %s" %(self.FilePath,"./res/hf-temp.png"))
		self.HalftoneImg=Image.open("./res/hf-temp.png")
		print("[VQRImage] Processing Halftoning(optimizing)...")
		#	中值滤波
		self.HalftoneImg=self.HalftoneImg.filter(ImageFilter.MedianFilter(3))
		pass

	#	生成Importance 图
	def stdImpMap(self):
		print("[VQRImage] Processing Importance map...")
		self.ImportanceImg= ImageOps.grayscale(self.RGBImg)
		self.ImportanceImg=	self.ImportanceImg.filter(ImageFilter.MedianFilter(3))
		self.ImportanceImg= self.ImportanceImg.filter(ImageFilter.CONTOUR)
		self.ImportanceImg= ImageOps.invert(self.ImportanceImg)
		pass

	#	使用Flowbased Image Abstruction(JE Kyprianidis)生成Importance图:
	def cvImpMap(self):
		print("[VQRImage] Processing Importance map...")
		os.system("./FbABS %s %s" % (self.FilePath, "./res/imp-temp.jpg"))
		self.ImportanceImg= Image.open("./res/imp-temp.jpg")
		self.ImportanceImg= ImageOps.invert(self.ImportanceImg)
		pass

	#	把半色调图片分成3*3的patch，访问第(x,y)个patch【aka Imi】
	#返回： 一个3*3的list，0表示白色，1表示黑色
	def halftonePatchAt(self,(x,y)):
		res=[]
		startPointX=x*3
		startPointY=y*3
		for r in range(3):
			row=[]
			htY=startPointY+r
			for c in range(3):
				htX=startPointX+c
				if self.getpixel((htX,htY))==255:
					#	是白色
					row.append(0)
				else:
					#	是黑色
					row.append(1)
			res.append(row)
		return res
	#	根据imp图生成权重图(n*n)
	def genWeightsMap(self,size):
		#	假设二维码是n×n的 那么我们把图片resize到3n×3n【即n×n个3*3的patch】
		self.resize(size*3)
		if self.ImportanceImg==None:
			print("[ERROR] Can't generate weights map due to lacking Importance Image")
			return -1
		wMap=[]
		for r in range(size):
			row=[]
			for c in range(size):
				w=0.0
				startPointX=c*3
				startPointY=r*3
				for y in range(3):
					for x in range(3):
						w=w+(self.ImportanceImg.getpixel((startPointX+x,startPointY+y))/255.0)
				w=w/9.0
				row.append(w)
			wMap.append(row)
		
		return wMap

	#	根据半色调图生成patch中心颜色图(n*n)
	def genCenterColorMap(self,size):
		#	假设二维码是n×n的 那么我们把图片resize到3n×3n【即n×n个3*3的patch】
		self.resize(size*3)
		if self.HalftoneImg==None:
			print("[ERROR] Can't generate center color map due to lacking Halftone Image")
			return -1
		ccMap=[]
		for r in range(size):
			row=[]
			for c in range(size):
				startPointX=c*3
				startPointY=r*3
				if self.HalftoneImg.getpixel((startPointX+1,startPointY+1))==0:
					#center of this patch is black
					row.append(1)
				else:
					#center of this patch is white
					row.append(0)
			ccMap.append(row)
		return ccMap

##	end of VQRImage类 	##

def test():

	vqrimg=VQRImage("./pics/nico.jpg")
	vqrimg.cvImpMap()
	vqrimg.save()
	pass


if __name__=="__main__":
	test()
