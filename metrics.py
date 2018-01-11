import sys

prefix = sys.argv[1]

for suffix in ["-train.results", "-dev.results", "-test.results"]:
  filename = prefix + suffix
  print("--- " + filename + " ---")
  accuracies = open(filename).readlines()

  total_num_correct = 0.
  total_num = 0.
  
  sentence_accuracies = { }

  for accuracy in accuracies:
    identifier, correct = accuracy.strip().split("\t")
    correct = correct.lower() == "true"

    sentence_id = identifier.split("-")[0]
    if not sentence_id in sentence_accuracies:
      sentence_accuracies[sentence_id] = correct
    sentence_accuracies[sentence_id] = correct and sentence_accuracies[sentence_id]

    total_num += 1.

    if correct:
      total_num_correct += 1.

  num_consistent = 0.
  num_unique_sents = len(sentence_accuracies)
  for consistent in sentence_accuracies.values():
    num_consistent += float(consistent)

  print("Accuracy: " + str(total_num_correct) + " / " + str(total_num) + " = " + "{:10.2f}".format(100. * total_num_correct / total_num))
  print("Consistency: " + str(num_consistent) + " / " + str(num_unique_sents) + " = " + "{:10.2f}".format(100. * num_consistent / num_unique_sents))
