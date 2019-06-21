import sys
import cv2
import numpy as np

__author__ = "Shinri Ishikawa<justlikebussiness@google.com>"
__status__ = "development"
__version__ = "0.0.1"
__date__    = "20 June 2019"

class Keystone(object):
    """
    Keystone class
    @see https://qiita.com/hnkyi/items/3ff24ee7c5cc2eda3b37
    """
    @classmethod
    def rewrite(self, filename):
        # ファイル読込み
        img = cv2.imread(filename)
        size = img.shape[0] * img.shape[1]

        # グレースケール化
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 入力座標の選定
        best_white = 0
        best_rate = 0.0
        best_approx = []
        dict_approx = {}
        for white in range(10, 255, 10):
            # 二値化
            ret, th1 = cv2.threshold(gray, white, 255, cv2.THRESH_BINARY)

            # 輪郭抽出
            contours, hierarchy = cv2.findContours(th1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # 面積が以下の条件に満たすものを選定
            # 角の数が4つ、1%以上、99%未満
            max_area = 0
            approxs = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                epsilon = 0.1 * cv2.arcLength(cnt, True)
                tmp = cv2.approxPolyDP(cnt, epsilon, True)
                if 4 == len(tmp):
                    approxs.append(tmp)
                    if size * 0.01 <= area\
                    and area <= size * 0.99\
                    and max_area < area:
                        best_approx = tmp
                        max_area = area
            if 0 != max_area:
                rate = max_area / size * 100
                if best_rate < rate:
                    best_rate = rate
                    best_white = white
            dict_approx.setdefault(white, approxs)

        if 0 == best_white:
            print("The analysis failed.")
            exit()

        # 出力座標の計算(三平方の定理)
        r_btm = best_approx[0][0]
        r_top = best_approx[1][0]
        l_top = best_approx[2][0]
        l_btm = best_approx[3][0]
        top_line   = (abs(r_top[0] - l_top[0]) ^ 2) + (abs(r_top[1] - l_top[1]) ^ 2)
        btm_line   = (abs(r_btm[0] - l_btm[0]) ^ 2) + (abs(r_btm[1] - l_btm[1]) ^ 2)
        left_line  = (abs(l_top[0] - l_btm[0]) ^ 2) + (abs(l_top[1] - l_btm[1]) ^ 2)
        right_line = (abs(r_top[0] - r_btm[0]) ^ 2) + (abs(r_top[1] - r_btm[1]) ^ 2)
        max_x = top_line  if top_line  > btm_line   else btm_line
        max_y = left_line if left_line > right_line else right_line

        # 画像の座標上から4角を切り出す
        pts1 = np.float32(best_approx)
        pts2 = np.float32([[max_x, max_y], [max_x, 0], [0, 0], [0, max_y]])

        # 透視変換の行列を求める
        M = cv2.getPerspectiveTransform(pts1, pts2)

        # 変換行列を用いて画像の透視変換
        src = cv2.imread(filename)
        dst = cv2.warpPerspective(src, M, (max_x, max_y))

        #高さを定義
        height = dst.shape[0]                         
        #幅を定義
        width = dst.shape[1]  
        #回転の中心を指定                          
        center = (int(width/2), int(height/2))
        #回転角を指定
        angle = 180.0
        #スケールを指定
        scale = 1.0
        #getRotationMatrix2D関数を使用
        trans = cv2.getRotationMatrix2D(center, angle, scale)
        #アフィン変換
        dst = cv2.warpAffine(dst, trans, (width, height))

        # 結果出力
        print("Best parameter: white={} (rate={})".format(best_white, best_rate))
        # rewrite
        cv2.imwrite(filename, dst)

        src = cv2.imread(filename)
        cv2.drawContours(src, dict_approx[best_white], -1, (0, 255, 0), 3)
        cv2.imwrite("_detail.{}".format(filename), src)