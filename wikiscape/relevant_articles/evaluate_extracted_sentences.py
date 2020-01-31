import pickle
import glob
import csv
from copy import deepcopy
from collections import defaultdict

TASKS_PRIMARY_PATH = "/data/aronsar/CrossTask/crosstask_release/tasks_primary.txt"
NUM_TASKS = 18 # number of primary tasks
TASK_STEPS = {}

def load_task_steps():
    with open(TASKS_PRIMARY_PATH, "rb") as f:
        # lines 0, 6, 12, 18, ... have the task id
        # lines 4, 10, 16, 22, ... have the task_steps
        all_lines = f.readlines()
        for i in range(NUM_TASKS):
            task_id = all_lines[i*6].decode('UTF-8').rstrip()
            TASK_STEPS[task_id] = all_lines[i*6+4].decode('UTF-8').rstrip().split(",")

def load_crosstask_orders(task_id):
    annotation_globpath = "/data/aronsar/CrossTask/crosstask_release/annotations/" + task_id + "_*.csv"
    task_step_orders = []
    for annotation_filepath in glob.glob(annotation_globpath):
        with open(annotation_filepath, "r") as annot_file:
            reader = csv.reader(annot_file)
            order_mask = []
            for line in reader:
                # actions organized in line by start time
                action_num, _, _ = line
                if int(action_num)-1 not in order_mask:
                    order_mask.append(int(action_num)-1)
            
            task_step_order = [TASK_STEPS[task_id][i] for i in order_mask]
            task_step_orders.append(task_step_order)

    return task_step_orders

def compare_orders(wikihow_orders, crosstask_orders):
    # recall: fraction of crosstask orders contained in wikihow
    # precision: fraction of wikihow orders contained in crosstask
    print("task_id: recall, precision")
    for task_id in wikihow_orders.keys():
        import pdb; pdb.set_trace()
        crosstask_orders_in_wikihow = 0
        wikihow_orders_in_crosstask = 0
        for wikihow_task_order in wikihow_orders[task_id]:
            if wikihow_task_order in crosstask_orders[task_id]:
                wikihow_orders_in_crosstask += 1
        for crosstask_task_order in crosstask_orders[task_id]:
            if crosstask_task_order in wikihow_orders[task_id]:
                crosstask_orders_in_wikihow += 1

        recall = crosstask_orders_in_wikihow / len(crosstask_orders[task_id])
        precision = wikihow_orders_in_crosstask / len(wikihow_orders[task_id])

        print(task_id + ": " + \
            str(recall)[:5] + " = " + \
            str(crosstask_orders_in_wikihow) + " / " + \
            str(len(crosstask_orders[task_id])) + ", " + \
            str(precision)[:5] + " = " + \
            str(wikihow_orders_in_crosstask) + " / " + \
            str(len(wikihow_orders[task_id])))


if __name__ == '__main__':
    load_task_steps()
    wikihow_orders = pickle.load(open("./extracted_orders.pkl", "rb"))
    crosstask_orders = {}
    for task_id in TASK_STEPS.keys():
        crosstask_orders[task_id] = load_crosstask_orders(task_id)

    compare_orders(wikihow_orders, crosstask_orders)
