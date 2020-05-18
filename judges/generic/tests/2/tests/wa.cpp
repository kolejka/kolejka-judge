// Heuristic that tries to only consider a subset of all active civilisations

#include <bits/stdc++.h>


using namespace std;


struct query {
    int i, j, newOwner;
    long long a, b, c;
};

int dx[] = {1, 0, -1, 0};
int dy[] = {0, 1, 0, -1};

struct Testcase {
    int n;

    vector <vector<int>> value, owner;
    map <int,int> totalValue, totalFields, totalBorders;

    set <pair<int,int>> byValue, byBorders, byProduct;

    Testcase(int n): n(n), value(n, vector <int> (n)), owner(n, vector <int> (n, -1)) {
        for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) {
            cin >> value[i][j];
        }

        for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) {
            int own;
            cin >> own;

            makeOwner(i, j, own);
        }

        for (auto &e : totalValue) {
            addToGroups(e.first);
        }
    }

    int isValid(int x, int y) {
        return x >= 0 && x < n && y >= 0 && y < n;
    }

    void changeBorders(int p, int value) {
        if (p == -1) return ;
        totalBorders[p] += value;
    }

    void changeValueAndFields(int p, int value, int fields) {
        if (p == -1) return ;

        totalValue[p] += value;
        totalFields[p] += fields;
    }

    void makeOwner(int x, int y, int p) {
        for (int d = 0; d < 4; d++) {
            int nx = x + dx[d], ny = y + dy[d];

            if (isValid(nx, ny)) {
                if (owner[x][y] != owner[nx][ny]) {
                    changeBorders(owner[x][y], -1);
                    changeBorders(owner[nx][ny], -1);
                }

                if (p != owner[nx][ny]) {
                    changeBorders(p, 1);
                    changeBorders(owner[nx][ny], 1);
                }
            }
        }

        changeValueAndFields(owner[x][y], -value[x][y], -1);
        changeValueAndFields(p, value[x][y], 1);

        owner[x][y] = p;
    }

    void addToGroups(int p) {
        if (p == -1) return ;

        byValue.insert({totalValue[p], p});
        byBorders.insert({totalBorders[p], p});
        byProduct.insert({totalValue[p] * totalBorders[p], p});
    }

    void removeFromGroups(int p) {
        if (p == -1) return ;

        byValue.erase({totalValue[p], p});
        byBorders.erase({totalBorders[p], p});
        byProduct.erase({totalValue[p] * totalBorders[p], p});
    }

    long long answerQuery(long long a, long long b, long long c) {
        long long maxPower = -LLONG_MAX;

        auto consider = [&](int p) {
            int hereValue = totalValue[p];
            int hereBorder = totalBorders[p];

            maxPower = max(maxPower, a * hereValue + b * hereBorder + c * hereValue * hereBorder);
        };

        auto updateAnswer = [&](set <pair<int,int>> &s, bool reversed) {
            auto it = reversed ? s.begin() : prev(s.end());
            auto last = reversed ? prev(s.end()) : s.begin();
        
            int toCheck = 100;

            while (toCheck--) {
                consider(it->second);

                if (it == last) break;
                it = reversed ? next(it) : prev(it);
            }
        };

        updateAnswer(byValue, a < 0);
        updateAnswer(byBorders, b < 0);
        updateAnswer(byProduct, c < 0);

        return maxPower;
    }

    void solveQueries(int q) {
        for (int i = 0; i < q; i++) {
            int x, y, newOwner;
            long long a, b, c;

            cin >> x >> y >> newOwner >> a >> b >> c;
            x--; y--;

            // Handle the case when a new civilisation appears.
            if (!totalValue.count(newOwner)) {
                totalValue[newOwner] = totalFields[newOwner] = totalBorders[newOwner] = 0;
                addToGroups(newOwner);
            }

            set <int> impacted = {owner[x][y], newOwner};

            for (int d = 0; d < 4; d++) {
                int nx = x + dx[d], ny = y + dy[d];

                if (isValid(nx, ny)) {
                    impacted.insert(owner[nx][ny]);
                }
            }

            for (int p : impacted) {
                removeFromGroups(p);
            }

            makeOwner(x, y, newOwner);

            for (int p : impacted) {
                // Handle the case when a civilisation disappears.
                if (p == -1 || totalFields[p] == 0) {
                    totalValue.erase(p);
                    totalFields.erase(p);
                    totalBorders.erase(p);

                    continue;
                }

                addToGroups(p);
            }

            cout << answerQuery(a, b, c) << " \n"[i == q - 1];
        }
    }
};

int main() {
    ios_base::sync_with_stdio(false);

    int t;
    cin >> t;

    while (t--) {
        int n;
        cin >> n;

        Testcase test(n);

        int q;
        cin >> q;

        test.solveQueries(q);
    }

    return 0;
}
