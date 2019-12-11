from rouge import Rouge
import sys

def find_most_similar(num_most_similar, hypothesis_text_file, reference_text):
    most_similar = [(0,"")]*num_most_similar
    rouge = Rouge()

    with open(hypothesis_text_file, "rb") as hypothesis_text:
        for hyp in hypothesis_text:
            scores = rouge.get_scores(str(hyp), reference_text)[0]
            avg_recall = (scores['rouge-1']['r'] \
                        + scores['rouge-2']['r'])/ 3

            for i, (recall, _) in enumerate(most_similar):
                if avg_recall > recall:
                    most_similar[i] = (avg_recall, str(hyp))
                    break

    return most_similar
            

if __name__ == "__main__":
    num_most_similar = sys.argv[1]
    hypothesis_text_file = sys.argv[2]
    reference_text = sys.argv[3]
    print(find_most_similar(int(num_most_similar), hypothesis_text_file, reference_text))



