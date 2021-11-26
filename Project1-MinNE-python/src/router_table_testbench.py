from layer.router import RouterTable

tables = [RouterTable(str(i)) for i in range(4, 9)]
packages = [table.package() for table in tables]

for i in range(5):
    while tables[i]._next_merge != "":
        tables[i].merge(packages[int(tables[i]._next_merge) - 4])
    print(f"Table {i + 4}:")
    print(tables[i])
