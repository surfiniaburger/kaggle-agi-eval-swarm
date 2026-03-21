import json
import matplotlib.pyplot as plt
import os

def plot_gap(json_path="benchmark_state.json", output_png="gap_progress.png"):
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    try:
        with open(json_path, "r") as f:
            data = json.load(f)
            
        if not data:
            print("benchmark_state.json is empty.")
            return

        scores = [item.get("val_score", 0.0) for item in data]
        statuses = [item.get("status", "unknown") for item in data]
        indices = list(range(len(scores)))

        fig, ax = plt.subplots(figsize=(10, 5))

        # Separate keeps and crashes for visualization
        keeps_idx = [i for i, s in enumerate(statuses) if s == "keep"]
        keeps_scores = [scores[i] for i in keeps_idx]
        
        crashes_idx = [i for i, s in enumerate(statuses) if s == "crash"]
        crashes_scores = [scores[i] for i in crashes_idx]

        if keeps_idx:
            ax.scatter(keeps_idx, keeps_scores, c="#2ecc71", s=100, edgecolors="black", label="Passed Benchmark", zorder=5)
            # Running maximum (improvement)
            running_max = []
            curr_max = 0.0
            for s in scores:
                curr_max = max(curr_max, s)
                running_max.append(curr_max)
            ax.step(indices, running_max, where="post", color="#27ae60", linewidth=2, alpha=0.7, label="Best Gap So Far")

        if crashes_idx:
            ax.scatter(crashes_idx, crashes_scores, c="#e74c3c", marker="x", s=80, alpha=0.6, label="Failed/Crashed")

        ax.set_xlabel("Iteration #")
        ax.set_ylabel("Discriminatory Gap (val_score)")
        ax.set_title(f"Benchmark Forge Progress: {len(data)} Iterations")
        ax.set_ylim(-0.05, 1.05)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_png, dpi=120)
        print(f"Updated {output_png} with benchmarking progress.")
        
    except Exception as e:
        print(f"Plotting failed: {e}")

if __name__ == "__main__":
    plot_gap()
