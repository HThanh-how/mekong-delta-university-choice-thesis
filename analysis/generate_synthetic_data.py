import csv
import random
from pathlib import Path

random.seed(2407059)
factors = ["FIT", "CAR", "REP", "COS", "SOC", "COM", "LOC"]
means = [4.08, 4.21, 3.94, 3.72, 3.55, 3.67, 3.78]
rows = []
for i in range(486):
    z = [random.gauss(0, 1) for _ in factors]
    values = {}
    for factor, mean, latent in zip(factors, means, z):
        for j in range(1, 5):
            values[f"{factor}{j}"] = max(1, min(5, round(mean + 0.48 * latent + random.gauss(0, 0.42))))
    dec_latent = sum(b * x for b, x in zip([.286, .241, .183, .146, .112, .078, .098], z)) + random.gauss(0, .55)
    for j in range(1, 5):
        values[f"DEC{j}"] = max(1, min(5, round(3.91 + .55 * dec_latent + random.gauss(0, .38))))
    rows.append({
        "ID": i + 1,
        "GioiTinh": 1 if i < 218 else (2 if i < 479 else 3),
        "KhuVuc": 0 if i < 205 else 1,
        "ThuNhap": 1 if i < 196 else (2 if i < 399 else 3),
        **values,
    })

target = Path(__file__).parents[1] / "data" / "survey_synthetic_486.csv"
target.parent.mkdir(exist_ok=True)
with target.open("w", newline="", encoding="utf-8-sig") as handle:
    writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
print(target)
