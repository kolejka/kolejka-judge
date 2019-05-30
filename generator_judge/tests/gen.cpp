#include <cstdio>
#include <cstdlib>

int main() {
  int Z;
  scanf("%d", &Z);
  printf("%d\n", Z);
  while (Z--) {
    int k, n, m, freedom;
    scanf("%d%d%d%d", &k, &n, &m, &freedom);
    srand(k + n + m + freedom);
    printf("%d %d %d\n", k, n, m);
    for (int i = 0; i < m; ++i)
      printf("%d\n", 1 + (i + rand() % freedom) % n);
  }
}
