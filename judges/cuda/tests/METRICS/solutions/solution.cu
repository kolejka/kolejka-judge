#include <iostream>
#include <stdexcept>

__device__ bool is_prime(uint64_t number) {
    if ( number < 2 )
        return false;
    if ( number == 2 )
        return true;
    if ( number % 2 == 0 )
        return false;
    for ( uint64_t i = 3 ; i*i <= number ; i+=2 ) {
        if ( number % i == 0 )
            return false;
    }
    return true;
}

__global__ void run(unsigned num_cases, uint64_t* values, char* results) {
    unsigned idx = blockIdx.x * blockDim.x + threadIdx.x;
    if ( idx < num_cases )
        results[idx] = is_prime(values[idx]) ? 1 : 0;
}

void check_cuda(cudaError_t err) {
    if (err != cudaSuccess) 
        throw std::runtime_error(cudaGetErrorString(err));
}

int main() {
    unsigned num_cases;
    std::cin >> num_cases;
    
    uint64_t* values = reinterpret_cast<uint64_t*>(malloc(num_cases*sizeof(uint64_t)));
    uint64_t* d_values;
    check_cuda(cudaMalloc(&d_values, num_cases*sizeof(uint64_t)));
    char* results = reinterpret_cast<char*>(malloc(num_cases));
    char* d_results;
    check_cuda(cudaMalloc(&d_results, num_cases*sizeof(char)));

    for ( unsigned c = 0 ; c < num_cases ; c++ )
        std::cin >> values[c];

    check_cuda(cudaMemcpy(d_values, values, num_cases*sizeof(uint64_t), cudaMemcpyHostToDevice));
    run<<<(num_cases+255)/256, 256>>>(num_cases, d_values, d_results);
    check_cuda(cudaMemcpy(results, d_results, num_cases*sizeof(char), cudaMemcpyDeviceToHost));

    for ( unsigned c = 0 ; c < num_cases ; c++ ) {
        if ( results[c] == 1 )
            std::cout << "yes" << std::endl;
        else
            std::cout << "no " << std::endl;
    }

    free(values);
    check_cuda(cudaFree(d_values));
    free(results);
    check_cuda(cudaFree(d_results));

    return 0;
}
