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

with open('primary_steps.pkl', 'rb') as handle:
    step_names = pkl.load(handle)

for task in Y_true:
    for vid in Y_true[task]:
        ground_truth = Y_true[task][vid]
        prediction = Y_pred[task][vid]
        lsm_outputs = outputs[task][vid]
        num_seconds, num_steps = np.shape(ground_truth)

        lsm_outputs = np.exp(lsm_outputs)
        for s in range(num_steps):
            lsm_outputs[:,s] = lsm_outputs[:,s] / np.max(lsm_outputs[:,s])

        fig, ax = plt.subplots()
        ax.set_axis_off()
        tb = Table(ax, bbox=[0,0,1,1])
        cwidth = 15
        cheight = 1

        # add cells
        for (r,c), _ in np.ndenumerate(ground_truth):
            # lsm_output cell
            color = (0, 0, lsm_outputs[r,c])
            column = 3*c+1
            tb.add_cell(r, column, cwidth, cheight, \
                    facecolor=color, edgecolor='none')

            # prediction cell
            if prediction[r,c] > .99 and ground_truth[r,c] > .99:
                color = 'limegreen'

            elif prediction[r,c] > .99 and ground_truth[r,c] < .99:
                color = 'red'

            else:
                color = (0, 0, lsm_outputs[r,c])
            column = 3*c+1+1
            tb.add_cell(r, column, cwidth, cheight, \
                    facecolor=color, edgecolor='none')

            # ground truth cell
            if ground_truth[r,c] > .99:
                color = 'yellow'
            else:
                color = (0, 0, lsm_outputs[r,c])
            column = 3*c+2+1
            tb.add_cell(r, column, cwidth, cheight, \
                    facecolor=color, edgecolor='none')
        
        # Row Labels
        for r in range(num_seconds):
            if r % 10 == 0:
                tb.add_cell(r, 0, 25, cheight, text=str(r), loc='right', \
                            edgecolor='none', facecolor='none')

        # Column Labels
        for c in range(num_steps):
            tb.add_cell(num_seconds, c+1, 15, 15, text=step_names[task][c], loc='right', \
                            edgecolor='none', facecolor='none')

        ax.add_table(tb)
        fig.savefig('graphs/' + task + '---' + vid)
        import pdb; pdb.set_trace()
        plt.close(fig)
