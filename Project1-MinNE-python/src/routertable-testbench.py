from layer.router import RouterTable

for i in range(5):
    table = RouterTable(str(i + 1))
    table.static_merge()
    print(f"Router table {i + 1}")
    print(table)
