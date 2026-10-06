#include <algorithm>
#include <chrono>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

vector<int> readRanks(const string& fileName) {
    ifstream input(fileName);
    if (!input) {
        throw runtime_error("Could not open " + fileName);
    }

    vector<int> ranks;
    int rank;
    while (input >> rank) {
        ranks.push_back(rank);
    }
    return ranks;
}

long long mergeSortCount(vector<int>& values, vector<int>& buffer,
                         int left, int right) {
    if (left >= right) {
        return 0;
    }

    int middle = left + (right - left) / 2;
    long long count = mergeSortCount(values, buffer, left, middle);
    count += mergeSortCount(values, buffer, middle + 1, right);

    int i = left;
    int j = middle + 1;
    int place = left;

    while (i <= middle && j <= right) {
        if (values[i] <= values[j]) {
            buffer[place++] = values[i++];
        } else {
            buffer[place++] = values[j++];
            count += middle - i + 1;
        }
    }

    while (i <= middle) {
        buffer[place++] = values[i++];
    }
    while (j <= right) {
        buffer[place++] = values[j++];
    }

    for (int k = left; k <= right; ++k) {
        values[k] = buffer[k];
    }

    return count;
}

long long mergeSortInversions(vector<int> values) {
    if (values.empty()) {
        return 0;
    }

    vector<int> buffer(values.size());
    return mergeSortCount(values, buffer, 0, static_cast<int>(values.size()) - 1);
}

int medianOfThree(int first, int middle, int last) {
    if (first > middle) {
        swap(first, middle);
    }
    if (middle > last) {
        swap(middle, last);
    }
    if (first > middle) {
        swap(first, middle);
    }
    return middle;
}

long long quickSortCount(vector<int>& values) {
    if (values.size() < 2) {
        return 0;
    }

    int pivot = medianOfThree(values.front(), values[values.size() / 2],
                              values.back());
    vector<int> smaller;
    vector<int> equal;
    vector<int> bigger;
    smaller.reserve(values.size());
    equal.reserve(values.size());
    bigger.reserve(values.size());

    long long biggerBefore = 0;
    long long equalBefore = 0;
    long long crossCount = 0;

    // Keep each partition in its old order so the cross pairs are countable.
    for (int value : values) {
        if (value < pivot) {
            crossCount += biggerBefore + equalBefore;
            smaller.push_back(value);
        } else if (value == pivot) {
            crossCount += biggerBefore;
            ++equalBefore;
            equal.push_back(value);
        } else {
            ++biggerBefore;
            bigger.push_back(value);
        }
    }

    long long count = crossCount;
    count += quickSortCount(smaller);
    count += quickSortCount(bigger);

    values.clear();
    values.insert(values.end(), smaller.begin(), smaller.end());
    values.insert(values.end(), equal.begin(), equal.end());
    values.insert(values.end(), bigger.begin(), bigger.end());
    return count;
}

long long quickSortInversions(vector<int> values) {
    return quickSortCount(values);
}

long long insertionSortInversions(vector<int> values) {
    long long count = 0;

    for (int i = 1; i < static_cast<int>(values.size()); ++i) {
        int current = values[i];
        int j = i - 1;

        while (j >= 0 && values[j] > current) {
            values[j + 1] = values[j];
            --j;
            ++count;
        }
        values[j + 1] = current;
    }

    return count;
}

vector<int> combinedOrder(const vector<vector<int>>& sources) {
    vector<long long> totals(sources[0].size(), 0);
    for (const vector<int>& source : sources) {
        for (int page = 0; page < static_cast<int>(source.size()); ++page) {
            totals[page] += source[page];
        }
    }

    vector<int> order(totals.size());
    iota(order.begin(), order.end(), 0);
    sort(order.begin(), order.end(), [&totals](int left, int right) {
        if (totals[left] != totals[right]) {
            return totals[left] < totals[right];
        }
        return left < right;
    });
    return order;
}

double milliseconds(chrono::steady_clock::time_point start,
                    chrono::steady_clock::time_point finish) {
    return chrono::duration<double, milli>(finish - start).count();
}

int main(int argc, char* argv[]) {
    string folder = "sources";
    if (argc == 2) {
        folder = argv[1];
    } else if (argc > 2) {
        cerr << "Usage: " << argv[0] << " [source-folder]\n";
        return 1;
    }

    try {
        vector<vector<int>> sources;
        for (int i = 1; i <= 5; ++i) {
            sources.push_back(readRanks(folder + "/source" + to_string(i) + ".txt"));
        }

        const size_t pageCount = sources[0].size();
        for (const vector<int>& source : sources) {
            if (source.size() != pageCount) {
                throw runtime_error("The source files do not contain the same number of pages");
            }
        }

        vector<int> order = combinedOrder(sources);
        vector<long long> inversionCounts(5);

        cout << "Search ranking reliability\n";
        cout << "Pages: " << pageCount << "\n";
        cout << "Lower combined rank totals are placed first.\n\n";

        for (int sourceNumber = 0; sourceNumber < 5; ++sourceNumber) {
            vector<int> inCombinedOrder;
            inCombinedOrder.reserve(pageCount);
            for (int page : order) {
                inCombinedOrder.push_back(sources[sourceNumber][page]);
            }

            auto start = chrono::steady_clock::now();
            long long mergeCount = mergeSortInversions(inCombinedOrder);
            auto finish = chrono::steady_clock::now();
            double mergeTime = milliseconds(start, finish);

            start = chrono::steady_clock::now();
            long long quickCount = quickSortInversions(inCombinedOrder);
            finish = chrono::steady_clock::now();
            double quickTime = milliseconds(start, finish);

            start = chrono::steady_clock::now();
            long long insertionCount = insertionSortInversions(inCombinedOrder);
            finish = chrono::steady_clock::now();
            double insertionTime = milliseconds(start, finish);

            if (mergeCount != quickCount || mergeCount != insertionCount) {
                throw runtime_error("The sorting algorithms produced different inversion counts");
            }

            inversionCounts[sourceNumber] = mergeCount;
            cout << "Source " << sourceNumber + 1 << ": " << mergeCount << " inversions\n";
            cout << fixed << setprecision(2);
            cout << "  merge sort:     " << mergeTime << " ms\n";
            cout << "  quicksort:      " << quickTime << " ms\n";
            cout << "  insertion sort: " << insertionTime << " ms\n\n";
        }

        int bestSource = 0;
        for (int i = 1; i < 5; ++i) {
            if (inversionCounts[i] < inversionCounts[bestSource]) {
                bestSource = i;
            }
        }

        cout << "Most reliable source: Source " << bestSource + 1 << "\n";
        cout << "It has the fewest inversions against the combined ranking.\n";
    } catch (const exception& error) {
        cerr << error.what() << '\n';
        return 1;
    }

    return 0;
}
