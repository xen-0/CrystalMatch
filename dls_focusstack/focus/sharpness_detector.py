IMG_TO_STACK = 8 #how many images will be stacked

class SharpnessDetector(object):

    def __init__(self, img_fft):
        self.fft_img = img_fft


    def images_to_stack(self):
        n = len(self.fft_img)
        level = 0
        max = None
        images = []
        for s in self.fft_img:
            fft = s.getFFT()
            if fft > level:
                level = fft
                max = s.getImageNumber()

        range = self.find_range(max)
        for s in self.fft_img:
            if s.getImageNumber() in range:
                images.append(s.getImage())

        return images

    def find_range(self, max):
        n = len(self.fft_img)
        if max -(IMG_TO_STACK / 2) < 1:
            return range(1, IMG_TO_STACK)
        elif max + (IMG_TO_STACK / 2) > n:
            return range(-IMG_TO_STACK, n)
        else:
            return range(max - IMG_TO_STACK / 2, max + IMG_TO_STACK / 2)


