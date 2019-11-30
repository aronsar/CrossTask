import pickle as pkl

Y_pred = {}
Y_true = {}

with open('Y_pred.pkl', 'rb') as handle:
    Y_pred = pkl.load(handle)

with open('Y_true.pkl', 'rb') as handle:
    Y_true = pkl.load(handle)

import pdb; pdb.set_trace()
#with open('outputs.pkl', 'rb') as handle:
#    outputs = pkl.load(handle)

for task in Y_true:
    for vid in Y_true[task]:
        ground_truth = Y_true[task][vid]
        prediction = Y_pred[task][vid]
        lsm_outputs = outputs[task][vid]
        num_seconds, num_steps = np.shape(ground_truth)

        fig, ax = plt.subplots()
        ax.set_axis_off()
        tb = Table(ax)
        cwidth = 15
        cheight = 1

        # add cells
        for (r,c), _ in np.ndenumerate(ground_truth):
            # lsm_output cell
            color = (1, 1, lsm_outputs[r,c])
            column = 3*c
            tb.add_cell(r, column, cwidth, cheight, \
                    facecolor=color, edgecolor='none')

            # prediction cell
            if prediction[r,c] > .99 and ground_truth[r,c] > .99:
                color = 'green'

            elif prediction[r,c] > .99 and ground_truth[r,c] < .99:
                color = 'red'

            else:
                color = (1, 1, lsm_outputs[r,c])
            column = 3*c+1
            tb.add_cell(r, column, cwidth, cheight, \
                    facecolor=color, edgecolor='none')

            # ground truth cell
            if ground_truth[r,c] > .99:
                color = 'yellow'
            else:
                color = (1, 1, lsm_outputs[r,c])
            column = 3*c+2
            tb.add_cell(r, column, cwidth, cheight, \
                    facecolor=color, edgecolor='none')

        ax.add_table(tb)
        fig.savefig(task + '---' + vid)
        plt.close(fig)
        














        graph = np.zeros(num_seconds, 3*num_steps, dtype=float32)
        for s in range(num_steps):
            bar = np.transpose(np.tile(model_ouputs[:,s], [3,1]))
            p_mask = prediction[:,s] > .99
            bar[:, 1][p_mask] = -1
            gt_mask = ground_truth[:,s] > .99
            bar[:, 2][gt_mask] = 2
            
            graph[:, 3*s: 3*(s+1)] = bar.copy()
        
        graphs[task][vid] = graph.copy()

pkl.dump(graphs, open('graphs.pkl', 'wb'))

def create_graph(pregraph)

for task in graphs:
    for vid in graphs[task]:
        create_graph(graphs[task][vid])
        
    
