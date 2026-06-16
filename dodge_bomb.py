import os
import random
import sys
import pygame as pg
import time

WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRect or 爆弾Rect
    戻り値：判定結果タプル（横方向判定結果、 縦方向判定結果）
    True：画面内 / False：画面外
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate        

def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面を5秒間表示する
    """
    black = pg.Surface((WIDTH, HEIGHT))
    black.fill((0, 0, 0))
    black.set_alpha(200)

    font = pg.font.Font(None, 80)
    txt = font.render("Game Over", True, (255, 255, 255))
    txt_rct = txt.get_rect(center=(WIDTH//2, HEIGHT//2 + 10))

    cry_img = pg.transform.rotozoom(
        pg.image.load("fig/8.png"), 0, 1.0
    )
    
    left_rct = cry_img.get_rect(
        center = (WIDTH//2 - 200, HEIGHT//2)
    )

    right_rct = cry_img.get_rect(
        center = (WIDTH//2 + 200, HEIGHT//2)
    )

    black.blit(txt, txt_rct)
    black.blit(cry_img, left_rct)
    black.blit(cry_img, right_rct)

    screen.blit(black, (0, 0))
    pg.display.update()

    time.sleep(5)

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    時間経過で拡大・加速する爆弾のSurfaceリストと加速度リストを返す関数
    """
    bb_imgs = []
    bb_accs = [a for a in range(1, 11)]
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0)) # 背景の黒を透過
        bb_imgs.append(bb_img)
    return bb_imgs, bb_accs

def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    移動量タプルと対応するこうかとん画像Surfaceの辞書を返す
    """
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9) # 左向き（元の画像）
    img1 = pg.transform.flip(img0, True, False) # 右向き（左右反転）

    return {
        (0, 0): img0,  # キー押下がない場合（デフォルトの向き）
        (+5, 0): img1, # 右
        (+5, -5): pg.transform.rotozoom(img1, 45, 1.0),  # 右上
        (0, -5): pg.transform.rotozoom(img1, 90, 1.0),   # 上
        (-5, -5): pg.transform.rotozoom(img0, -45, 1.0), # 左上
        (-5, 0): img0, # 左
        (-5, +5): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
        (0, +5): pg.transform.rotozoom(img1, -90, 1.0),  # 下
        (+5, +5): pg.transform.rotozoom(img1, -45, 1.0), # 右下
    }

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    
    # こうかとん画像の初期化（辞書を取得）
    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(0, 0)] 
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    # 爆弾の初期化
    bb_imgs, bb_accs = init_bb_imgs()
    bb_img = bb_imgs[0]
    bb_rct = bb_img.get_rect() 
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    vx, vy = +5, +5
    
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
            
        # 飛ぶ方向に従ってこうかとん画像を切り替える
        kk_img = kk_imgs[tuple(sum_mv)]
        screen.blit(kk_img, kk_rct)

        # 段階（0〜9）の計算
        step = min(tmr // 500, 9)
        
        # 爆弾の画像、Rectサイズ、加速度を更新
        bb_img = bb_imgs[step]
        bb_rct.width = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height
        avx = vx * bb_accs[step]
        avy = vy * bb_accs[step]

        # 計算した加速度(avx, avy)で移動
        bb_rct.move_ip(avx, avy)
        
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1 
        if not tate:
            vy *= -1
            
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()