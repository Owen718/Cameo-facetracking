import cv2
import numpy
import utils

def cv_show(name,img):
	cv2.imshow(name,img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()



#边缘检测优化方法 先对图像进行模糊处理，再转为为灰度彩色图像，再使用laplacian检测边缘。此方法可较好的避免将噪声错误地识别为边缘。
def strokeEdges(src,dst,blurKsize = 7,edgeKsize = 5):
	if blurKsize >=3:
		blurredSrc = cv2.medianBlur(numpy.array(src),blurKsize)
		graySrc = cv2.cvtColor(blurredSrc,cv2.COLOR_BGR2GRAY)
	else:
		graySrc = cv2.cvtColor(src,cv2.COLOR_BGR2GRAY)
	cv2.Laplacian(graySrc,cv2.CV_8U,graySrc,ksize = edgeKsize )
	#cv_show('binary',binary)
	normalizedInverseAlpha = (1.0 / 255) * (255 - graySrc)
	#cv_show('normalized',normalizedInverseAlpha)
	channels = cv2.split(src)
	for channel in channels:
		channel[:] = channel * normalizedInverseAlpha
		#cv_show('channel',channel)
	cv2.merge(channels,dst)




#一般的卷积滤波器方法
class VConvolutionFilter(object):
	#A filter that applies a convolution to V (or all of BGR)
	def __init__(self,kernel):
		self._kernel = kernel
	def apply(self,src,dst):
		#Apply the filter with a BGR or gray source /destination
		cv2.filter2D(src,-1,self._kernel,dst=dst)


#特定的锐化滤波器方法
class shapenFilter(VConvolutionFilter):
	#A shapen filter with a 1-pixel radius
	def __init__(self):
		kernel = numpy.array([
			[-1,-1,-1],
			[-1, 9,-1],
			[-1,-1,-1],
		])#若不想改变图像亮度，则权重加起来为1。若使权重和为0，则得到一个边缘检测核，把边缘转化为白色，把非边缘区域转为黑色，例如下面的FindEdgesFilter方法
		VConvolutionFilter.__init__(self,kernel)

#边缘检测滤波器。
class FindEdgesFilter(VConvolutionFilter):
	#An edge-finding filter with a 1-pixel radius
	def __init__(self):
		kernel = numpy.array([
			[-1,-1,-1],
			[-1, 9,-1],
			[-1,-1,-1],
		])
		VConvolutionFilter.__init__(self,kernel)


#模糊滤波器，为了达到模糊效果，通常权重和为1，而且临近像素的权重全为正。下面实现一个简单的邻近平均滤波器:
class BlurFilter(VConvolutionFilter):
	#A blur filter with a 2-piexl radius
	def __init__(self):
		kernel = numpy.array([
		[0.04,0.04,0.04,0.04,0.04],
		[0.04,0.04,0.04,0.04,0.04],
		[0.04,0.04,0.04,0.04,0.04],
		[0.04,0.04,0.04,0.04,0.04],
		[0.04,0.04,0.04,0.04,0.04],
		])
		VConvolutionFilter.__init__(self,kernel)

#脊状/浮雕效果滤波器
class EmbossFilter(VConvolutionFilter):
	def __init__(self):
		kernel = numpy.array([
			[-2,-1, 0],
			[-1, 9, 1],
			[ 0, 1, 2],
		])
		VConvolutionFilter.__init__(self,kernel)


class BGRFuncFilter(object):
	def __init__(self, vFunc = None, bFunc = None, gFunc = None, rFunc = None,dtype = numpy.uint8) :
		length = numpy.iinfo(dtype).max + 1
		self._bLookupArray = utils.createLookupArray(utils.createCompositeFunc(bFunc, vFunc), length)
		self._gLookupArray = utils.createLookupArray(utils.createCompositeFunc(gFunc, vFunc), length)
		self._rLookupArray = utils.createLookupArray(utils.createCompositeFunc(rFunc, vFunc), length)

	def apply(self, src, dst) :
		"""Apply the filter with a BGR source/destination."""
		b, g, r = cv2.split(src)
		utils.applyLookupArray(self._bLookupArray, b, b)
		utils.applyLookupArray(self._gLookupArray, g, g)
		utils.applyLookupArray(self._rLookupArray, r, r)
		cv2.merge([ b, g, r ], dst)



class BGRCurveFilter(BGRFuncFilter):
	def __init__(self, vPoints = None, bPoints = None,gPoints = None, rPoints = None, dtype = numpy.uint8):
		BGRFuncFilter.__init__(self, utils.createCurveFunc(vPoints), utils.createCurveFunc(bPoints), utils.createCurveFunc(gPoints), utils.createCurveFunc(rPoints), dtype)


class BGRPortraCurveFilter(BGRCurveFilter):
	def __init__(self, dtype = numpy.uint8):
		BGRCurveFilter.__init__(
			self,
			vPoints = [ (0, 0), (23, 20), (157, 173), (255, 255) ],
			bPoints = [ (0, 0), (41, 46), (231, 228), (255, 255) ],
			gPoints = [ (0, 0), (52, 47), (189, 196), (255, 255) ],
			rPoints = [ (0, 0), (69, 69), (213, 218), (255, 255) ],
			dtype = dtype)
