import matplotlib.pyplot as plt
import seaborn as sns


def get_amount_combinations(moves):
    move_amount = moves // 2
    if moves % 2 == 0:
        black_amount, white_amount = move_amount, move_amount
    else:
        black_amount, white_amount = move_amount + 1, move_amount

    black_turn = True
    combinations = 1

    while True:
        if black_amount == 0:
            break
        if black_turn:
            combinations *= black_amount
            black_amount -= 1
            black_turn = False
        else:
            combinations *= white_amount
            white_amount -= 1
            black_turn = True

    return combinations


amounts = [get_amount_combinations(i) for i in range(1, 20)]


fig, ax = plt.subplots(figsize=(8, 6), dpi=300)

# Seaborn bar plot with black bars
sns.barplot(
    x=[i for i in range(1, 20)],
    y=amounts,
    errorbar=None,
    color="black",
    edgecolor="black",
    linewidth=2.5,
)

# Axis labels with bold formatting
ax.set_xlabel("Missing Moves", fontsize=18, fontweight="bold")
ax.set_ylabel("Amount Variations", fontsize=18, fontweight="bold")
ax.set_yscale("log")

# Customize tick parameters for better visibility
ax.tick_params(
    axis="both", which="major", labelsize=14, width=2.5, length=6, direction="in"
)

# Set thicker axis spines
for spine in ["top", "right", "bottom", "left"]:
    ax.spines[spine].set_linewidth(2.5)

# Optional: Add grid with subtle styling
# ax.grid(True, linestyle='--', linewidth=0.7, alpha=0.6)

# Adjust layout to prevent cropping of labels
plt.tight_layout()

# Save as a high-resolution PNG (change to PDF if needed)
plt.savefig("barplot_variation_amount.png", dpi=300, bbox_inches="tight")
