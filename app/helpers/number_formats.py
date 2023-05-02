def human_format(num, round_to=2):
    num = float(num)
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num = round(num / 1000.0, round_to)
    return "{:.{}f} {}".format(num, round_to, ["", "K", "M", "G", "T", "P"][magnitude])
