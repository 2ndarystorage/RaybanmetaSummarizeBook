"""Draw an illustrative usage walkthrough; not a device recording."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
REGULAR = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REGULAR, size)

STEPS = [
    ("初回準備", ["Meta AIでメガネをペアリング。", "Developer Modeを有効にします。", "アプリの設定で自分のAPIキーを保存。"], "設定"),
    ("メガネを接続", ["「メガネを接続」でアプリを登録。", "次に「接続を開始」を押します。", "メガネを装着し、電源を入れてください。"], "メガネを接続"),
    ("本のページを映す", ["「映像を開始」を押します。", "初回はMeta AIでカメラ利用を許可。", "明るい場所で文字を正面に映します。"], "映像を開始"),
    ("文字数を決める", ["要約の上限を50〜1000文字で設定。", "初期値は200文字です。", "写っているページの文章を対象にします。"], "200文字以内"),
    ("ページを要約", ["「このページを要約」を押します。", "その時点の画像をOpenAIへ送信。", "文字の読み取りと要約が完了するまで待機。"], "このページを要約"),
    ("日本語で聴く", ["完成した要約を自動で読み上げます。", "「もう一度聴く」「読み上げ停止」も可能。", "メガネで聴く場合は音声出力先を確認。"], "もう一度聴く"),
]
frames = []
for step, (title, lines, target) in enumerate(STEPS):
    for pulse in range(4):
        canvas = Image.new("RGB", (960, 600), "#101827")
        d = ImageDraw.Draw(canvas)
        def text(x, y, value, size=20, color="#e7edf7", bold=False):
            d.text((x, y), value, font=font(size, bold), fill=color)
        def box(bounds, fill, outline=None, radius=14, width=2):
            d.rounded_rectangle(bounds, radius=radius, fill=fill, outline=outline, width=width)
        def button(y, label, enabled=True):
            active = label == target
            box((610, y, 880, y+42), "#237fca" if active else "#e9edf2",
                "#76d7ff" if active else None, width=3)
            text(625, y+8, label, 17, "#ffffff" if active else "#334155")
            if active:
                x = 874
                d.ellipse((x-10-pulse, y+10-pulse, x+10+pulse, y+30+pulse),
                          outline="#ffe184", width=3)
        text(40, 24, "META BOOK READER", 17, "#78d4ff", True)
        text(40, 65, "本を見て、短く聴く", 32, bold=True)
        text(40, 122, "操作イメージ / 実機録画ではありません", 16, "#a5b5c9")
        box((40, 186, 98, 244), "#237fca")
        text(59, 193, str(step+1), 30, bold=True)
        text(40, 270, title, 30, bold=True)
        for i, line in enumerate(lines):
            text(40, 331+i*39, line, 19)
        for i in range(6):
            box((40+i*73, 509, 100+i*73, 516), "#63caff" if i<=step else "#334155", radius=3)
        text(40, 536, f"{step+1} / 6  ·  自動で繰り返します", 16, "#a5b5c9")

        box((584, 22, 906, 578), "#f7f9fc", "#4b5b72", 30, 3)
        text(610, 48, "Meta Book Reader", 21, "#17253b", True)
        text(610, 83, "本を見て、短く聴く", 21, "#17253b", True)
        if step == 0:
            box((610, 130, 880, 385), "#ffffff", "#d6dee9")
            text(630, 151, "設定", 23, "#17253b", True)
            text(630, 197, "OpenAI API", 18, "#334155")
            box((627, 241, 862, 283), "#edf2f8")
            text(640, 250, "APIキー  ••••••••••", 18, "#334155")
            text(630, 308, "端末のKeychainに保存", 16, "#64748b")
            button(407, "設定")
            text(625, 470, "ご自身のAPIキーを使用", 15, "#64748b")
        else:
            box((610, 130, 880, 294), "#1e293b")
            if step >= 2:
                box((653, 145, 837, 278), "#fff8e9", radius=5)
                text(668, 153, "サンプルの本", 16, "#5a4a33", True)
                for n in range(6):
                    d.line((668, 191+n*12, 820-(n%3)*14, 191+n*12), fill="#a99d88", width=2)
                if step==2:
                    d.rectangle((646-pulse, 139-pulse, 844+pulse, 284+pulse), outline="#78d4ff", width=2)
            else:
                text(639, 193, "メガネの接続待ち", 18, "#ffffff")
            text(610, 304, "映像受信中" if step>=2 else "映像停止中", 14, "#64748b")
            if step==1:
                button(333, "メガネを接続")
                button(388, "接続を開始")
            elif step==2:
                button(340, "映像を開始")
                text(614, 400, "初回はカメラ許可が必要", 16, "#64748b")
            else:
                button(333, "200文字以内")
                button(388, "このページを要約")
                if step==4:
                    text(625, 457, "読み取り・要約中" + "・"*pulse, 17, "#237fca")
                    text(625, 495, "キャンセル", 16, "#64748b")
                elif step==5:
                    box((610, 443, 880, 496), "#e6f2fb")
                    text(625, 454, "要約の例：小さな習慣を", 16, "#17253b")
                    text(625, 476, "続ける大切さを述べている。", 14, "#17253b")
                    button(514, "もう一度聴く")
                else:
                    text(625, 459, "−    200文字以内    ＋", 18, "#334155")
        frames.append(canvas)
ROOT.mkdir(exist_ok=True)
path = ROOT / "usage-guide.gif"
frames[0].save(path, save_all=True, append_images=frames[1:], duration=850,
               loop=0, optimize=True, disposal=1)
frames[22].save(ROOT / "usage-preview.png")
print(f"{path}: {path.stat().st_size} bytes, {len(frames)} frames")
