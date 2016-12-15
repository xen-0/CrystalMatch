"""
Creates a default cases file which includes an entry for every cell in the specified plate.
"""

plate = "46412"
batch1 = "449"
batch2 = "584"

case_file = "cases_blank.csv"

with open(case_file, 'w') as f:
    for row in "ABCDEFGH":
        for col in range(12):
            name = str(row) + str(col+1).zfill(2)

            template = "{}/{}/{}.jpg"
            file1 = template.format(plate, batch1, name)
            file2 = template.format(plate, batch2, name)

            line = file1 + ",," + file2 + ","
            print(line)
            f.write(line + "\n")
