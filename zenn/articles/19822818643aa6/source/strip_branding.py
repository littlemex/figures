"""strip_branding.py -- pptx から会社のロゴ、著作権表示、ヘッダー、フッター、ページ番号を取り除く。

    /usr/bin/python3 strip_branding.py <in.pptx> [out.pptx]

1. マスターとすべてのレイアウトから、画像と、フッター・日付・ページ番号のプレースホルダーと、
   Amazon / AWS / (c) を含む文字の図形を消す。
2. 各スライドに showMasterSp="0" を付け、マスターとレイアウトの図形を表示しない。
3. 各スライドに残ったフッター類のプレースホルダーも消す。背景の塗りは残す。
"""
import re
import sys

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE, PP_PLACEHOLDER

BRAND = re.compile(r"amazon|aws|©|copyright|all rights reserved", re.I)
FOOTERS = {PP_PLACEHOLDER.FOOTER, PP_PLACEHOLDER.DATE, PP_PLACEHOLDER.SLIDE_NUMBER, PP_PLACEHOLDER.HEADER}


def bad(sh):
    if sh.shape_type == MSO_SHAPE_TYPE.PICTURE or sh.shape_type == MSO_SHAPE_TYPE.GROUP:
        return True
    if sh.is_placeholder and sh.placeholder_format.type in FOOTERS:
        return True
    if sh.has_text_frame and BRAND.search(sh.text_frame.text or ""):
        return True
    if sh.element.xpath('.//a:blip'):
        return True
    return False


def clean(tree):
    n = 0
    for sh in list(tree.shapes):
        if bad(sh):
            sh.element.getparent().remove(sh.element)
            n += 1
    return n


def main(src, dst):
    p = Presentation(src)
    n = 0
    for m in p.slide_masters:
        n += clean(m)
        for lay in m.slide_layouts:
            n += clean(lay)
    for s in p.slides:
        s.element.set("showMasterSp", "0")
        for sh in list(s.shapes):
            if sh.is_placeholder and sh.placeholder_format.type in FOOTERS:
                sh.element.getparent().remove(sh.element)
                n += 1
            elif sh.has_text_frame and BRAND.search(sh.text_frame.text or "") and sh.element.xpath('.//a:fld'):
                sh.element.getparent().remove(sh.element)
                n += 1
    p.save(dst)
    print(dst, "removed", n)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else sys.argv[1])
