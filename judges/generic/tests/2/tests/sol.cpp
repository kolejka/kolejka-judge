// Model solution
// Complexity: O(n^2 + q * n)

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

    map <int, multiset<int>> groups;

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
        groups[totalBorders[p]].insert(totalValue[p]);
    }

    void removeFromGroups(int p) {
        if (p == -1) return ;

        int y = totalBorders[p];
        groups[y].erase(groups[y].find(totalValue[p]));

        if (groups[y].empty()) {
            groups.erase(y);
        }
    }

    long long answerQuery(long long a, long long b, long long c) {
        long long bestValue = -LLONG_MAX;

        for (auto &e : groups) {
            int hereBorder = e.first;
            long long coef = a + c * hereBorder;

            int hereValue;
            if (coef >= 0) {
                hereValue = *e.second.rbegin();
            } else {
                hereValue = *e.second.begin();
            }

            bestValue = max(bestValue, coef * hereValue + b * hereBorder);
        }

        return bestValue;
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
