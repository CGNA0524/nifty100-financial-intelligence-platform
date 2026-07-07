from src.analytics.cagr import free_cash_flow_cagr

tests = [
    (100, 200, 5),
    (200, 100, 5),
    (0, 100, 5),
    (-100, 200, 5),
    (100, -50, 5)
]

for start, end, years in tests:

    value, flag = free_cash_flow_cagr(
        start,
        end,
        years
    )

    print(
        f"Start={start} | End={end} | Years={years}"
    )
    print("CAGR :", value)
    print("Flag :", flag)
    print("-" * 50)