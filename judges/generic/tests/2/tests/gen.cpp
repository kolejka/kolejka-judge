#include <bits/stdc++.h>


using namespace std;

const int MAXN = 500;
const int MAXQ = 100 * 1000;

const long long MAXA = 1e10;
const long long MAXB = 1e12;
const long long MAXC = 1e4;

const int MAXVAL = 100;

const int MAXP = 1000 * 1000 * 1000;


long long randLong(long long l, long long r) {
    static mt19937_64 twister(0xdead);

    uniform_int_distribution <unsigned long long> uniformRand(l, r);
    return uniformRand(twister);
}

struct Event {
    int x, y, newOwner;
    long long a, b, c;
};

struct Test {
    int n, q;
    vector <vector<int>> initValue, initOwner;
    vector <Event> events;
};

struct Categorical {
    int c;
    long long sumDistribution;

    vector <int> distribution;

    Categorical(const vector <int> &distribution): c(distribution.size()), distribution(distribution) {
        sumDistribution = 0;
        for (int x : distribution) sumDistribution += x;
    }

    int sample() const {
        int x = randLong(0, sumDistribution - 1);

        for (int i = 0; i < c; i++) {
            if (x < distribution[i]) {
                return i;
            }

            x -= distribution[i];
        }

        assert(false);
    }
};

Categorical getUniformDistribution(int c) {
    return Categorical(vector <int> (c, 1));
}

Categorical getSkewedDistribution(int c) {
    vector <int> dist(c);
    iota(dist.begin(), dist.end(), 1);

    return Categorical(dist);
}

vector <vector<int>> genRandomValues(int n, int low, int high) {
    vector <vector<int>> value(n, vector <int> (n));

    for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) {
        value[i][j] = randLong(low, high);
    }

    return value;
}

vector <vector<int>> genRandomOwners(int n, const Categorical &distribution) {
    vector <vector<int>> owner(n, vector <int> (n));

    for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) {
        owner[i][j] = distribution.sample();
    }

    return owner;
}

tuple <int,int,int> genRandomUpdate(int n, const vector <vector<int>> &owner, const Categorical &distribution) {
    int x, y, newOwner;
    do {
        x = randLong(0, n - 1);
        y = randLong(0, n - 1);
        newOwner = distribution.sample();
    } while (owner[x][y] == newOwner);

    return tuple <int,int,int> {x, y, newOwner};
}

Test genRandom(int n, int q, const Categorical &distribution, int valueRange, long long aRange, long long bRange, long long cRange) {
    auto owner = genRandomOwners(n, distribution);

    Test t = {
        n, q, genRandomValues(n, -valueRange, valueRange), owner
    };

    while (t.events.size() < q) {
        int x, y, newOwner;
        tie(x, y, newOwner) = genRandomUpdate(n, owner, distribution);

        owner[x][y] = newOwner;

        long long a = randLong(-aRange, aRange);
        long long b = randLong(-bRange, bRange);
        long long c = randLong(-cRange, cRange);

        t.events.push_back({x, y, newOwner, a, b, c});
    }

    return t;
}

Test genRandomUniform(int n, int q, int c, int valueRange, long long aRange, long long bRange, long long cRange) {
    return genRandom(n, q, getUniformDistribution(c), valueRange, aRange, bRange, cRange);
}

Test genRandomSkewed(int n, int q, int c, int valueRange, long long aRange, long long bRange, long long cRange) {
    return genRandom(n, q, getSkewedDistribution(c), valueRange, aRange, bRange, cRange);
}

Test genSnek(int n, int q, long long aRange, long long bRange, long long cRange) {
    // TODO
}

void randomizeAndPrint(Test &t) {
    vector <int> owners;

    for (int i = 0; i < t.n; i++) for (int j = 0; j < t.n; j++) {
        owners.push_back(t.initOwner[i][j]);
    }

    for (auto &e : t.events) {
        owners.push_back(e.newOwner);
    }

    sort(owners.begin(), owners.end());
    owners.resize(unique(owners.begin(), owners.end()) - owners.begin());

    set <int> usedIds;
    map <int,int> ownersMap;

    for (int x : owners) {
        int id;
        do {
            id = randLong(0, MAXP);
        } while (usedIds.count(id));

        ownersMap[x] = id;
        usedIds.insert(id);
    }

    cout << t.n << '\n';

    for (int i = 0; i < t.n; i++) for (int j = 0; j < t.n; j++) {
        cout << t.initValue[i][j] << " \n"[j == t.n - 1];
    }

    for (int i = 0; i < t.n; i++) for (int j = 0; j < t.n; j++) {
        cout << ownersMap[t.initOwner[i][j]] << " \n"[j == t.n - 1];
    }

    cout << t.q << '\n';

    for (auto &e : t.events) {
        cout << e.x + 1 << ' ' << e.y + 1 << ' ' << ownersMap[e.newOwner] << ' ';
        cout << e.a << ' ' << e.b << ' ' << e.c << '\n';
    }
}

int main() {
    ios_base::sync_with_stdio(false);

    string test;
    cin >> test;

    vector <Test> tests;

    if (test == "small") {
        for (int n = 2; n <= 27; n++) {
            int q = randLong(n * n / 4, n * n / 2);

            for (int valueRange : {1, 10, MAXVAL}) {
                for (long long aRange : {10LL, MAXA}) {
                    for (long long bRange : {10LL, MAXB}) {
                        for (long long cRange : {3LL, MAXC}) {
                            for (int c : {n, n * n / 2}) {
                                tests.push_back(genRandomUniform(n, q, c, valueRange, aRange, bRange, cRange));
                            }

                            tests.push_back(genRandomSkewed(n, q, 2 * n, valueRange, aRange, bRange, cRange));
                        }
                    }
                }
            }
        }
    } else if (test == "large-uniform") {
        tests.push_back(genRandomUniform(MAXN, MAXQ, 2 * MAXN, MAXVAL, MAXA, MAXB, MAXC));
        tests.push_back(genRandomUniform(MAXN, MAXQ, MAXN * MAXN / 6, MAXVAL, MAXA, MAXB, MAXC));
    } else if (test == "large-skewed") {
        tests.push_back(genRandomSkewed(MAXN, MAXQ, 2 * MAXN, MAXVAL, MAXA, MAXB, MAXC));
        tests.push_back(genRandomSkewed(MAXN, MAXQ, 3 * MAXN, MAXVAL, MAXA, MAXB, MAXC));
    } else if (test == "large-snek") {
        assert(false);
        // TODO
        //
        // Add a test where civs are arranged in a snake (first row left to right, second row right to left, etc), with
        // each subsequent civ having slightly larger border length, so that there are O(n) different lengths.
    } else {
        assert(false);
    }

    random_shuffle(tests.begin(), tests.end());

    cout << tests.size() << '\n';

    for (auto &t : tests) {
        randomizeAndPrint(t);
    }

    return 0;
}