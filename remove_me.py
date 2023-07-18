import matplotlib.pyplot as plt
import numpy as np
import mplcursors
np.random.seed(42)



lines = plt.plot(range(3), range(3), "o")
labels = ["a", "b", "c"]
cursor = mplcursors.cursor(lines, hover=mplcursors.HoverMode.Transient)
cursor.connect(
    "add", lambda sel: sel.annotation.set_text(labels[sel.index]))

plt.show()