import sys
import numpy as np
import copy

global trainFileName
global testFileName
global outputFileName

train_data = []
test_data = []
features = {}
features_idx = {}


def get_features():
    feats = train_data[0]
    del train_data[0]  # train_data에서 feature 이름 행은 제거
    for i in range(len(feats)):
        values = list(set(np.array(train_data).T[i]))  # 배열에서 column 추출
        features[feats[i]] = values
        features_idx[feats[i]] = i


def output_result(result):
    global outputFileName
    f = open(outputFileName, 'w')
    output_feature = list(features.keys())[len(features)-1]
    for key in features.keys():
        f.write(key)
        f.write('\t')
    f.write('\n')
    for i in range(1, len(test_data)):
        data = test_data[i]
        for d in data:
            f.write(d)
            f.write('\t')
        f.write(result[i-1])
        f.write('\n')


def get_input():
    global trainFileName, testFileName, outputFileName
    trainFileName = sys.argv[1]
    testFileName = sys.argv[2]
    outputFileName = sys.argv[3]
    f = open(trainFileName, mode='r', encoding='utf-8')
    while True:
        line = f.readline()
        if not line:
            break
        parse = line.split()
        data = []
        for i in range(len(parse)):
            data.append(parse[i])
        train_data.append(data)
    f = open(testFileName, mode='r', encoding='utf-8')
    while True:
        line = f.readline()
        if not line:
            break
        parse = line.split()
        data = []
        for i in range(len(parse)):
            data.append(parse[i])
        test_data.append(data)


def get_before_gain(data):
    output_feature_idx = len(features) - 1
    key, counts = np.unique(np.array(data).T[output_feature_idx], return_counts=True)
    total_len = len(data)
    gain = 0
    for val in counts:
        p = (val / total_len)
        gain += (-(p * np.log2(p)) if p > 0 else 0)
    return gain


def pick_next_feature(data, available_features):
    output_feature_idx = len(features) - 1
    before_gain = get_before_gain(data)
    total_len = len(data)  # 나누기전 record 개수
    gain_ratio = {}
    for feature in available_features:  # credit, term, income ....
        value_output = []
        split_info = 0
        feature_idx = features_idx[feature]
        feature_values = np.unique(np.array(data).T[feature_idx])
        if len(feature_values) != len(features[feature]):
            continue
        for feature_value in feature_values:  # fair, poor ,excellent ...
            one_value = []
            for d in data:
                if feature_value == d[feature_idx]:
                    one_value.append(d[output_feature_idx])
            p = len(one_value) / total_len
            split_info += (-(p * np.log2(p)) if p > 0 else 0)
            value_output.append(one_value)
        after_gain = 0
        if split_info == 0:
            continue
        for value in value_output:
            weighted_avg = len(value)/total_len
            key, counts = np.unique(value, return_counts=True)
            entropy = 0
            for c in counts:
                p = c / len(value)
                entropy += (-(p * np.log2(p)) if p > 0 else 0)
            after_gain += (weighted_avg * entropy)
        gain_ratio[feature] = (before_gain - after_gain) / split_info

    gain_ratio = dict(sorted(gain_ratio.items(), key=lambda x: x[1], reverse=True))
    if len(gain_ratio) != 0:
        return list(gain_ratio.keys())[0]
    return "no"


def decision_tree(data, available_features):
    output_feature_idx = len(features) - 1

    if len(set(np.array(data).T[output_feature_idx])) == 1:  # all same labels in the node
        return data[0][output_feature_idx]

    else:
        next_feature = pick_next_feature(data, available_features)
        if next_feature == "no":  # no more remaining feature to partition.
            output_values = np.array(data).T[output_feature_idx]
            values, counts = np.unique(output_values, return_counts=True)  # majority voting
            max_idx = np.argmax(counts)
            return values[max_idx]
        next_available_features = copy.deepcopy(available_features)
        next_available_features.remove(next_feature)  # no repeated feature in one path

        tree = {next_feature: {}}

        feature_idx = features_idx[next_feature]
        for feature_value in features[next_feature]:   # partition by picked feature(next feature)
            next_data = []
            for d in data:
                if feature_value == d[feature_idx]:
                    next_data.append(d)
            child = decision_tree(next_data, next_available_features)
            tree[next_feature][feature_value] = child
        return tree


def get_label(tree, dict_data):
    tmp_tree = tree
    while True:
        if type(tmp_tree) is not dict:
            return tmp_tree
        cur_key = list(tmp_tree.keys())[0]
        value = dict_data[cur_key]
        tmp_tree = tmp_tree[cur_key][value]


def get_result(tree):
    input_features = test_data[0]
    result = []
    for i in range(1, len(test_data)):  # test data 한 줄 씩
        record = test_data[i]
        record_to_dict = {}
        for j in range(len(record)):
            record_to_dict[input_features[j]] = record[j]
        result.append(get_label(tree, record_to_dict))
    return result


def main():
    get_input()
    get_features()
    avail = []
    for key, value in features.items():
        avail.append(key)
    del avail[len(avail)-1]  # output feature은 제외
    dt = decision_tree(train_data, avail)
    result = get_result(dt)
    output_result(result)


if __name__ == '__main__':
    main()
