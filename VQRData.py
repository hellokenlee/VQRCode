# -*- coding: utf-8 -*-
__author__="KenLee"

#	libraries
import qrcode
from PIL import Image


##	VQRData类 	##
# data:
#	string Text;
#	constant ECL;
#	int Version;
#	int Length;
#	QRCode QR;
# 	Image QRImg;
#	list<list> CodeMat;
class VQRData(object):
	#	初始化
	def __init__(self, text, version=3, ecl=qrcode.constants.ERROR_CORRECT_L):
		self.Text=text
		self.Version=version
		self.ECL=ecl
		self.QR=qrcode.QRCode(
			version=self.Version,
			error_correction=self.ECL,
			box_size=3,
			border=0
		)
		self.QR.add_data(self.Text)
		self.QR.make()
		self.CodeMat=self.QR.get_matrix()
		self.Length=len(self.CodeMat)
		self.QRimg= self.QR.make_image()
		pass

	#	设置文字
	def setText(self,text):
		self.QR.clear()
		self.Text=text
		self.QR.add_data(self.Text)
		self.QR.make()
		self.CodeMat=self.QR.get_matrix()
		self.QRimg= self.QR.make_image()
		pass

	#	设置版本aka. QR矩阵大小
	def setVersion(self,ver):
		self.Version=ver
		self.QR=qrcode.QRCode(
			version=self.Version,
			error_correction=self.ECL,
			box_size=10,
			border=0
		)
		self.QR.add_data(self.Text)
		self.QR.make()
		self.CodeMat=self.QR.get_matrix()
		self.Length=len(self.CodeMat)
		self.QRimg= self.QR.make_image()
		pass

	#	设置误差改正级别
	def setErrorCorrectionLevel(ecl):
		self.ECL=ecl
		self.QR=qrcode.QRCode(
			version=self.Version,
			error_correction=self.ECL,
			box_size=9,
			border=0
		)
		self.QR.add_data(self.Text)
		self.QR.make()
		self.CodeMat=self.QR.get_matrix()
		self.QRimg= self.QR.make_image()
		pass

	#	保存二维码到指定文件
	def save(self,filePath):
		print("[VQRData] Saving QRCode Image to %s" %(filePath))
		self.QRimg.save(filePath)
		pass


def test():
	qrd=VQRData("HelloKenLee!",5)
	print(qrd.Length)
	qrd.CodeMat[0][0]=False
	qrd.save("./res/qrd.png")
	
	pass

if __name__=="__main__":
	test()
