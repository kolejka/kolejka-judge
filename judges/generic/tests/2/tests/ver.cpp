#include "ver.h"
#include <bits/stdc++.h>


using namespace std;


const int MINZ = 1;
const int MAXZ = 2000;

const int MINN = 2;
const int MAXN = 500;
const int MAXAREASUM = 500 * 1000;

const int MINQ = 1;
const int MAXQ = 100 * 1000;
const int MAXQSUM = 200 * 1000;

const int MINP = 0;
const int MAXP = 1000 * 1000 * 1000;

const int MAXABSVAL = 100;
const long long MAXABSA =   10LL * 1000LL * 1000LL * 1000LL;
const long long MAXABSB = 1000LL * 1000LL * 1000LL * 1000LL;
const long long MAXABSC =   10LL * 1000LL;


int main() {
    oi::Scanner in(stdin);

    int z = in.readInt(MINZ, MAXZ); in.readEoln();

    int nMin = MAXN;
    int nMax = MINN;
    int areaSum = 0;

    int qMin = MAXQ;
    int qMax = MINQ;
    int qSum = 0;

    long long aMin = MAXABSA;
    long long aMax = -MAXABSA;

    long long bMin = MAXABSB;
    long long bMax = -MAXABSB;

    long long cMin = MAXABSC;
    long long cMax = -MAXABSC;

    for (int t = 0; t < z; t++) {
        int n = in.readInt(MINN, MAXN); in.readEoln();

        nMin = min(nMin, n);
        nMax = max(nMax, n);

        areaSum += n * n;

        if (areaSum > MAXAREASUM) {
            in.error("Total number of fields is too large");
        }

        for (int x = 0; x < n; x++) for (int y = 0; y < n; y++) {
            in.readInt(-MAXABSVAL, MAXABSVAL);

            if (y < n - 1) {
                in.readSpace();
            } else {
                in.readEoln();
            }
        }

        vector <vector<int>> owner(n, vector <int> (n));

        for (int x = 0; x < n; x++) for (int y = 0; y < n; y++) {
            owner[x][y] = in.readInt(MINP, MAXP);

            if (y < n - 1) {
                in.readSpace();
            } else {
                in.readEoln();
            }
        }

        int q = in.readInt(MINQ, MAXQ); in.readEoln();

        qMin = min(qMin, q);
        qMax = max(qMax, q);
        qSum += q;

        if (qSum > MAXQSUM) {
            in.error("Sum of q too large");
        }

        while (q--) {
            int x = in.readInt(1, n); in.readSpace();
            int y = in.readInt(1, n); in.readSpace();
            int newOwner = in.readInt(MINP, MAXP); in.readSpace();

            x--; y--;

            if (owner[x][y] == newOwner) {
                in.error("Civilisation takes over a field it already owns");
            }

            owner[x][y] = newOwner;

            long long a = in.readLL(-MAXABSA, MAXABSA); in.readSpace();
            long long b = in.readLL(-MAXABSB, MAXABSB); in.readSpace();
            long long c = in.readLL(-MAXABSC, MAXABSC); in.readEoln();

            aMin = min(aMin, a);
            aMax = max(aMax, a);

            bMin = min(bMin, b);
            bMax = max(bMax, b);

            cMin = min(cMin, c);
            cMax = max(cMax, c);
        }
    }

    in.readEof();

    printf("OK, z = %d\n", z);

    printf("n min = %d, n max = %d, n^2 sum = %d\n", nMin, nMax, areaSum);
    printf("q min = %d, q max = %d, q sum = %d\n", qMin, qMax, qSum);

    printf("a min = %lld, a max = %lld\n", aMin, aMax);
    printf("b min = %lld, b max = %lld\n", bMin, bMax);
    printf("c min = %lld, c max = %lld\n", cMin, cMax);
}
