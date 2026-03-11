import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

# Reference benchmark from the original Karpathy repo (approximate for H100 baseline)
# Note: Results are platform-dependent, but this provides a visual target.
KARPATHY_BASELINE = 1.05

def plot_progress(tsv_path="results.tsv", output_png="progress.png"):
    if not os.path.exists(tsv_path):
        print(f"Error: {tsv_path} not found.")
        return

    try:
        df = pd.read_csv(tsv_path, sep="\t")
        if df.empty:
            print("results.tsv is empty.")
            return

        df["val_bpb"] = pd.to_numeric(df["val_bpb"], errors="coerce")
        df["status"] = df["status"].str.strip().str.upper()

        # Filter out crashes for plotting
        valid = df[df["status"] != "CRASH"].copy().reset_index(drop=True)
        if valid.empty:
             print("No valid (non-crash) results to plot yet.")
             return

        fig, ax = plt.subplots(figsize=(12, 6))

        baseline_bpb = valid.loc[0, "val_bpb"]
        best_so_far = valid["val_bpb"].min()

        # Plot all experiments
        disc = valid[valid["status"] == "DISCARD"]
        if not disc.empty:
            ax.scatter(disc.index, disc["val_bpb"], c="#cccccc", s=20, alpha=0.5, label="Discarded")

        kept = valid[valid["status"] == "KEEP"]
        ax.scatter(kept.index, kept["val_bpb"], c="#2ecc71", s=60, edgecolors="black", label="Kept", zorder=5)

        # Running minimum
        running_min = valid["val_bpb"].cummin()
        ax.step(valid.index, running_min, where="post", color="#27ae60", linewidth=2, alpha=0.7, label="Your Best BPB")

        # Reference Line for Karpathy's Baseline
        ax.axhline(y=KARPATHY_BASELINE, color="#e74c3c", linestyle="--", linewidth=1.5, alpha=0.8, label=f"Karpathy Ref ({KARPATHY_BASELINE})")

        ax.set_xlabel("Experiment #")
        ax.set_ylabel("Validation BPB")
        ax.set_title(f"Autoresearch Progress: {len(df)} Experiments ({len(kept)} Kept)")
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Dynamic Y limits to include both your baseline and Karpathy's ref
        y_min = min(best_so_far, KARPATHY_BASELINE) * 0.98
        y_max = max(baseline_bpb, KARPATHY_BASELINE) * 1.05
        ax.set_ylim(y_min, y_max)

        plt.tight_layout()
        plt.savefig(output_png, dpi=120)
        print(f"Updated {output_png} (Includes Karpathy Reference)")
        
    except Exception as e:
        print(f"Plotting failed: {e}")

if __name__ == "__main__":
    # Change to the directory of results.tsv if needed
    target_dir = "/Users/surfiniaburger/Desktop/med-safety-gym-v2/autoresearch-macos"
    os.chdir(target_dir)
    plot_progress()
