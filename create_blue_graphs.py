import pickle as pkl
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.table import Table

Y_pred = {}
Y_true = {}

with open('Y_pred.pkl', 'rb') as handle:
    Y_pred = pkl.load(handle)

with open('Y_true.pkl', 'rb') as handle:
    Y_true = pkl.load(handle)

with open('outputs.pkl', 'rb') as handle:
    outputs = pkl.load(handle)

for task in Y_true:
    for vid in Y_true[task]:
        ground_truth = Y_true[task][vid]
        prediction = Y_pred[task][vid]
        lsm_outputs = outputs[task][vid]
        num_seconds, num_steps = np.shape(ground_truth)

        lsm_outputs = np.exp(lsm_outputs)
        for t in range(num_seconds):
            lsm_outputs[t,:] = lsm_outputs[t,:] / np.max(lsm_outputs[t,:])

        fig, ax = plt.subplots()
        ax.set_axis_off()
        tb = Table(ax, bbox=[0,0,1,1])
        cwidth = 15
        cheight = 1

        # add cells
        for (r,c), _ in np.ndenumerate(ground_truth):
            # lsm_output cell
            color = (0, 0, lsm_outputs[r,c])
            column = 3*c
            tb.add_cell(r, column, cwidth, cheight, \
                    facecolor=color, edgecolor='none')

            # prediction cell
            if prediction[r,c] > .99 and ground_truth[r,c] > .99:
                color = 'green'

            elif prediction[r,c] > .99 and ground_truth[r,c] < .99:
                color = 'red'

            else:
                color = (0, 0, lsm_outputs[r,c])
            column = 3*c+1
            tb.add_cell(r, column, cwidth, cheight, \
                    facecolor=color, edgecolor='none')

            # ground truth cell
            if ground_truth[r,c] > .99:
                color = 'yellow'
            else:
                color = (0, 0, lsm_outputs[r,c])
            column = 3*c+2
            tb.add_cell(r, column, cwidth, cheight, \
                    facecolor=color, edgecolor='none')

        ax.add_table(tb)
        fig.savefig('graphs/' + task + '---' + vid)
        import pdb; pdb.set_trace()
        plt.close(fig)
