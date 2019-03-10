./megam binary train_without_prefix.txt > weights.txt
./megam -predict weights.txt binary train_without_prefix.txt > train_predictions.txt
./megam -predict weights.txt binary dev_without_prefix.txt > dev_predictions.txt
./megam -predict weights.txt binary test_without_prefix.txt > test_predictions.txt
./megam -predict weights.txt binary unreleased_without_prefix.txt > unreleased_predictions.txt
