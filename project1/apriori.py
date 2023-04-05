import sys
import itertools

transactions = []
L = [[]]  # for 1 start index
every_L = []
count = {}  # for memoization ( item set 별 count 횟수 dictionary 에 저장 )
rules = []
global minSupport
global inputFileName
global outputFileName


def get_first_l():
    c1 = {}  # dictionary (key, value)
    for transaction in transactions:
        for key in transaction:
            if key in c1:
                c1[key] += 1
            else:
                c1[key] = 1
    l1 = []
    num_transactions = len(transactions)
    for key, value in c1.items():
        count[tuple([key])] = value
        if (value / num_transactions) >= minSupport:
            l1.append(tuple([key]))
    l1 = sorted(l1)
    L.append(l1)


def output():
    global outputFileName
    f = open(outputFileName, 'w')
    for rule in rules:
        f.write("{")
        for j in range(len(rule[0])):
            f.write(rule[0][j])
            if j != len(rule[0])-1:
                f.write(",")
        f.write("}")
        f.write("\t")
        f.write("{")
        for j in range(len(rule[1])):
            f.write(rule[1][j])
            if j != len(rule[1]) - 1:
                f.write(",")
        f.write("}")
        f.write("\t")
        f.write(format(rule[2]*100, ".2f"))
        f.write("\t")
        f.write(format(rule[3]*100, ".2f"))
        f.write("\n")


def get_input():
    global minSupport, inputFileName, outputFileName
    minSupport = int(sys.argv[1]) / 100
    inputFileName = sys.argv[2]
    outputFileName = sys.argv[3]
    f = open(inputFileName, mode='r', encoding='utf-8')
    while True:
        line = f.readline()
        if not line:
            break
        parse = line.split()
        transaction = []
        for i in range(len(parse)):
            transaction.append(parse[i])
        transactions.append(sorted(transaction))


# get Ck+1 from Lk
def get_c(size):
    # self join
    previous_l = L[size-1]
    all_items = []
    for item_set in previous_l:
        for item in item_set:
            if item not in all_items:
                all_items.append(item)
    all_items = sorted(all_items)
    candidate = list(itertools.combinations(all_items, size))
    if size == 2:
        return candidate

    # pruning 1 : infrequent item set 여부 확인해서 제거
    candidate2 = []
    for item_set in candidate:
        nCr = list(itertools.combinations(item_set, size-1))
        is_frequent = True
        for comb in nCr:
            if comb not in previous_l:
                is_frequent = False
                break
        if is_frequent:
            candidate2.append(item_set)
    return candidate2


# pruning 2 : sup 계산해서 min 보다 작으면 없애고 L 얻기
def get_l_from_c(c, size):
    chk = {}
    for item in c:
        chk[item] = 0
    for transaction in transactions:
        nCr = tuple(list(itertools.combinations(transaction, size)))
        for comb in nCr:
            if comb in chk:
                chk[comb] += 1
    l = []
    num_transactions = len(transactions)
    for key, value in chk.items():
        count[key] = value
        if value / num_transactions >= minSupport:
            l.append(key)
    L.append(l)


def get_count(item):  # item : tuple
    if item in count:
        return count[item]
    cnt = 0
    for transaction in transactions:
        nCi = list(itertools.combinations(transaction, len(item)))
        for comb in nCi:
            if comb == item:
                cnt += 1
                break
    count[item] = cnt
    return cnt


def get_subsets(item):
    subsets = []
    n = len(item)
    for i in range(1, n):
        subsets += list(itertools.combinations(item, i))
    return subsets


def get_associate_rules():
    num_transactions = len(transactions)
    for frequent_set in every_L:
        if len(frequent_set) < 2:
            continue
        subsets = get_subsets(frequent_set)
        pick_two = list(itertools.combinations(subsets, 2))
        for pair in pick_two:
            chk = tuple(set(pair[0] + pair[1]))
            if len(chk) != len(pair[0] + pair[1]):
                continue
            a = pair[0]
            b = pair[1]
            a_cnt = get_count(a)
            b_cnt = get_count(b)
            ab = tuple(sorted(a + b))
            ab_cnt = get_count(ab)
            rules.append(tuple([a, b, float(ab_cnt / num_transactions), float(ab_cnt / a_cnt)]))
            rules.append(tuple([b, a, float(ab_cnt / num_transactions), float(ab_cnt / b_cnt)]))


def main():
    get_input()
    get_first_l()   # get frequent 1-item set before loop
    k = 1
    while True:
        if len(L[k]) == 0:
            break
        first_pruned_c = get_c(k+1)
        get_l_from_c(first_pruned_c, k+1)
        k += 1
    for i in L:
        if len(i) != 0:
            for j in i:
                every_L.append(j)

    get_associate_rules()
    global rules
    rules = list(set(rules))  # 중복 제거

    output()


if __name__ == '__main__':
    main()
