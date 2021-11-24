from layer.router import RouterTable

tables = [RouterTable(str(i)) for i in range(4, 9)]
packages = [table.pack() for table in tables]

for i in range(5):
    while tables[i].next_merge != "":
        tables[i].merge(packages[int(tables[i].next_merge) - 4])
    print(f"Table {i + 4}:")
    print(tables[i])
