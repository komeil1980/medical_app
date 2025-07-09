
@captcha_bp.route('/captcha_image')
def captcha_image():
    # تولید رشته کپچا (حروف و اعداد فارسی)
    chars = '۱۲۳۴۵۶۷۸۹۰' + 'ابپتثجچحخدذرزسشصضطظعغفقکگلمنوهی'
    captcha_text = ''.join(random.choices(chars, k=5))
    session['captcha_text'] = captcha_text

    # ساخت تصویر
    img = Image.new('RGB', (150, 50), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT_PATH, 32)
    except:
        font = ImageFont.load_default()
    draw.text((15, 5), captcha_text, font=font, fill=(0, 0, 0))

    # نویز ساده
    for _ in range(30):
        x1 = random.randint(0, 150)
        y1 = random.randint(0, 50)
        x2 = random.randint(0, 150)
        y2 = random.randint(0, 50)
        draw.line(((x1, y1), (x2, y2)), fill=(150, 150, 150), width=1)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    response = make_response(send_file(buf, mimetype='image/png'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response
