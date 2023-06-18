import time
import easyocr

# This needs to run only once to load the model into memory
reader = easyocr.Reader(['en'], gpu=True)

signs = {  # 'T': 'Stop',
    # 'P': 'Stop',
    '3': 30,
    #  '5': 50,
    '6': 60,
    #  '7': 70,
    #  '8': 80,
    '9': 90
    }

runs = 0
hits = 0
last_sign = ''


def image_to_string(img):
    global runs, hits, last_sign

    t_proc = time.perf_counter()

    # result = reader.readtext(img, batch_size=10, allowlist ='0123456789', low_text=0.2, text_threshold=0.2)
    result = reader.readtext(img, detail=0, batch_size=100, allowlist='0369',
                             low_text=0.4, text_threshold=0.4, link_threshold=0.5, mag_ratio=2.5)
    print(f"OCR: {result}")
    sign = ''
    try:
        sign = result[0]
    except:
        pass
    print(f"OCR: {sign} ({(time.perf_counter()-t_proc):.3f}s)")

    # Optimization
    # Number must be a multiple of 10 (30, 60, ...)
    for key in signs.keys():
        if key in sign:
            sign = signs[key]
            break

    # The number must have two digits
    if len(sign) != 2:
        sign = ''

    # Convert to int
    if (sign != ''):
        sign = int(sign)

    # Only set if detected at least two times in a row
    if (sign != '') and (sign != last_sign):
        tmp = last_sign
        last_sign = sign
        sign = tmp

    print(f"Sign: {sign} ({(time.perf_counter()-t_proc):.3f}s)")

    return sign
