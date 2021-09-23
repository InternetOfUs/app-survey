



def map_creator(file_path):
    with open(file_path, encoding='utf8') as f:
        line_count = 0
        for line in f:
            line_count += 1
            #print("{:02d}".format(1))
            print('"'+'{:02d}'.format(line_count)+'":"'+line.strip()+'",')


file_path = "/home/davaa/country_list.txt"
map_creator(file_path)