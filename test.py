# -*- coding: utf-8 -*-
__author__="KenLee"

from PIL import Image
from PIL import ImageOps
from PIL import ImageFilter
import pickle
import maxflow
#	裁剪成正方形
def cropMiddle(img):
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

#	缩放操作
def resize(img,width,height):
	size=(width,height)
	return img.resize(size)

#	误差扩散半色调化(Floyod-Steinberg)
def halftone(img, threshold):
	img=ImageOps.grayscale(img)
	#	误差分配规则 右 下 右下 左下
	#
	#       	*		7/16
	#	3/16	5/16	1/16
	#
	width=img.size[0]
	height=img.size[1]
	thresholdNum=threshold*255
	#	对每个像素进行操作
	for y in range(0,height):
		for x in range(0,width):
			oldpixel=img.getpixel((x,y))
			#	二值化
			if oldpixel <thresholdNum:
				newpixel=0
			else:
				newpixel=255
			#img.putpixel((x,y),newpixel)
			#	误差
			err=oldpixel-newpixel
			#print("(%s %s) %s %s %s" %(x,y,oldpixel,newpixel,err))
			#	右
			if x<width-1:
				img.putpixel((x+1,y),int(img.getpixel((x+1,y))+err*7/16))
			#	左下
			if x>0 and y<height-1:
				img.putpixel((x-1,y+1),int(img.getpixel((x-1,y+1))+err*3/16))
			#	下
			if y<height-1:
				img.putpixel((x,y+1),int(img.getpixel((x,y+1))+err*5/16))
			#	右下
			if x<width-1 and y<height-1:
				img.putpixel((x+1,y+1),int(img.getpixel((x+1,y+1))+err/16))
	return img


def opetimize(img):
	img=img.copy()
	width=img.size[0]
	height=img.size[1]
	offsetNear=[(-1,-1),(0,-1),(1,-1),  (-1,0),(1,0),  (-1,1),(0,1),(1,1)]
	#offsetBetween=[()]
	for y in range(2,height-2):
		for x in range(2,width-2):
			count=0
			for os in offsetNear:
				if img.getpixel((x+os[0],y+os[1])) !=0:
					count=count+1
			if(count>4):
				img.putpixel((x,y),255)
			else:
				img.putpixel((x,y),0)
	return img


class s(object):
	sd=[]
	counter=0
	"""docstring for s"""
	def __init__(self, arg):
		pass
	@staticmethod
	def printSd(i):
		while s.counter<=i:
			s.sd.append(s.counter)
			s.counter=s.counter+1
		print(s.sd[i])

def main():
	# im = Image.open("./pics/baby.png")
	# print(im.format, im.size, im.mode)
	# im=ImageOps.grayscale(im)
	# im=im.filter(ImageFilter.FIND_EDGES)
	# #im=im.filter(ImageFilter.EDGE_ENHANCE)
	# im.save("./res/filtered.png","PNG")
	# im=Image.new("L",(1,1))
	# print(im.putpixel((0,0),1))
	# im.save("./res/test.png")
	pf=open("./SSIMVal.dat","rb")
	mat=pickle.load(pf)
	pf.close()
	for 
	pass

if __name__=="__main__":
	main()
