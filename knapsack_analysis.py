import csv
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None  # Matplotlib yüklü değilse grafik çizimi atlanır


@dataclass
class Item:
    """Ürünün ağırlık ve değeri için basit veri sınıfı."""
    weight: int
    value: int


def generate_items(n: int, max_weight: int = 100, max_value: int = 100) -> List[Item]:
    """Rastgele ağırlık ve değer çiftlerinden oluşan item listesi üretir."""
    items = []
    for _ in range(n):
        weight = random.randint(1, max_weight)
        value = random.randint(1, max_value)
        items.append(Item(weight=weight, value=value))
    return items


def knapsack_dp(items: List[Item], capacity: int) -> Tuple[int, List[int]]:
    """Dinamik programlama ile sırt çantası için en yüksek değeri hesaplar."""
    n = len(items)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    # DP tablosunu doldurma: i. ürüne kadar olan itemlerle j kapasite için en iyi değer
    for i in range(1, n + 1):
        item = items[i - 1]
        for j in range(1, capacity + 1):
            if item.weight <= j:
                take = item.value + dp[i - 1][j - item.weight]
                skip = dp[i - 1][j]
                dp[i][j] = max(take, skip)
            else:
                dp[i][j] = dp[i - 1][j]

    # Seçilen itemleri izleme
    selected = []
    j = capacity
    for i in range(n, 0, -1):
        if dp[i][j] != dp[i - 1][j]:
            selected.append(i - 1)
            j -= items[i - 1].weight

    selected.reverse()
    return dp[n][capacity], selected


def knapsack_greedy(items: List[Item], capacity: int) -> Tuple[int, List[int]]:
    """Greedy yöntemiyle değer/ağırlık oranına göre seçim yapar."""
    indexed_items = [(i, item, item.value / item.weight) for i, item in enumerate(items)]
    indexed_items.sort(key=lambda x: x[2], reverse=True)

    total_value = 0
    total_weight = 0
    selected = []

    for index, item, ratio in indexed_items:
        if total_weight + item.weight <= capacity:
            selected.append(index)
            total_weight += item.weight
            total_value += item.value

    selected.sort()
    return total_value, selected


def run_experiment(n: int, capacity_ratio: float = 0.5) -> Tuple[dict, dict]:
    """Bir veri büyüklüğü için DP ve Greedy algoritmalarının sonuçlarını döndürür."""
    items = generate_items(n)
    total_weight = sum(item.weight for item in items)
    capacity = max(1, int(total_weight * capacity_ratio))

    # Dinamik Programlama çalıştırma
    start_dp = time.perf_counter()
    dp_value, dp_selected = knapsack_dp(items, capacity)
    dp_time = time.perf_counter() - start_dp

    # Greedy algoritması çalıştırma
    start_greedy = time.perf_counter()
    greedy_value, greedy_selected = knapsack_greedy(items, capacity)
    greedy_time = time.perf_counter() - start_greedy

    dp_result = {
        "N": n,
        "capacity": capacity,
        "value": dp_value,
        "time_sec": dp_time,
        "selected_count": len(dp_selected),
    }
    greedy_result = {
        "N": n,
        "capacity": capacity,
        "value": greedy_value,
        "time_sec": greedy_time,
        "selected_count": len(greedy_selected),
    }

    return dp_result, greedy_result


def save_results_csv(results: List[dict], filename: str) -> None:
    """Deney sonuçlarını CSV dosyasına kaydeder."""
    fieldnames = ["N", "capacity", "algorithm", "value", "time_sec", "selected_count"]
    path = Path(filename)
    with path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)


def plot_times(results: List[dict], filename: str) -> None:
    """Matplotlib ile algoritma çalışma sürelerini çizerek görselleştirir."""
    if plt is None:
        raise RuntimeError("Matplotlib yüklü değil; grafik üretmek için 'matplotlib' paketini yükleyin.")

    sizes = sorted({row["N"] for row in results})
    dp_times = [next(row["time_sec"] for row in results if row["N"] == n and row["algorithm"] == "DP") for n in sizes]
    greedy_times = [next(row["time_sec"] for row in results if row["N"] == n and row["algorithm"] == "Greedy") for n in sizes]

    plt.figure(figsize=(8, 5))
    plt.plot(sizes, dp_times, marker="o", label="DP")
    plt.plot(sizes, greedy_times, marker="s", label="Greedy")
    plt.title("Knapsack Algoritma Çalışma Süreleri")
    plt.xlabel("N (ürün sayısı)")
    plt.ylabel("Zaman (saniye)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


def main() -> None:
    """Ana program: deneyleri yürütür, sonuçları kaydeder ve grafik üretir."""
    random.seed(42)
    experiment_sizes = [100, 1000, 5000]
    results = []

    for n in experiment_sizes:
        print(f"Deney başlıyor: N={n}")
        dp_result, greedy_result = run_experiment(n)
        dp_result["algorithm"] = "DP"
        greedy_result["algorithm"] = "Greedy"
        results.append(dp_result)
        results.append(greedy_result)
        print(f"  DP: değer={dp_result['value']}, süre={dp_result['time_sec']:.4f} s")
        print(f"  Greedy: değer={greedy_result['value']}, süre={greedy_result['time_sec']:.4f} s")

    csv_file = "knapsack_results.csv"
    image_file = "knapsack_times.png"
    save_results_csv(results, csv_file)

    try:
        plot_times(results, image_file)
        print(f"Çalışma süreleri grafiği '{image_file}' olarak üretildi.")
    except RuntimeError as error:
        print(str(error))
        print("Grafik oluşturulamadı; önce 'matplotlib' yükleyin.")

    print(f"Sonuçlar '{csv_file}' dosyasına kaydedildi.")


if __name__ == "__main__":
    main()
