// Straight-forward brute force solution
// Complexity: O(q * n^2)

#include <bits/stdc++.h>


using namespace std;


long long answerQuery(int n, const vector <vector<int>> &owner, const vector <vector<int>> &value, long long a, long long b, long long c) {
    map <int,int> totalValue;
    map <int,int> totalBorder;

    int dx[] = {1, 0, -1, 0};
    int dy[] = {0, 1, 0, -1};

    for (int x = 0; x < n; x++) for (int y = 0; y < n; y++) {
        totalValue[owner[x][y]] += value[x][y];

        for (int d = 0; d < 4; d++) {
            int nx = x + dx[d], ny = y + dy[d];

            if (nx >= 0 && nx < n && ny >= 0 && ny < n && owner[x][y] != owner[nx][ny]) {
                totalBorder[owner[x][y]]++;
            }
        }
    }

    bool any = false;
    long long maxPower;

    for (auto &e : totalValue) {
        int civId, civValue;
        tie(civId, civValue) = e;

        int civBorder = totalBorder[civId];

        long long power = a * civValue + b * civBorder + c * civValue * civBorder;

        if (!any || power > maxPower) {
            maxPower = power;
            any = true;
        }
    }

    return maxPower;
}

void solve() {
    int n;
    cin >> n;

    vector <vector<int>> value(n, vector <int> (n));
    vector <vector<int>> owner(n, vector <int> (n));

    for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) {
        cin >> value[i][j];
    }

    for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) {
        cin >> owner[i][j];
    }

    int q;
    cin >> q;

    for (int i = 0; i < q; i++) {
        int x, y, newOwner;
        long long a, b, c;

        cin >> x >> y >> newOwner >> a >> b >> c;
        x--; y--;

        owner[x][y] = newOwner;

        cout << answerQuery(n, owner, value, a, b, c) << " \n"[i == q - 1];
    }
};

int main() {
    ios_base::sync_with_stdio(false);

    int t;
    cin >> t;

    while (t--) {
        solve();
    }

    return 0;
}
