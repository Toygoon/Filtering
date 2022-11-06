import cv2
import numpy as np
from skimage.exposure import rescale_intensity


class ImageFilter:
    def __init__(self, img: str):
        self.img = cv2.imread(img)
        self.mask = None

    def getFilterNames(self):
        return {'mean3': 'Mean Filter 3*3'}

    def getMeanFilterMask(self, size: int):
        return np.full((size, size), 1 / (size * size))

    def mean(self, size: int):
        self.mask = self.getMeanFilterMask(size)
        return self.convolution()

    def convolution(self):
        # H : Height, W : Width
        # 원본 이미지의 크기를 나타냄
        (H, W) = self.img.shape[:2]

        # MH : Mask Height, MW : Mask Width
        # Mask의 크기를 나타냄
        (MH, MW) = self.mask.shape[:2]

        # P : Padding
        # 테두리 부분은 이미지를 그대로 Convolution 할 수 없으므로,
        # 크기를 늘려야 하며, 이미지의 추가 공간을 위한 크기
        P = (MW - 1) // 2

        # 추가 공간을 만듬
        img = cv2.copyMakeBorder(self.img, P, P, P, P, cv2.BORDER_REPLICATE)
        # 결과를 저장할 공간을 만들어 둠
        out = np.zeros((H, W), dtype="float32")

        for y in np.arange(P, H + P):
            for x in np.arange(P, W + P):
                # 픽셀 별로 저장하기 위해, 현재 연산 중인 부분을
                # Region of Interest로 뽑음
                roi = img[y - P:y + P + 1, x - P:x + P + 1]

                # 계산된 값을 출력 이미지에 저장함
                out[y - P, x - P] = (roi * self.mask).sum()

        # rescale_intensity를 이용해 [0, 255] 범위를 벗어나는 부분을 보정
        out = rescale_intensity(out, in_range=(0, 255))
        # 이미지 형식인 uint8로 변경
        out = (out * 255).astype("uint8")

        # 이미지 출력
        return out
