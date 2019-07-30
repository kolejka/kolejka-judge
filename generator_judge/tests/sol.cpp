#include <iostream>
#include <set>
#include <vector>
using namespace std;

int main() {
  ios_base::sync_with_stdio(false);
  int Z;
  cin >> Z;
  while (Z--) {
    int k, n, m;
    cin >> k >> n >> m;
    vector<int> memory(m);
    for (int i = 0; i < m; ++i)
      cin >> memory[i];
    vector<int> last(n + 1, m), next(m);
    for (int i = m - 1; i >= 0; --i) {
      next[i] = last[memory[i]];
      last[memory[i]] = i;
    }
    int count = 0;
    multiset<int> cache;
    for (int i = 0; i < m; ++i) {
      if (cache.count(i)) {
        cache.erase(i);
      } else {
        ++count;
        if (cache.size() == k) {
          set<int>::iterator it = cache.end();
          --it;
          cache.erase(it);
        }
      }
      cache.insert(next[i]);
    }
    cout << count << endl;
  }
}
