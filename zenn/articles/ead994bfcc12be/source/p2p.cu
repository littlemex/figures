// p2p.cu: GPU どうしの直接アクセスの可否を表にし、GPU 0 から GPU 1 のメモリへの直接アクセスを有効にして保持する
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <cuda_runtime.h>

__global__ void touch(int *peer, size_t n) {
    size_t i = blockIdx.x * (size_t)blockDim.x + threadIdx.x;
    if (i < n) peer[i] = (int)i;
}

int main(int argc, char **argv) {
    int n; cudaGetDeviceCount(&n);
    printf("cudaDeviceCanAccessPeer (row = from, col = to)\n    ");
    for (int j = 0; j < n; j++) printf(" GPU%d", j);
    printf("\n");
    for (int i = 0; i < n; i++) {
        printf("GPU%d", i);
        for (int j = 0; j < n; j++) {
            int ok = 0;
            if (i != j) cudaDeviceCanAccessPeer(&ok, i, j);
            printf("    %s", i == j ? "-" : (ok ? "1" : "0"));
        }
        printf("\n");
    }
    size_t mib = argc > 1 ? atol(argv[1]) : 1024;
    int hold = argc > 2 ? atoi(argv[2]) : 0;
    int ok = 0; cudaDeviceCanAccessPeer(&ok, 0, 1);
    if (!ok) { printf("GPU0 -> GPU1: no peer access\n"); return 0; }
    int *buf1; cudaSetDevice(1); cudaMalloc(&buf1, mib << 20);
    printf("allocated %zu MiB on GPU1; sleeping %d s before enabling peer access\n", mib, hold);
    fflush(stdout); sleep(hold);
    cudaSetDevice(0);
    cudaError_t e = cudaDeviceEnablePeerAccess(1, 0);
    printf("cudaDeviceEnablePeerAccess(0 -> 1): %s\n", cudaGetErrorString(e));
    size_t cnt = (mib << 20) / sizeof(int);
    touch<<<(cnt + 255) / 256, 256>>>(buf1, cnt);
    e = cudaDeviceSynchronize();
    printf("GPU0 wrote %zu MiB into GPU1 memory: %s\n", mib, cudaGetErrorString(e));
    fflush(stdout); sleep(hold);
    return 0;
}
