def parse_from_file(filename: str):
    with open(filename) as f:
        contents = f.readlines()[-20:]
    average_tps, droprate = None, None
    ans_count = 0
    for line in contents:
        if "Average TPS:" in line:
            average_tps = float(line.split()[-1].rstrip())
            ans_count += 1
        elif "drop rate:" in line:
            droprate = float(line.split()[-1].rstrip())
            ans_count += 1
        if ans_count == 2:
            break
    return average_tps, droprate

def parse_from_str(contents: str):
    contents = contents.split('\n')[-20:]
    average_tps, droprate = None, None
    for line in contents:
        if "Average TPS:" in line:
            average_tps = float(line.split()[-1].rstrip())
            continue
        if "drop rate:" in line:
            droprate = float(line.split()[-1].rstrip())
            break
    return average_tps, droprate
